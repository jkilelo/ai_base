#!/usr/bin/env python3
"""
generate_tests.py — End-to-end test case generation pipeline.

Analyzes a repo with code_analyzer, sends the report + prompt to Gemini,
and writes structured test cases (JSON) to disk.

Usage:
    python generate_tests.py /path/to/repo
    python generate_tests.py /path/to/repo --output test_cases.json
    python generate_tests.py /path/to/repo --model flash --thinking medium
    python generate_tests.py --report existing_report.json  # skip analysis, reuse report
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    print("Error: GEMINI_API_KEY not found.", file=sys.stderr)
    sys.exit(1)


def run_analysis(repo_path: str, report_path: str) -> dict:
    from code_analyzer import analyze_repo
    print(f"[1/3] Analyzing {repo_path}...", file=sys.stderr)
    return analyze_repo(repo_path, output_path=report_path, parallel=False)


def build_prompt(report: dict, prompt_template_path: str) -> str:
    template = Path(prompt_template_path).read_text(encoding="utf-8")
    trimmed = trim_report(report)
    report_json = json.dumps(trimmed, indent=1, default=str)
    return f"{template}\n\n---\n\n# Analysis Report\n\n```json\n{report_json}\n```"


def _trim_func(func: dict) -> None:
    """Trim a single function dict in-place for token efficiency."""
    cc = func.get("complexity", {}).get("cyclomatic", 0)

    source = func.get("source", "")
    lines = source.splitlines()
    if cc <= 1 and len(lines) > 5:
        func["source"] = "\n".join(lines[:3]) + f"\n    # ... ({len(lines)} lines)"
    elif cc <= 3 and len(lines) > 15:
        func["source"] = "\n".join(lines[:10]) + f"\n    # ... ({len(lines)} lines)"

    edges = func.get("edge_cases", [])
    if edges:
        seen: set[str] = set()
        kept: list[dict] = []
        for e in edges:
            key = f"{e.get('category')}:{e.get('parameter')}"
            if key not in seen:
                seen.add(key)
                kept.append(e)
            if len(kept) >= 6:
                break
        func["edge_cases"] = kept

    doc = func.get("docstring", {})
    if isinstance(doc, dict) and doc.get("summary"):
        doc.pop("raw", None)

    calls = func.get("data_flow", {}).get("calls_made", [])
    if calls:
        func["data_flow"]["calls_made"] = list(dict.fromkeys(calls))


def trim_report(report: dict) -> dict:
    """Reduce token usage by trimming verbose/redundant fields."""
    import copy
    r = copy.deepcopy(report)

    r.get("repository", {}).pop("project_structure", None)

    for mod in r.get("modules", []):
        if not mod.get("functions") and not mod.get("classes") and not mod.get("module_variables"):
            mod.clear()
            mod["_skipped"] = True
            continue

        for func in mod.get("functions", []):
            _trim_func(func)

        for cls in mod.get("classes", []):
            cls.pop("source", None)
            for group, funcs in cls.get("methods", {}).items():
                for func in funcs:
                    _trim_func(func)

    r["modules"] = [m for m in r["modules"] if "_skipped" not in m]
    return r


def call_gemini(prompt: str, model: str, thinking: str | None, api_key: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai not installed. Run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-pro-preview" if model == "pro" else "gemini-3-flash-preview"

    config_kwargs: dict = {}
    if thinking:
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=thinking)

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    print(f"[2/3] Sending to Gemini ({model_id}, {len(prompt):,} chars)...", file=sys.stderr)
    start = time.time()

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config,
        )
    except Exception as e:
        print(f"\nError: Gemini API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start
    print(f"       Response received in {elapsed:.1f}s", file=sys.stderr)

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        um = response.usage_metadata
        pt = getattr(um, "prompt_token_count", "?")
        rt = getattr(um, "candidates_token_count", "?")
        print(f"       Tokens — prompt: {pt}, response: {rt}", file=sys.stderr)

    return response.text or ""


def extract_test_cases(response_text: str) -> list[dict]:
    """Extract JSON array of test cases from LLM response.

    Handles:
      1) Raw JSON array (response starts with '[')
      2) JSON inside ```json ... ``` fences
      3) JSON inside ``` ... ``` fences
    """
    text = response_text.strip()

    # Try raw JSON first
    if text.startswith("["):
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Try fenced ```json ... ``` block
    m = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if m:
        try:
            result = json.loads(m.group(1))
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Last resort: find the outermost [ ... ] in the response
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end > start:
        try:
            result = json.loads(text[start:end + 1])
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    return []


def validate_test_cases(cases: list[dict]) -> tuple[list[dict], list[str]]:
    """Validate test case structure. Returns (valid_cases, warnings)."""
    required_fields = {"name", "description", "steps", "expected_results"}
    valid = []
    warnings = []

    for i, tc in enumerate(cases):
        if not isinstance(tc, dict):
            warnings.append(f"  Item {i}: not a dict, skipped")
            continue

        missing = required_fields - set(tc.keys())
        if missing:
            warnings.append(f"  Item {i} ({tc.get('name', '?')}): missing {missing}, skipped")
            continue

        if not tc["name"] or not tc["description"]:
            warnings.append(f"  Item {i}: empty name or description, skipped")
            continue

        # Normalize steps to list
        if isinstance(tc["steps"], str):
            tc["steps"] = [s.strip() for s in tc["steps"].split("\n") if s.strip()]

        if not isinstance(tc["steps"], list) or not tc["steps"]:
            warnings.append(f"  Item {i} ({tc['name']}): empty or invalid steps, skipped")
            continue

        if not isinstance(tc["expected_results"], str) or not tc["expected_results"].strip():
            warnings.append(f"  Item {i} ({tc['name']}): empty expected_results, skipped")
            continue

        valid.append(tc)

    return valid, warnings


def main():
    parser = argparse.ArgumentParser(description="Generate structured test cases from repo analysis via Gemini.")
    parser.add_argument("repo_path", nargs="?", help="Path to the repository to analyze")
    parser.add_argument("--report", help="Use an existing report.json instead of re-analyzing")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file (default: <repo>/test_cases.json)")
    parser.add_argument("--model", "-m", choices=["pro", "flash"], default="pro", help="Gemini model (default: pro)")
    parser.add_argument("--thinking", "-t", choices=["high", "medium", "low"], default=None, help="Thinking level")
    parser.add_argument("--prompt-template", default=None, help="Custom prompt template .md file")
    parser.add_argument("--save-prompt", default=None, help="Save assembled prompt to file (for debugging)")
    parser.add_argument("--save-response", default=None, help="Save raw LLM response to file")

    args = parser.parse_args()

    if not args.repo_path and not args.report:
        parser.error("Provide repo_path or --report")

    api_key = load_api_key()

    # Step 1: Analysis
    if args.report:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        try:
            repo_root = Path(report["repository"]["root_path"])
        except KeyError:
            if not args.output:
                parser.error("Report missing 'repository.root_path'. Use --output to specify output path.")
            repo_root = Path(".")
    else:
        repo_root = Path(args.repo_path).resolve()
        report_path = str(Path(__file__).parent / "report.json")
        report = run_analysis(str(repo_root), report_path)

    # Step 2: Build prompt and call LLM
    template_path = args.prompt_template or str(Path(__file__).parent / "test_generation_prompt.md")
    prompt = build_prompt(report, template_path)

    if args.save_prompt:
        Path(args.save_prompt).write_text(prompt, encoding="utf-8")
        print(f"       Saved prompt to {args.save_prompt}", file=sys.stderr)

    response_text = call_gemini(prompt, args.model, args.thinking, api_key)

    if args.save_response:
        Path(args.save_response).write_text(response_text, encoding="utf-8")
        print(f"       Saved response to {args.save_response}", file=sys.stderr)

    # Step 3: Extract, validate, and write test cases
    print("[3/3] Extracting test cases...", file=sys.stderr)

    cases = extract_test_cases(response_text)
    if not cases:
        print("\nError: Could not extract test cases from response.", file=sys.stderr)
        fallback = Path(args.output or "raw_response.txt")
        fallback.write_text(response_text, encoding="utf-8")
        print(f"  Raw response saved to {fallback}", file=sys.stderr)
        sys.exit(1)

    valid, warnings = validate_test_cases(cases)

    if warnings:
        print(f"  Warnings ({len(warnings)}):", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)

    # Write output
    output_path = Path(args.output) if args.output else repo_root / "test_cases.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(valid, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nDone! {len(valid)} test cases written to {output_path}", file=sys.stderr)
    if len(valid) != len(cases):
        print(f"  Skipped (invalid): {len(cases) - len(valid)}", file=sys.stderr)


if __name__ == "__main__":
    main()
