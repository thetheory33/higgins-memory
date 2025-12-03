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
    print(f"\n[ACTION] Searching memory for: '{query}'")
    
    try:
        my_filters = {"user_id": FIXED_USER_ID}
        
        # API Call
        results = memory.search(query=query, filters=my_filters)
        
        # --- DEBUG LOGGING (So we can see exactly what came back) ---
        print(f"[DEBUG] Raw data received: {results}")

        # --- THE FIX: Handle different return formats ---
        # If it returns a Dictionary (The Box), we look for the list inside
        if isinstance(results, dict):
            if "results" in results:
                results = results["results"]
            elif "data" in results:
                results = results["data"]
            # If it's a dict but has no list inside, it might be an empty response
            else:
                 # If the dict is just empty or not what we expect, treat as empty list
                 pass
        
        # If it's not a list now (and not a dict we successfully unwrapped), safety check:
        if not isinstance(results, list):
            # Sometimes empty search returns just a message or empty dict
            results = []

        if not results:
            print("[RESULT] No memories found.")
            return "No relevant memories found."
        
        # Clean up the results
        # We add a safety check here too in case the item isn't a dictionary
        found_memories = []
        for item in results:
            if isinstance(item, dict) and 'memory' in item:
                found_memories.append(f"- {item['memory']}")
            else:
                # Fallback for weird data
                found_memories.append(f"- {str(item)}")

        print(f"[RESULT] Found: {found_memories}")
        return "Found these memories:\n" + "\n".join(found_memories)

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        return f"Error searching memory: {str(e)}"

# --- RUN SERVER ---
if __name__ == "__main__":
    # Listen on 0.0.0.0 (required for cloud) and port 8080
    mcp.run(transport="sse", host="0.0.0.0", port=8080)