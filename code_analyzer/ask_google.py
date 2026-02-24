#!/usr/bin/env python3
"""
ask_google.py — Generic Gemini 3 Pro query tool with Google Search grounding.

Usage:
  python ask_google.py "Your question here"
  python ask_google.py --file context.md "Follow-up question"
  python ask_google.py --model flash "Quick question"
  python ask_google.py --thinking high "Complex analysis"
  python ask_google.py --no-search "Answer from training data only"
  python ask_google.py --output response.md "Your question"
  python ask_google.py --system "You are an expert in X" "Your question"
  echo "piped input" | python ask_google.py
"""

import argparse
import os
import sys
import time

def main():
    parser = argparse.ArgumentParser(
        description="Ask Gemini 3 a question with optional Google Search grounding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="The question or prompt to send to Gemini.",
    )
    parser.add_argument(
        "--file", "-f",
        help="Read prompt/context from a file. Combined with positional prompt if both given.",
    )
    parser.add_argument(
        "--model", "-m",
        choices=["pro", "flash"],
        default="pro",
        help="Model to use: 'pro' (Gemini 3 Pro) or 'flash' (Gemini 3 Flash). Default: pro.",
    )
    parser.add_argument(
        "--thinking", "-t",
        choices=["high", "medium", "low", "minimal"],
        default=None,
        help="Thinking level. Pro supports high/low. Flash supports high/medium/low/minimal.",
    )
    parser.add_argument(
        "--no-search",
        action="store_true",
        help="Disable Google Search grounding (answer from training data only).",
    )
    parser.add_argument(
        "--system", "-s",
        default=None,
        help="System instruction to set context/persona.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Save response to this file instead of (in addition to) printing.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only print the response text, no status messages.",
    )

    args = parser.parse_args()

    # Build the prompt from all sources
    parts = []

    # File content
    if args.file:
        file_path = args.file
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            parts.append(f.read())

    # Positional prompt
    if args.prompt:
        parts.append(args.prompt)

    # Stdin (if piped)
    if not sys.stdin.isatty() and not args.prompt and not args.file:
        parts.append(sys.stdin.read())

    if not parts:
        parser.print_help()
        print("\nError: No prompt provided. Pass a prompt, --file, or pipe stdin.", file=sys.stderr)
        sys.exit(1)

    full_prompt = "\n\n".join(parts)

    # Load API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Try loading from .env
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment or .env file.", file=sys.stderr)
        sys.exit(1)

    # Import google genai
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed. Run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    # Configure client
    client = genai.Client(api_key=api_key)

    # Select model
    model_id = "gemini-3-pro-preview" if args.model == "pro" else "gemini-3-flash-preview"

    # Build config
    config_kwargs = {}

    # Thinking level (must be wrapped in ThinkingConfig)
    if args.thinking:
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=args.thinking)

    # System instruction
    if args.system:
        config_kwargs["system_instruction"] = args.system

    # Google Search grounding
    if not args.no_search:
        config_kwargs["tools"] = [
            types.Tool(google_search=types.GoogleSearch()),
        ]

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    # Send request
    if not args.quiet:
        search_status = "ON" if not args.no_search else "OFF"
        thinking = args.thinking or ("high" if args.model == "pro" else "high")
        print(f"[Gemini 3 {args.model.title()}] Thinking: {thinking} | Search: {search_status}", file=sys.stderr)
        print(f"[Prompt length: {len(full_prompt):,} chars]", file=sys.stderr)
        print("[Waiting for response...]", file=sys.stderr)

    start = time.time()

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=full_prompt,
            config=config,
        )
    except Exception as e:
        print(f"\nError from Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start

    # Extract text
    response_text = response.text if response.text else "(No text in response)"

    # Print response (force UTF-8 on Windows to handle emoji)
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print(response_text)

    # Print metadata
    if not args.quiet:
        print(f"\n---", file=sys.stderr)
        print(f"[Response received in {elapsed:.1f}s]", file=sys.stderr)
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            prompt_tokens = getattr(um, "prompt_token_count", "?")
            response_tokens = getattr(um, "candidates_token_count", "?")
            total = getattr(um, "total_token_count", "?")
            print(f"[Tokens — prompt: {prompt_tokens}, response: {response_tokens}, total: {total}]", file=sys.stderr)

    # Check for grounding metadata
    if not args.quiet and hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        grounding = getattr(candidate, "grounding_metadata", None)
        if grounding:
            chunks = getattr(grounding, "grounding_chunks", None)
            if chunks:
                print(f"[Grounded with {len(chunks)} search result(s)]", file=sys.stderr)

    # Save to file
    if args.output:
        output_path = args.output
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response_text)
        if not args.quiet:
            print(f"[Saved to {output_path}]", file=sys.stderr)


if __name__ == "__main__":
    main()