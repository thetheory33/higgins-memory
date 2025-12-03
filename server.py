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
        # Standard add
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
    # If it's not a list now (and not a dict we successfully unwrapped), safety check:
    # (Simplified logic for clarity)
    
    print(f"\n[ACTION] Searching memory for: '{query}'")
    
    try:
        my_filters = {"user_id": FIXED_USER_ID}
        results = memory.search(query=query, filters=my_filters)
        
        # --- DEBUG LOGGING ---
        print(f"[DEBUG] Raw data received: {results}")

        # Unwrap dictionary if needed
        if isinstance(results, dict):
            if "results" in results:
                results = results["results"]
            elif "data" in results:
                results = results["data"]
        
        # Safety fallback
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

# --- SMART CLOUD RUNNER (The Fix) ---
if __name__ == "__main__":
    import uvicorn
    
    print("Starting Higgins Memory Server...")
    
    # We look for the hidden app object using common names
    # The library developers hide it in different places depending on version
    app = getattr(mcp, "_app", None) or getattr(mcp, "_starlette_app", None) or getattr(mcp, "app", None)
    
    if app:
        print("✅ Found internal app! Starting server on 0.0.0.0:8080...")
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        # If we can't find it, we print EVERYTHING so we can see the real name in logs
        print("❌ COULD NOT FIND APP. Here is what is inside 'mcp':")
        print(dir(mcp))
        # Fallback: Try running normally (might fail on port binding but worth a shot)
        mcp.run(transport="sse")