# Installing the CrawlerData MCP server in Cline (instructions for an AI agent)

CrawlerData is a **hosted** (remote) MCP server. There is nothing to clone, build or run locally: you only add a remote server entry to Cline's MCP settings.

## What you need from the user
A CrawlerData API key. If they do not have one, tell them to create it at https://app.crawlerdata.com/register (new accounts with a verified work email get 50 free credits). Ask them to paste the key. Never invent a key.

## Steps
1. Open Cline's MCP settings file `cline_mcp_settings.json` (Cline panel -> MCP Servers -> Configure -> Configure MCP Servers).
2. Add this entry under `mcpServers`, replacing `YOUR_API_KEY` with the user's key:

```json
{
  "mcpServers": {
    "crawlerdata": {
      "type": "streamableHttp",
      "url": "https://api.crawlerdata.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

   If the file already has other servers, keep them and only add the `crawlerdata` key.
3. Save the file. Cline connects automatically; the server should show as connected with 8 tools.
4. Check it works: ask the user for a search, for example "Search Google for `what is a serp api` and tell me whether Google shows an AI Overview and which sources it cites", and call the `google_search` tool.

## Tools (all read-only)
`google_search`, `google_news`, `google_images`, `google_local`, `google_autocomplete`, `google_shopping_search`, `google_shopping_sellers`, `google_shopping_product`.

## Notes
- Each tool call costs 1 credit (Google Shopping sellers: 1 credit per 10 sellers returned). Failed requests are not charged. `initialize` and `tools/list` are free.
- Transport is Streamable HTTP (no SSE endpoint). `"type": "streamableHttp"` must be set; without it Cline assumes the legacy SSE transport.
- Errors: HTTP 401 means the key is missing or wrong; 402 means the account is out of credits (top up at https://app.crawlerdata.com).
- Docs: https://crawlerdata.com/integrations/mcp
