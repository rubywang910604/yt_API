from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from pydantic import BaseModel

# Define request model
class ChatMessage(BaseModel):
    message: str

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Langflow API Wrapper",
    description="A FastAPI wrapper for Langflow chat API",
    version="1.0.0"
)

# Langflow API configuration
LANGFLOW_URL = "https://langflow-c.u22.ypcloud.com/api/v1/run/4653f2ce-2583-486a-8f0b-38268596a24a"
HEADERS = {'Content-Type': 'application/json'}

# Security: HTTP Bearer token authentication
security = HTTPBearer()
API_KEY = "yt355a7fecb0"  # Custom API key set by the user

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Bearer token in the Authorization header
    """
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid Bearer Token"
        )
    return credentials.credentials

@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information
    """
    return {
        "message": "Welcome to Langflow API Wrapper",
        "docs_url": "/docs",
        "api_key": API_KEY,  # Display the API Key for reference
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }

@app.post("/chat")
async def chat(
    message: ChatMessage,
    token: str = Depends(verify_bearer_token)  # Add token verification
):
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
                json=payload,
                timeout=30.0  # Add timeout
            )

            # Check if request was successful
            response.raise_for_status()
            
            # Return the raw response
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request to Langflow API timed out"
        )
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

@app.get("/health")
async def health_check(
    token: str = Depends(verify_bearer_token)  # Add token verification
):
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
