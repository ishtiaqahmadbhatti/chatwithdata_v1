
from fastmcp import FastMCP
from app.main import app
mcp = FastMCP.from_fastapi(app=app, name="ChatWithData MCP Server")
if __name__ == "__main__":
    mcp.run()

