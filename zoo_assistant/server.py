import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import our backend API
from backend.api.main import app as api_app

# Create main app
app = FastAPI(
    title="Zoo Assistant",
    description="AI-powered assistant for zookeepers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend", "static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "frontend", "templates"))

# Mount API
app.mount("/api", api_app)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main frontend page."""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    # Create data directories if they don't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), "data", "uploads"), exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )