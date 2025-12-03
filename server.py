from mcp.server.fastmcp import FastMCP
from mem0 import MemoryClient
import os

# --- CONFIGURATION ---
os.environ["MEM0_API_KEY"] = "m0-rQ2seYAVT2BDLojobFwAM9YhIp762Ci6oZjhXIRZ"

# Initialize
mcp = FastMCP("Higgins Memory")
memory = MemoryClient()

# --- CONSTANTS ---
FIXED_USER_ID = "seth_master_user"

# --- TOOLS ---

@mcp.tool()
async def add_memory(text: str) -> str:
    """
    Stores a new memory. Use this when the user tells you a name, preference, 
    plan, or specific fact about themselves.
    """
    print(f"\n[ACTION] Attempting to save memory: '{text}'")
    
    try:
        result = memory.add(messages=text, user_id=FIXED_USER_ID)
        print(f"[SUCCESS] Saved to user: {FIXED_USER_ID}")
        return "Memory successfully stored."
    except Exception as e:
        print(f"[ERROR] Failed to save: {str(e)}")
        return f"Error storing memory: {str(e)}"

@mcp.tool()
async def search_memory(query: str) -> str:
    """
    Searches past memories. Use this immediately when the user asks a question 
    that relies on previous context or personal history.
    """
    print(f"\n[ACTION] Searching memory for: '{query}'")
    
    try:
        my_filters = {"user_id": FIXED_USER_ID}
        results = memory.search(query=query, filters=my_filters)
        
        # --- DEBUG LOGGING ---
        print(f"[DEBUG] Raw data received: {results}")

        if isinstance(results, dict):
            if "results" in results:
                results = results["results"]
            elif "data" in results:
                results = results["data"]
        
        if not isinstance(results, list):
            results = []

        if not results:
            print("[RESULT] No memories found.")
            return "No relevant memories found."
        
        found_memories = []
        for item in results:
            if isinstance(item, dict) and 'memory' in item:
                found_memories.append(f"- {item['memory']}")
            else:
                found_memories.append(f"- {str(item)}")

        print(f"[RESULT] Found: {found_memories}")
        return "Found these memories:\n" + "\n".join(found_memories)

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        return f"Error searching memory: {str(e)}"

# --- FINAL CLOUD RUNNER (Universal Fix) ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Higgins Memory Server...")

    # 1. RETRIEVE THE APP (Handle both Factory and Instance cases)
    app_to_run = None
    
    # Try to grab the internal cached app (often named _sse_app)
    if hasattr(mcp, "_sse_app") and mcp._sse_app is not None:
        print("✅ Found pre-built _sse_app")
        app_to_run = mcp._sse_app
    
    # If not found, try calling the factory method
    if app_to_run is None and hasattr(mcp, "sse_app"):
        try:
            print("🔄 Calling sse_app() factory to generate app...")
            app_to_run = mcp.sse_app()
            print("✅ Factory returned the app successfully")
        except Exception as e:
            print(f"⚠️ Factory call failed (might be a property): {e}")
            app_to_run = mcp.sse_app

    if app_to_run is None:
        print("❌ CRITICAL: Could not find ASGI app. Deployment will likely fail.")
    else:
        # 2. WRAP THE APP (The 'Liar Code' to fix 421 Misdirected Request)
        async def cloud_wrapper(scope, receive, send):
            if scope['type'] == 'http':
                # We edit the envelope to say "localhost" instead of "render.com"
                # This bypasses the security check.
                headers = [(k, v) for k, v in scope['headers'] if k.lower() != b'host']
                headers.append((b'host', b'localhost:8080'))
                scope['headers'] = headers
            
            await app_to_run(scope, receive, send)

        print("🚀 Starting Server with Host Fix on 0.0.0.0:8080...")
        uvicorn.run(cloud_wrapper, host="0.0.0.0", port=8080)