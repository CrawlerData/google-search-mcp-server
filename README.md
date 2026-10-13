# Google Search & Google Shopping MCP Server for Claude, Cursor and n8n

Give Claude Code, Claude Desktop, Cursor, n8n or any MCP client live Google data. The CrawlerData **remote MCP server** at `https://api.crawlerdata.com/mcp` exposes eight tools — Google Search, Google Shopping search, all sellers of a product, product details, Google Images, Google News, Google Local and Autocomplete — so your assistant can look things up on Google while it works. This repo has copy-paste configs for each client and a small Python script to check your connection.

> **Uses the CrawlerData API — you need an API key** (free trial credits available at https://app.crawlerdata.com/register). Tool calls cost the same credits as the REST API: 1 credit per call (Google Shopping sellers: 1 credit per 10 sellers returned).

This is a **hosted** server run by CrawlerData. There is nothing to install or self-host: you point your client at the URL and send your API key as a Bearer token.

## Connection details

| | |
| --- | --- |
| URL | `https://api.crawlerdata.com/mcp` |
| Transport | Streamable HTTP (stateless; no SSE endpoint, no session ID) |
| Auth | Header `Authorization: Bearer YOUR_API_KEY` (no OAuth) |
| Registry | Listed in the official MCP Registry as `com.crawlerdata/google-shopping-serp` |

## Tools

| Tool | Arguments (required in bold) | Returns | Credits |
| --- | --- | --- | --- |
| `google_search` | **query**, country, language, device, page | Organic results, ads, AI Overview, People Also Ask, local pack, top stories, related searches | 1 |
| `google_shopping_search` | **query**, country, language, page | Products with price, merchant, rating, `product_id` | 1 |
| `google_shopping_sellers` | **product_id**, country, language | Every seller's price, shipping, total, availability | 1 per 10 sellers |
| `google_shopping_product` | **product_id**, country, language | Title, description, specs, images, rating | 1 |
| `google_images` | **query**, country, language, page | Image URL, thumbnail, title, source page, size | 1 |
| `google_news` | **query**, country, language, page | Headline, source, date, snippet, link | 1 |
| `google_local` | **query**, country, language, page | Businesses with rating, reviews, address, phone, hours, website | 1 |
| `google_autocomplete` | **query**, country, language | Google search suggestions | 1 |

`country` is one of 31 codes (us, gb, ca, au, de, fr, nl, it, es, pt, be, at, ch, se, no, dk, fi, ie, pl, cz, il, ae, in, jp, kr, sg, mx, br, nz, za, tr). `initialize` and `tools/list` are free.

## Claude Code

```bash
claude mcp add --transport http crawlerdata https://api.crawlerdata.com/mcp \
  --header "Authorization: Bearer YOUR_API_KEY"

# Check it connected
claude mcp list
```

Add `--scope user` to make it available in every project. [`configs/claude-code.sh`](configs/claude-code.sh)

### Shared with a team: `.mcp.json`

Commit this at your project root without the key; Claude Code expands `${CRAWLERDATA_API_KEY}` from each person's environment and asks each person to approve the server the first time. [`configs/.mcp.json`](configs/.mcp.json)

```json
{
  "mcpServers": {
    "crawlerdata": {
      "type": "http",
      "url": "https://api.crawlerdata.com/mcp",
      "headers": {
        "Authorization": "Bearer ${CRAWLERDATA_API_KEY}"
      }
    }
  }
}
```

## Claude Desktop and claude.ai (custom connector)

Open **Connectors** (under Customize, or Settings in older versions) → **Add** → **Add custom connector**, and enter `https://api.crawlerdata.com/mcp`. Choose **No sign in** for authentication and under **Request headers** add `Authorization` with the value `Bearer YOUR_API_KEY`. Custom connectors are available on Free (one connector), Pro, Max, Team and Enterprise plans; on Team and Enterprise an owner adds them in the organization settings.

### Claude Desktop with `claude_desktop_config.json`

Claude Desktop starts local (stdio) servers from its config file, so use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge (needs Node.js 18+). Open Settings → Developer → Edit Config, add this, and restart Claude Desktop. [`configs/claude_desktop_config.json`](configs/claude_desktop_config.json)

```json
{
  "mcpServers": {
    "crawlerdata": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@0.14.3",
        "https://api.crawlerdata.com/mcp",
        "--header",
        "Authorization:${AUTH_HEADER}"
      ],
      "env": {
        "AUTH_HEADER": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

There is no space after `Authorization:` on purpose: Claude Desktop on Windows and Cursor don't escape spaces in `args`, so the value with the space goes in `env`. This form works on macOS too.

## Cursor

Put this in `.cursor/mcp.json` in your project (or `~/.cursor/mcp.json` for all projects). Cursor reads `${env:CRAWLERDATA_API_KEY}` from your environment. [`configs/cursor-mcp.json`](configs/cursor-mcp.json)

```json
{
  "mcpServers": {
    "crawlerdata": {
      "url": "https://api.crawlerdata.com/mcp",
      "headers": {
        "Authorization": "Bearer ${env:CRAWLERDATA_API_KEY}"
      }
    }
  }
}
```

## n8n

**As tools for an AI Agent:** add an **MCP Client Tool** node to your AI Agent and set:

- Endpoint: `https://api.crawlerdata.com/mcp`
- Server Transport: **HTTP Streamable**
- Authentication: **Header Auth**, with a credential whose Name is `Authorization` and Value is `Bearer YOUR_API_KEY`
- Tools to include: all, or pick the ones you need

(These are the standard n8n MCP Client Tool settings; we haven't clicked through every n8n version, so labels may differ slightly in yours.)

**In a regular workflow (no agent):** call the REST API with an **HTTP Request** node: `POST https://api.crawlerdata.com/v1/jobs`, header `Authorization: Bearer YOUR_API_KEY`, JSON body `{"endpoint": "google-search", "params": {"query": "..."}, "queue": "live"}`, and a timeout of about 200 seconds. Step-by-step settings and an importable price-tracking workflow are on the [n8n integration page](https://crawlerdata.com/integrations/n8n).

## Other MCP clients

Any client that supports remote servers over Streamable HTTP with a custom header works with the URL and header above. Clients that only support stdio can use the `mcp-remote` bridge as in the Claude Desktop config.

## Check your key and the server: `mcp_check.py`

A dependency-light script (just `requests`) that initializes, lists the tools and calls one. Run it before debugging a client config.

```bash
git clone https://github.com/CrawlerData/google-search-mcp-server.git
cd google-search-mcp-server
pip install -r requirements.txt
export CRAWLERDATA_API_KEY="your_api_key"        # PowerShell: $env:CRAWLERDATA_API_KEY="your_api_key"

python mcp_check.py --list                                          # free
python mcp_check.py                                                 # google_autocomplete, 1 credit
python mcp_check.py --tool google_news --args '{"query": "anthropic", "country": "gb"}'
```

Real output on 13 October 2026:

```text
$ python mcp_check.py
server: {'name': 'crawlerdata', 'version': '1.0.0'}
8 tools:
  google_shopping_search   Search Google Shopping. Returns products with title, price, merchant, rating and product_i
  google_shopping_sellers  Every seller's offer for a Google Shopping product_id: merchant, price, shipping, total, a
  google_shopping_product  Details for a Google Shopping product_id: title, description, specs, images, rating and re
  google_search            Google web search results (organic results, featured snippets, related questions and more)
  google_images            Google Images results: image URL, thumbnail, title, source page and size. 1 credit.
  google_news              Google News results: headline, source, date, snippet and link. 1 credit.
  google_local             Google local business results: name, rating, reviews, category, address, phone, hours and
  google_autocomplete      Google search suggestions for a partial query. 1 credit.

google_autocomplete -> credits: 1
{
  "search_parameters": {
    "engine": "google_autocomplete",
    "query": "running sho",
    "country": "us",
    "language": "en"
  },
  "suggestions": [
    { "value": "running shoes", "type": "QUERY" },
    { "value": "running shorts", "type": "QUERY" },
    { "value": "running shoes for women", "type": "QUERY" },
    ...
  ]
}
```

## Prompts to try

- "Find the Google Shopping product for the Sony WH-1000XM5 and list every seller with total price."
- "What does Google show for *best crm software* in the UK? Is there an AI Overview?"
- "Get the latest Google News results for *nvidia* and summarise the main stories."
- "List 10 highly rated plumbers in Austin, TX with phone numbers."
- "What does Google autocomplete suggest for *how to start a*?"

For Google Shopping, ask the assistant to search by **brand and model** (not a bare barcode/GTIN, which often matches unrelated products) and to ignore offers for accessories or other sizes. For web search, plain keywords work best; don't rely on advanced operators such as `site:`.

## Cost

Each tool call is one API request and costs the same as the REST API: 1 credit, except `google_shopping_sellers` at 1 credit per 10 sellers returned (rounded up, minimum 1). Failed calls are free. An assistant may call several tools to answer one question (for example a shopping search followed by a sellers call), so ask it to stop after one search if you want to keep a conversation to a single credit. Packs run from $1.00 down to $0.30 per 1,000 credits ([pricing](https://crawlerdata.com/pricing)). Each tool result includes the credits it used.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Server shows as failed, or `401` | The header must be exactly `Authorization: Bearer YOUR_API_KEY`. In the `mcp-remote` config keep `Authorization:${AUTH_HEADER}` with no space and put `Bearer YOUR_API_KEY` in `env`. Run `python mcp_check.py --list` to test the key. |
| Claude Desktop doesn't show the tools | Fully restart Claude Desktop after editing the config, and check that `node` and `npx` run in a terminal (Node 18+). |
| `402` / out of credits | Buy a credit pack in the [dashboard](https://app.crawlerdata.com). |
| `429` / rate limited | 100 requests per minute and 20 per second per key. Wait a moment and retry. |
| A sellers call times out | `google_shopping_sellers` loads the full product page and can take 30-120 seconds. Raise the client's tool timeout if it has one, or use `google_shopping_product` when you don't need every seller. |

## Links

- [CrawlerData](https://crawlerdata.com)
- [MCP server setup guide](https://crawlerdata.com/integrations/mcp)
- [Google Search API](https://crawlerdata.com/apis/google-search-api) and [Google Shopping API](https://crawlerdata.com/apis/google-shopping-api)
- [API docs](https://app.crawlerdata.com/docs)

## More CrawlerData examples

| Repo | What it does |
| --- | --- |
| [google-shopping-scraper](https://github.com/CrawlerData/google-shopping-scraper) | Search Google Shopping, export products to CSV/JSON (Python + Node.js) |
| [google-shopping-sellers-scraper](https://github.com/CrawlerData/google-shopping-sellers-scraper) | Every seller and price for one product, as a comparison table |
| [google-shopping-price-tracker](https://github.com/CrawlerData/google-shopping-price-tracker) | Scheduled price history in SQLite, CSV export and an HTML chart |
| [competitor-price-monitoring](https://github.com/CrawlerData/competitor-price-monitoring) | Your catalog vs Google Shopping sellers, with undercut alerts |
| [map-violation-monitor](https://github.com/CrawlerData/map-violation-monitor) | Flag sellers below MAP with timestamped evidence |
| [google-search-scraper](https://github.com/CrawlerData/google-search-scraper) | Google SERP to JSON/CSV: organic, ads, People Also Ask, AI Overview (Python + Node.js) |
| [google-rank-tracker](https://github.com/CrawlerData/google-rank-tracker) | Daily keyword positions by country and device, with a change report |
| [google-local-business-leads](https://github.com/CrawlerData/google-local-business-leads) | Google Local results to a lead list CSV |
| [google-news-scraper](https://github.com/CrawlerData/google-news-scraper) | Brand and keyword news monitoring to CSV and JSON Feed |
| [google-search-mcp-server](https://github.com/CrawlerData/google-search-mcp-server) | Connect Claude, Cursor or n8n to the CrawlerData MCP server |
| [crawlerdata-examples](https://github.com/CrawlerData/crawlerdata-examples) | Python, Node.js and curl snippets for every endpoint |

## License

MIT. See [LICENSE](LICENSE). Google and Google Shopping are trademarks of Google LLC; this project is not affiliated with Google.
