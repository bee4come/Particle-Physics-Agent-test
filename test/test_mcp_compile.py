#!/usr/bin/env python3
import subprocess
import sys
import time
import json
from pathlib import Path
import urllib.request


def wait_for_health(url: str, timeout: float = 10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def main():
    # Start MCP server
    env = dict(**dict(Path.cwd().env if hasattr(Path.cwd(), 'env') else {}), **dict())
    cmd = [sys.executable, "-m", "uvicorn", "experimental.latex_mcp.server:app", "--host", "127.0.0.1", "--port", "8003"]
    print("Starting MCP server:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    try:
        if not wait_for_health("http://127.0.0.1:8003/health", timeout=12):
            print("MCP server failed to start in time")
            # Show some logs
            try:
                out = proc.stdout.read(2000)
                print(out)
            except Exception:
                pass
            proc.terminate()
            proc.wait(timeout=5)
            sys.exit(1)

        print("MCP server is up")

        payload = {
            "jsonrpc": "2.0",
            "id": "feynman-1",
            "method": "tools/call",
            "params": {
                "name": "latex_compile",
                "arguments": {
                    "tikz": "\\begin{tikzpicture}\n\\begin{feynman}\n  \\diagram* { e1 [particle= $e^-$] -- [fermion] a -- [fermion] e2 [particle= $e^+$], a -- [photon, edge label=$\\gamma$] b, };\n\\end{feynman}\n\\end{tikzpicture}",
                    "engine": "lualatex",
                    "format": "svg",
                    "timeoutSec": 30
                }
            }
        }

        req = urllib.request.Request(
            "http://127.0.0.1:8003/mcp",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        result = data.get("result", {})
        print("status:", result.get("status"))
        print(json.dumps(result, indent=2))
        if result.get("status") != "ok":
            print("Compile failed")
            sys.exit(2)
        artifacts = result.get("artifacts", {})
        if artifacts.get("svgPath"):
            print("SVG:", artifacts["svgPath"])
        else:
            print("SVG not generated; install pdf2svg/inkscape/dvisvgm if needed")

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


if __name__ == "__main__":
    main()

