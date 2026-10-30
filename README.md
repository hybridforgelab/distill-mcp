# Distill MCP server

Give your AI agent clean Markdown from any web page: the main content only, without navigation, ads or scripts. Distill honours robots.txt and AI opt-outs.

The server is open source (MIT). It calls the [Distill API](https://distill.hybridforgelab.com), which is paid, with a free plan.

- You use **your own key, from RapidAPI or api.market**.
- Every tool call is one request on your plan.
- The free Basic plan has 15 requests a month, with a hard limit, so it never runs up a bill.

## 1. Get a key

| marketplace | |
|---|---|
| RapidAPI | [plans](https://rapidapi.com/hybrid-forge-lab-hybrid-forge-lab-default/api/distill-html-to-markdown-api/pricing) |
| api.market | [store](https://api.market/store/hybrid-forge-lab/distill) |

## 2. Add the server to your MCP client

The server runs locally over stdio with [uv](https://docs.astral.sh/uv/). Put your key in its environment.

**JSON configuration** (Claude Desktop, Cursor, VS Code and most clients):

```json
{
  "mcpServers": {
    "distill": {
      "command": "uvx",
      "args": ["--from", "hybridforgelab-distill-mcp", "distill-mcp"],
      "env": { "RAPIDAPI_KEY": "your-rapidapi-key" }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add distill --env RAPIDAPI_KEY=your-rapidapi-key -- uvx --from hybridforgelab-distill-mcp distill-mcp
```

### Environment

| variable | meaning |
|---|---|
| `RAPIDAPI_KEY` | your RapidAPI key |
| `API_MARKET_KEY` | your api.market key, used when `RAPIDAPI_KEY` is not set |
| `HFL_MARKETPLACE` | `rapidapi` or `apimarket`, when both keys are set |

Without a key the server still starts. The first tool call then explains where to get one.

## 3. Tools

| tool | what it does |
|---|---|
| `fetch_markdown(url, max_chars=20000, include_links=True, include_images=False, include_tables=True)` | fetches the page and returns its main content as Markdown, with the title, author, date and language |
| `html_to_markdown(html, base_url=None, …)` | the same, for HTML you already have; nothing is fetched |

When a site refuses (robots.txt, a `noai` directive, bot protection), `status` says so and a `note` asks the agent to respect it. Don't fetch the page another way: the [terms](https://distill.hybridforgelab.com/terms.html) forbid it.

`status` is `ok` on success. Other values (`robots_txt`, `opted_out`, `blocked`, `not_html`, `http_error`, `unreachable`) explain why there is no content.

Every tool returns the API's JSON response.

- When the marketplace reports it, `quota_remaining` is added: the requests left on your plan this month.
- Errors are explained in plain words, with what to do next:
  - key refused, with the link to subscribe;
  - quota reached, with the plans;
  - input the API couldn't process, with the API's reason.

## Privacy

- Local files are read only when a tool is given their path. They are sent to the API for that one request.
- The API processes inputs in memory and doesn't store them. See the [privacy policy](https://distill.hybridforgelab.com/privacy.html).
- Your key is only sent to the marketplace you chose.

## Limits

- `html` up to 5 MB.
- Only HTML pages; PDFs and other files are refused (use Unfold for documents).
- The server needs Python 3.10+ (uv installs it for you).

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest            # unit tests, no network; 100% coverage required
.venv/bin/ruff check src tests scripts
```

`scripts/e2e_stdio.py distill` runs the server over stdio, as a client would, and calls its tools against the real API. It needs `RAPIDAPI_KEY` or `API_MARKET_KEY`.

## Licence

MIT. Distill itself is a paid API with a free plan, run by [Hybrid Forge Lab](https://hybridforgelab.com).
