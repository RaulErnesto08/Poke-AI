from fastapi import FastAPI, Request
from starlette.routing import Mount
from mcp.server.sse import SseServerTransport
from server import mcp
import uvicorn

app = FastAPI(
    title="PokeAPI MCP Server",
    description="MCP server exposing tools for Pokémon backend.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup SSE transport for MCP
sse = SseServerTransport("/messages/")

app.router.routes.append(
    Mount("/messages", app=sse.handle_post_message)
)

@app.get("/sse", tags=["MCP"])
async def sse_entrypoint(request: Request):
    # Connect to the SSE transport
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        init_options = mcp._mcp_server.create_initialization_options()

        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            init_options,
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)