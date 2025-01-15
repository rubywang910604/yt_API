from fastapi import FastAPI, HTTPException
import httpx
import json
from pydantic import BaseModel
from typing import Any, Dict

# Define request model
class ChatMessage(BaseModel):
    message: str

# Define response model
class ChatResponse(BaseModel):
    response: Dict[str, Any]  # Changed to accept dictionary response

# Initialize FastAPI app
app = FastAPI(
    title="Langflow API Wrapper",
    description="A FastAPI wrapper for Langflow chat API"
)

# Langflow API configuration
LANGFLOW_URL = "https://langflow-c.u22.ypcloud.com/api/v1/run/4653f2ce-2583-486a-8f0b-38268596a24a"
HEADERS = {'Content-Type': 'application/json'}

@app.post("/chat", response_model=None)  # Removed response_model to return raw response
async def chat(message: ChatMessage):
    """
    Send a chat message to Langflow API and return the response
    """
    try:
        # Prepare the request payload
        payload = {
            "input_value": message.message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                "ChatOutput-Id8I6": {},
                "ChatInput-tr6V9": {},
                "CustomComponent-dfT0Z": {}
            }
        }

        # Make request to Langflow API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LANGFLOW_URL,
                headers=HEADERS,
                json=payload
            )

            # Check if request was successful
            response.raise_for_status()
            
            # Return the raw response
            return response.json()

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Langflow API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
