
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from distill_mcp import server as distill

SPEC_V1 = "openapi: 3.0.3\ninfo: {title: t, version: '1'}\npaths: {}\n"
SPEC_V2 = "openapi: 3.0.3\ninfo: {title: t, version: '2'}\npaths: {}\n"


async def test_server_lists_its_tools():
    listed = await distill.server.list_tools()
    assert {t.name for t in listed} == {"fetch_markdown", "html_to_markdown"}
    for t in listed:
        assert t.description and t.annotations.read_only_hint is True and t.annotations.open_world_hint is True


async def test_tool_call_through_the_server(api):
    api.queue(200, {"status": "ok", "markdown": "# Hi"})
    r = await distill.server.call_tool("fetch_markdown", {"url": "https://example.com/"})
    assert not r.is_error and "# Hi" in r.content[0].text
    with pytest.raises(ToolError, match="html is empty"):
        await distill.server.call_tool("html_to_markdown", {"html": "  "})


async def test_fetch_markdown_body(api):
    api.queue(200, {"status": "ok"})
    await distill.fetch_markdown("https://example.com/", max_chars=500)
    assert api.last.url.path == "/v1/markdown" and api.last.method == "POST"
    assert api.last_json() == {"url": "https://example.com/", "max_chars": 500, "include_links": True,
                               "include_images": False, "include_tables": True}


async def test_refusals_carry_a_note(api):
    api.queue(200, {"status": "robots_txt", "detail": "robots.txt disallows this path for GPTBot"})
    r = await distill.fetch_markdown("https://example.com/")
    assert "Respect it" in r["note"]
    api.queue(200, {"status": "ok"})
    assert "note" not in await distill.fetch_markdown("https://example.com/")


async def test_html_to_markdown_body(api):
    api.queue(200, {"status": "ok"})
    await distill.html_to_markdown("<p>x</p>", base_url="https://e.x/", include_images=True)
    assert api.last_json()["base_url"] == "https://e.x/" and api.last_json()["include_images"] is True
    await distill.html_to_markdown("<p>x</p>")
    assert "base_url" not in api.last_json()
    with pytest.raises(ToolError):
        await distill.html_to_markdown("")
