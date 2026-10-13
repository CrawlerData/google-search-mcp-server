#!/usr/bin/env python3
"""Check the CrawlerData MCP server from a script: initialize, list tools, call one tool.

Useful to confirm your API key works before debugging a client config.

    python mcp_check.py                                    # calls google_autocomplete (1 credit)
    python mcp_check.py --list                             # list tools only (free)
    python mcp_check.py --tool google_search --args '{"query": "best crm software", "country": "gb"}'

Needs: requests. Set CRAWLERDATA_API_KEY first.
"""
import argparse
import json
import os
import sys

import requests

URL = "https://api.crawlerdata.com/mcp"


def main():
    ap = argparse.ArgumentParser(description="Talk to the CrawlerData MCP server over Streamable HTTP.")
    ap.add_argument("--tool", default="google_autocomplete", help="tool to call (default: google_autocomplete)")
    ap.add_argument("--args", default='{"query": "running sho"}', help="tool arguments as JSON")
    ap.add_argument("--list", action="store_true", help="only initialize and list tools (no credits used)")
    args = ap.parse_args()

    key = os.environ.get("CRAWLERDATA_API_KEY")
    if not key:
        sys.exit("Set CRAWLERDATA_API_KEY (get a key at https://app.crawlerdata.com/register)")
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json, text/event-stream"}

    def rpc(id_, method, params):
        body = {"jsonrpc": "2.0", "id": id_, "method": method, "params": params}
        resp = requests.post(URL, headers=headers, json=body, timeout=200)
        if resp.status_code == 401:
            sys.exit("401 Unauthorized: check CRAWLERDATA_API_KEY")
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            sys.exit(f"{method} failed: {data['error']}")
        return data["result"]

    info = rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "mcp-check", "version": "1.0"}})
    print("server:", info["serverInfo"])

    tools = rpc(2, "tools/list", {})["tools"]
    print(f"{len(tools)} tools:")
    for t in tools:
        print(f"  {t['name']:24} {(t.get('description') or '').splitlines()[0][:90]}")
    if args.list:
        return

    call = rpc(3, "tools/call", {"name": args.tool, "arguments": json.loads(args.args)})
    text = call["content"][0]["text"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(text[:1000])
        return
    print(f"\n{args.tool} -> credits: {data.get('credits')}")
    print(json.dumps(strip_images(data.get("result", data)), indent=2, ensure_ascii=False)[:1500])


def strip_images(obj):
    """Shorten base64 data: URIs (thumbnails) so the output stays readable."""
    if isinstance(obj, dict):
        return {k: strip_images(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_images(v) for v in obj]
    if isinstance(obj, str) and obj.startswith("data:"):
        return obj[:30] + "..."
    return obj


if __name__ == "__main__":
    main()
