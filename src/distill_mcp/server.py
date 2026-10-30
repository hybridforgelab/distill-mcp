"""Distill MCP server: web pages to clean Markdown, honouring robots.txt and AI opt-outs."""
from __future__ import annotations

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from .client import PRODUCTS, call

PRODUCT = PRODUCTS["distill"]
REFUSED = {"robots_txt", "opted_out", "blocked"}

server = MCPServer(
    "distill",
    title="Distill: web page to Markdown",
    instructions=(
        "Fetch a web page and get its main content as clean Markdown, without navigation, ads or scripts. "
        "Distill honours robots.txt and AI opt-outs: when a result says the site refused, don't try to get the "
        "page another way. Each call is one request on the user's Distill plan."
    ),
    website_url="https://distill.hybridforgelab.com",
)

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=True)


def _shape(result: dict) -> dict:
    if result.get("status") in REFUSED:
        result["note"] = ("The site refused this fetch (robots.txt, a noai directive or bot protection). "
                          "Respect it: don't fetch the page another way.")
    return result


@server.tool(annotations=READ_ONLY)
async def fetch_markdown(
    url: Annotated[str, Field(description="Page to fetch (http or https).")],
    max_chars: Annotated[int, Field(ge=100, le=2_000_000, description="Cut the Markdown to this many characters.")]
    = 20_000,
    include_links: Annotated[bool, Field(description="Keep links and return the list of links.")] = True,
    include_images: Annotated[bool, Field(description="Keep images as ![alt](src).")] = False,
    include_tables: Annotated[bool, Field(description="Keep tables as Markdown tables.")] = True,
) -> dict:
    """Fetch a web page and return its main content as Markdown, with title, author, date and language.

    `status` is "ok" on success. Other values (robots_txt, opted_out, blocked, not_html, http_error,
    unreachable) explain why there is no content."""
    return _shape(await call(PRODUCT, "POST", "/v1/markdown", json={
        "url": url, "max_chars": max_chars, "include_links": include_links,
        "include_images": include_images, "include_tables": include_tables}))


@server.tool(annotations=READ_ONLY)
async def html_to_markdown(
    html: Annotated[str, Field(description="Raw HTML you already have (up to 5 MB). Nothing is fetched.")],
    base_url: Annotated[str | None, Field(description="Page URL, to resolve relative links and images.")] = None,
    max_chars: Annotated[int, Field(ge=100, le=2_000_000, description="Cut the Markdown to this many characters.")]
    = 20_000,
    include_links: Annotated[bool, Field(description="Keep links and return the list of links.")] = True,
    include_images: Annotated[bool, Field(description="Keep images as ![alt](src).")] = False,
    include_tables: Annotated[bool, Field(description="Keep tables as Markdown tables.")] = True,
) -> dict:
    """Turn HTML you already have into clean Markdown (main content only). A `noai` directive in the HTML is
    honoured: the result then has no content."""
    if not html.strip():
        raise ToolError("html is empty.")
    body = {"html": html, "max_chars": max_chars, "include_links": include_links,
            "include_images": include_images, "include_tables": include_tables}
    if base_url:
        body["base_url"] = base_url
    return _shape(await call(PRODUCT, "POST", "/v1/markdown", json=body))


def main() -> None:  # pragma: no cover - stdio entry point
    server.run("stdio")

if __name__ == "__main__":  # pragma: no cover
    main()
