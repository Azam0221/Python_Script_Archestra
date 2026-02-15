import uvicorn
import asyncio
import json
import httpx
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.responses import JSONResponse, StreamingResponse, Response


SPRING_BOOT_URL = "http://localhost:8080/api"


async def send_log(agent_id, message):
    try:
        async with httpx.AsyncClient() as client:
        
            await client.post(f"{SPRING_BOOT_URL}/v1/agent/logs/{agent_id}", json={"log": message})
    except Exception as e:
        print(f"❌ Failed to send log to Java: {e}")

async def universal_handler(scope, receive, send):
    assert scope["type"] == "http"
    method = scope["method"]

    if method == "GET":
        async def event_generator():
            yield "event: endpoint\ndata: /messages\n\n"
            while True: await asyncio.sleep(1)
        await StreamingResponse(event_generator(), media_type="text/event-stream")(scope, receive, send)
        return


    if method == "POST":
        body_bytes = b""
        more_body = True
        while more_body:
            message = await receive()
            body_bytes += message.get("body", b"")
            more_body = message.get("more_body", False)
        
        try:
            data = json.loads(body_bytes)
            rpc_method = data.get("method")
            msg_id = data.get("id")
            params = data.get("params", {})
            result = {}

            if rpc_method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "Sentinel-Bridge", "version": "1.0"}
                }

            elif rpc_method == "tools/list":
                result = {
                    "tools": [
                        {"name": "status", "description": "Check system health", "inputSchema": {"type": "object"}},
                        {"name": "deploy", "description": "Trigger deployment", "inputSchema": {"type": "object", "properties": {"env": {"type": "string"}}}},
                        {"name": "request_permission", "description": "Request human approval for dangerous tasks", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]}}
                    ]
                }
                

            elif rpc_method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                agent_id = "agent-1" 
                text_reply = ""

                async with httpx.AsyncClient() as client:
                    try:
                        kill_check = await client.get(f"{SPRING_BOOT_URL}/v1/agent/should-kill/{agent_id}")
                        if kill_check.json().get("shouldKill"):
                            await send_log(agent_id, "🛑 CRITICAL: Execution blocked. Agent is TERMINATED.")
                            text_reply = "ACCESS DENIED: Agent-1 has been terminated by the Admin."
                        
                        elif tool_name == "request_permission":
                            action_desc = tool_args.get("action")
                            await send_log(agent_id, f"🚨 AUTH_REQUIRED: Requesting permission for [{action_desc}]")
                            print(f"🚨 AI ASKING FOR PERMISSION: {action_desc}")
                            
                            ask_resp = await client.post(f"{SPRING_BOOT_URL}/v1/permission/agent/ask", json={"agentId": agent_id, "action": action_desc})
                            req_id = ask_resp.json().get("id")
                            
                            text_reply = "⏳ TIMEOUT: Admin did not respond."
                            for _ in range(30): # Poll for 60 seconds
                                status_check = await client.get(f"{SPRING_BOOT_URL}/v1/permission/agent/status/{req_id}")
                                status = status_check.json().get("status")
                                if status == "APPROVED":
                                    await send_log(agent_id, f"✅ AUTH_GRANTED: Admin authorized [{action_desc}]")
                                    text_reply = f"✅ PERMISSION GRANTED: {action_desc}"
                                    break
                                elif status == "DENIED":
                                    await send_log(agent_id, f"❌ AUTH_DENIED: Admin rejected [{action_desc}]")
                                    text_reply = "❌ PERMISSION DENIED by Admin."
                                    break
                                await asyncio.sleep(2)

                        else:
                            await send_log(agent_id, f"⚙️ EXECUTING_TOOL: {tool_name}")
                            resp = await client.post(f"{SPRING_BOOT_URL}/{tool_name}", json=tool_args, timeout=5.0)
                            text_reply = f"✅ Java says: {resp.json().get('message')}" if resp.status_code == 200 else "❌ Java Error"
                    
                    except Exception as e:
                        text_reply = f"⚠️ Connection Failure: {str(e)}"

                result = {"content": [{"type": "text", "text": text_reply}]}

            await JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": result})(scope, receive, send)
            return

        except Exception as e:
            print(f"❌ ERROR: {e}")
            await JSONResponse({"error": str(e)}, status_code=500)(scope, receive, send)
            return

routes = [ Mount("/", app=universal_handler) ]
middleware = [ Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]) ]
app = Starlette(routes=routes, middleware=middleware)

if __name__ == "__main__":
    print("🚀 SENTINEL BRIDGE RUNNING on http://0.0.0.0:9095")
    uvicorn.run(app, host="0.0.0.0", port=9095)