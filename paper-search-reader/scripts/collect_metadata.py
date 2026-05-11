#!/usr/bin/env python3
"""Collect and merge metadata from Zotero, DOI, Semantic Scholar, OpenAlex, arXiv, Hugging Face, and publisher pages."""

from __future__ import annotations

import json
import logging
import urllib.request
import urllib.parse

from .common import base_parser, emit, enrich_metadata, maybe_load_json_record, paper_id_for_record, resolve_reference

logger = logging.getLogger(__name__)

HF_API_BASE = "https://huggingface.co/api"


def fetch_hf_paper_metadata(arxiv_id: str) -> dict | None:
    """从 HF Papers API 获取论文元数据（含关联资源）。"""
    url = f"{HF_API_BASE}/papers/{arxiv_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.info("HF metadata not available for %s: %s", arxiv_id, e)
    return None


def fetch_hf_linked_resources(arxiv_id: str) -> dict:
    """从 HF API 获取论文关联的 models/datasets/spaces。"""
    resources = {"models": [], "datasets": [], "spaces": []}

    for resource_type in ("models", "datasets", "spaces"):
        url = f"{HF_API_BASE}/{resource_type}?filter=arxiv:{arxiv_id}&limit=10"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    for item in data:
                        entry = {
                            "id": item.get("id", ""),
                            "url": f"https://huggingface.co/{resource_type}/{item.get('id', '')}",
                        }
                        if resource_type == "models":
                            entry["pipeline_tag"] = item.get("pipeline_tag", "")
                        resources[resource_type].append(entry)
        except Exception:
            pass  # Non-fatal: linked resources are optional enhancement

    return resources


def main() -> None:
    parser = base_parser(__doc__ or "collect metadata")
    args = parser.parse_args()

    if not args.input:
        raise SystemExit("collect_metadata.py requires --input.")

    input_record = maybe_load_json_record(args.input)
    if input_record is not None:
        record = dict(input_record)
    else:
        record = resolve_reference(args.input)

    metadata = enrich_metadata(record)

    # HF 元数据增强：如果有 arXiv ID，尝试获取 HF 关联资源
    arxiv_id = metadata.get("arxiv_id") or metadata.get("arxivId")
    if arxiv_id:
        hf_meta = fetch_hf_paper_metadata(arxiv_id)
        if hf_meta:
            metadata["hf_metadata"] = {
                "github_repo": hf_meta.get("githubRepo"),
                "project_page": hf_meta.get("projectPage"),
                "upvotes": hf_meta.get("upvotes", 0),
            }
            # Remove None values
            metadata["hf_metadata"] = {k: v for k, v in metadata["hf_metadata"].items() if v is not None}

        hf_resources = fetch_hf_linked_resources(arxiv_id)
        has_resources = any(len(v) > 0 for v in hf_resources.values())
        if has_resources:
            metadata["hf_linked_resources"] = hf_resources

    metadata["paper_id"] = args.paper_id or metadata.get("paper_id") or paper_id_for_record(metadata)
    metadata["status"] = "ok"
    metadata["script"] = "collect_metadata.py"
    emit(metadata, args.output)


if __name__ == "__main__":
    main()
