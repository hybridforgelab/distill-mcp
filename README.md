# hybridforgelab-distill-mcp: moved to bytestay-distill-mcp

This package has moved to **[bytestay-distill-mcp](https://pypi.org/project/bytestay-distill-mcp/)**. Hybrid Forge Lab is now ByteStay.

This last version only installs bytestay-distill-mcp and forwards to it. It prints a one-line notice on stderr and gets no more updates.

## Switch

Replace `hybridforgelab-distill-mcp` with `bytestay-distill-mcp` in your MCP client config:

```json
"command": "uvx",
"args": ["--from", "bytestay-distill-mcp", "distill-mcp"]
```

Or with Claude Code:

```bash
claude mcp add distill --env RAPIDAPI_KEY=your-rapidapi-key -- uvx --from bytestay-distill-mcp distill-mcp
```

The environment variables are the same, so your keys keep working.

## Links

- Package: [bytestay-distill-mcp](https://pypi.org/project/bytestay-distill-mcp/)
- Source: [Bytestay/distill-mcp](https://github.com/Bytestay/distill-mcp)
- Distill API: [distill.bytestay.pt](https://distill.bytestay.pt)
