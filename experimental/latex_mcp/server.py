from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from schemas import JsonRpcRequest, JsonRpcResponse, CompileRequest
from compiler import compile_tikz

app = FastAPI(title="Latex Compile MCP (Isolated)")

# Enable CORS for local static test page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8088", "http://127.0.0.1:8088"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post("/mcp")
async def mcp_endpoint(payload: dict):
    try:
        req = JsonRpcRequest(**payload)
    except ValidationError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    if req.method != "tools/call":
        return JsonRpcResponse(id=req.id, result={"error": "Unsupported method"})

    name = (req.params or {}).get("name")
    args = (req.params or {}).get("arguments", {})

    if name != "latex_compile":
        return JsonRpcResponse(id=req.id, result={"error": f"Unknown tool: {name}"})

    try:
        compile_req = CompileRequest(**args)
        result = compile_tikz(compile_req)
        return JsonRpcResponse(id=req.id, result=result.model_dump())
    except ValidationError as e:
        return JsonRpcResponse(id=req.id, result={"error": str(e)})


@app.get("/health")
async def health():
    return {"status": "ok", "tools": ["latex_compile"]}
