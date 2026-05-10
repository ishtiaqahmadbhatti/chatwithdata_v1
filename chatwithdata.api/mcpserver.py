
from fastmcp import FastMCP
from app.main import app
mcp = FastMCP.from_fastapi(app=app,name="Smart Converter MCP Server")
if __name__ == "__main__":
    mcp.run()

