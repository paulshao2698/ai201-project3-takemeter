#!/usr/bin/env python3
"""
Collect public r/iRacing Reddit posts/comments as candidate examples for TakeMeter.

This script does NOT finalize labels for you. It creates candidate rows that you
must manually review and label before training.

Output:
  data/iracing_reddit_candidates.csv

Recommended workflow:
  1. Run this script.
  2. Open the CSV in Excel/Google Sheets.
  3. Review each text row.
  4. Fill the `label` column with one of:
       racecraft_analysis
       practical_help
       emotional_reaction
  5. Save the reviewed file as takemeter_dataset.csv.
"""

from __future__ import annotations

import csv
import html
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import requests


SUBREDDIT = "iRacing"
OUTPUT_PATH = Path("data/iracing_reddit_candidates.csv")

# Search terms are chosen to create a mix of the three labels:
# racecraft_analysis, practical_help, emotional_reaction.
SEARCH_TERMS = [
    # racecraft / incident / fault analysis
    "fault incident racing line",
    "protest wrecked braking",
    "divebomb corner overlap",
    "unsafe rejoin racing",
    "who is at fault",
    "racecraft advice",
    # practical help
    "setup wheel pedals help",
    "what car should I buy",
    "what track should I buy",
    "license safety rating",
    "graphics settings fps",
    "force feedback settings",
    "new player advice",
    # emotional reaction / venting
    "rookies are terrible",
    "got punted again",
    "this game is impossible",
    "i hate safety rating",
    "finally got promoted",
    "best race ever",
]

VALID_LABELS = {"racecraft_analysis", "practical_help", "emotional_reaction"}

HEADERS = {
    "User-Agent": "TakeMeter classroom data collection script by u/paulshao2698"
}


@dataclass
class Candidate:
    reddit_id: str
    kind: str  # post or comment
    subreddit: str
    created_utc: str
    score: int
    permalink: str
    title: str
    text: str
    suggested_label: str
    label: str
    notes: str


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def suggest_label(text: str) -> str:
    """Very rough pre-label to speed review. You must verify manually."""
    t = text.lower()

    practical_terms = [
        "how do i", "how to", "what car", "what track", "should i buy",
        "settings", "setup", "wheel", "pedal", "license", "safety rating",
        "fps", "vr", "monitor", "download", "install", "error", "help",
        "new to", "beginner",
    ]
    racecraft_terms = [
        "fault", "incident", "racing line", "braking", "turn in", "turn-in",
        "apex", "overlap", "divebomb", "rejoin", "protest", "space",
        "corner", "defend", "inside", "outside", "avoidable contact",
    ]
    emotional_terms = [
        "hate", "impossible", "terrible", "ridiculous", "lmao", "lol",
        "finally", "best race", "worst", "got punted", "wrecked again",
        "so tired", "frustrated", "rant", "vent", "amazing", "stupid",
    ]

    scores = {
        "practical_help": sum(term in t for term in practical_terms),
        "racecraft_analysis": sum(term in t for term in racecraft_terms),
        "emotional_reaction": sum(term in t for term in emotional_terms),
    }

    best_label, best_score = max(scores.items(), key=lambda x: x[1])
    return best_label if best_score > 0 else ""


def reddit_get(url: str, params: dict | None = None) -> dict | list:
    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def search_posts(term: str, pages: int = 2, limit: int = 100) -> Iterable[dict]:
    after = None
    for _ in range(pages):
        params = {
            "q": term,
            "restrict_sr": "1",
            "sort": "relevance",
            "t": "year",
            "limit": str(limit),
        }
        if after:
            params["after"] = after

        url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json"
        data = reddit_get(url, params=params)
        listing = data.get("data", {})
        children = listing.get("children", [])

        for child in children:
            if child.get("kind") == "t3":
                yield child.get("data", {})

        after = listing.get("after")
        if not after:
            break

        time.sleep(1.5)


def fetch_top_comments(permalink: str, limit: int = 8) -> Iterable[dict]:
    url = f"https://www.reddit.com{permalink}.json"
    data = reddit_get(url, params={"limit": str(limit), "sort": "top"})
    if not isinstance(data, list) or len(data) < 2:
        return []

    comments_listing = data[1].get("data", {}).get("children", [])
    comments = []
    for child in comments_listing:
        if child.get("kind") != "t1":
            continue
        c = child.get("data", {})
        body = clean_text(c.get("body"))
        if len(body) < 40:
            continue
        comments.append(c)
    return comments


def is_usable_text(text: str) -> bool:
    if len(text) < 40:
        return False
    lowered = text.lower()
    bad_markers = ["[deleted]", "[removed]", "automoderator"]
    return not any(marker in lowered for marker in bad_markers)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    seen_texts: set[str] = set()
    seen_ids: set[str] = set()
    candidates: list[Candidate] = []

    for term in SEARCH_TERMS:
        print(f"Searching: {term}")
        try:
            posts = list(search_posts(term))
        except Exception as exc:
            print(f"  Search failed for {term!r}: {exc}")
            continue

        for post in posts:
            post_id = post.get("id", "")
            permalink = post.get("permalink", "")
            title = clean_text(post.get("title"))
            selftext = clean_text(post.get("selftext"))
            post_text = clean_text(f"{title}. {selftext}".strip())

            if post_id and post_id not in seen_ids and is_usable_text(post_text):
                seen_ids.add(post_id)
                seen_texts.add(post_text.lower())
                candidates.append(
                    Candidate(
                        reddit_id=post_id,
                        kind="post",
                        subreddit=SUBREDDIT,
                        created_utc=str(post.get("created_utc", "")),
                        score=int(post.get("score", 0) or 0),
                        permalink=f"https://www.reddit.com{permalink}",
                        title=title,
                        text=post_text,
                        suggested_label=suggest_label(post_text),
                        label="",
                        notes="",
                    )
                )

            # Add top comments because comments often contain better discourse examples.
            if permalink:
                try:
                    comments = fetch_top_comments(permalink)
                except Exception as exc:
                    print(f"  Comment fetch failed for {permalink}: {exc}")
                    comments = []

                for c in comments:
                    comment_id = c.get("id", "")
                    body = clean_text(c.get("body"))
                    body_key = body.lower()
                    if not comment_id or comment_id in seen_ids or body_key in seen_texts:
                        continue
                    if not is_usable_text(body):
                        continue

                    seen_ids.add(comment_id)
                    seen_texts.add(body_key)
                    candidates.append(
                        Candidate(
                            reddit_id=comment_id,
                            kind="comment",
                            subreddit=SUBREDDIT,
                            created_utc=str(c.get("created_utc", "")),
                            score=int(c.get("score", 0) or 0),
                            permalink=f"https://www.reddit.com{permalink}{comment_id}",
                            title=title,
                            text=body,
                            suggested_label=suggest_label(body),
                            label="",
                            notes="",
                        )
                    )

                time.sleep(1.5)

    # Sort to put stronger examples first, but keep all rows for review.
    candidates.sort(key=lambda x: x.score, reverse=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(candidates[0]).keys()) if candidates else [
            "reddit_id", "kind", "subreddit", "created_utc", "score",
            "permalink", "title", "text", "suggested_label", "label", "notes"
        ])
        writer.writeheader()
        for row in candidates:
            writer.writerow(asdict(row))

    print(f"\nSaved {len(candidates)} candidate rows to {OUTPUT_PATH}")
    print("Next: manually review labels and save final file as takemeter_dataset.csv")


if __name__ == "__main__":
    main()
