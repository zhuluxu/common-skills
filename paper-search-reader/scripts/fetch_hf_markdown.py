#!/usr/bin/env python3
"""Fetch a Hugging Face paper page as markdown using Python urllib.

Uses urllib rather than curl for better TLS/network compatibility.
Falls back gracefully on 404 (paper not indexed) and network errors.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

from .common import base_parser, emit, maybe_load_json_record

logger = logging.getLogger(__name__)

HF_MD_URL = "https://huggingface.co/papers/{paper_id}.md"
HF_API_URL = "https://huggingface.co/api/papers/{paper_id}"


def fetch_hf_markdown(arxiv_id: str, timeout: int = 30) -> str | None:
    """Fetch the HF paper page as markdown.

    Returns:
        Markdown string on success, None on failure (404, network error, etc.)
    """
    url = HF_MD_URL.format(paper_id=arxiv_id)
    try:
        req = urllib.request.Request(url, headers={"Accept": "text/markdown"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.info("Paper %s not indexed on HF (404)", arxiv_id)
        else:
            logger.warning("HF markdown fetch HTTP error for %s: %s", arxiv_id, e)
    except Exception as e:
        logger.warning("HF markdown fetch failed for %s: %s", arxiv_id, e)
    return None


def fetch_hf_api_metadata(arxiv_id: str, timeout: int = 15) -> dict | None:
    """Fetch minimal metadata from HF Papers API as fallback."""
    url = HF_API_URL.format(paper_id=arxiv_id)
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.info("HF API metadata not available for %s: %s", arxiv_id, e)
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a Hugging Face paper page as markdown."
    )
    parser.add_argument("--arxiv-id", required=True, help="arXiv paper ID")
    parser.add_argument(
        "--output", default="", help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--save-dir",
        default="",
        help="Directory to save markdown file (auto-named as {arxiv_id}.md)",
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Request timeout in seconds"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    arxiv_id = args.arxiv_id.strip()
    logger.info("Fetching HF markdown for %s", arxiv_id)

    markdown = fetch_hf_markdown(arxiv_id, timeout=args.timeout)

    if markdown is None:
        # Try to get at least metadata for a partial result
        meta = fetch_hf_api_metadata(arxiv_id, timeout=args.timeout)
        result = {
            "status": "markdown_unavailable",
            "arxiv_id": arxiv_id,
            "source_type": "hf_markdown",
            "markdown_path": None,
        }
        if meta:
            result["title"] = meta.get("title", "")
            result["hf_metadata"] = True
            logger.info("Got HF API metadata but no markdown for %s", arxiv_id)
        else:
            result["hf_metadata"] = False
            logger.warning("No HF data available for %s", arxiv_id)
        emit(result, args.output)
        sys.exit(1)

    # Determine output path
    if args.save_dir:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        output_path = save_dir / f"{arxiv_id}.md"
    elif args.output:
        output_path = Path(args.output)
    else:
        output_path = None

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        logger.info("Saved markdown to %s (%d chars)", output_path, len(markdown))
    else:
        sys.stdout.write(markdown)
        sys.stdout.write("\n")

    result = {
        "status": "ok",
        "arxiv_id": arxiv_id,
        "source_type": "hf_markdown",
        "markdown_path": str(output_path) if output_path else "stdout",
        "markdown_length": len(markdown),
    }
    emit(result, args.output)


if __name__ == "__main__":
    main()
