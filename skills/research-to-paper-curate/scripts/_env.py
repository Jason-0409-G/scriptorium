#!/usr/bin/env python3
"""Tiny stdlib loader for API credentials from a .env-style file (no python-dotenv needed).

Why: the emails/keys for the curate APIs (CrossRef / NCBI / Semantic Scholar / OpenAlex) are
otherwise scattered across shell environment variables. This lets a user keep them all in ONE
file. Real environment variables always win — load_env never overrides an already-set value.

Search order (the first file that exists is loaded):
  1. $RESEARCH_TO_PAPER_ENV          (explicit path, if set)
  2. ./.env                          (current working dir, e.g. the manuscript workspace)
  3. ~/.config/research-to-paper/keys.env

File format: plain KEY=VALUE lines; blank lines and lines starting with # are ignored;
surrounding single/double quotes around the value are stripped.
"""
from __future__ import annotations
import os


def _candidates():
    return [
        os.environ.get("RESEARCH_TO_PAPER_ENV", ""),
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/.config/research-to-paper/keys.env"),
    ]


def _parse(path):
    pairs = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k:
                pairs[k] = v
    return pairs


def load_env(verbose=False):
    """Populate os.environ from the first credentials file found; never override existing vars.
    Returns the path that was loaded, or "" if none was found."""
    for path in _candidates():
        if path and os.path.isfile(path):
            try:
                for k, v in _parse(path).items():
                    os.environ.setdefault(k, v)
            except OSError:
                return ""
            if verbose:
                print(f"[env] loaded credentials from {path}")
            return path
    return ""


if __name__ == "__main__":
    p = load_env(verbose=True)
    if not p:
        checked = ", ".join(c for c in _candidates() if c)
        print(f"[env] no credentials file found (checked: {checked})")
