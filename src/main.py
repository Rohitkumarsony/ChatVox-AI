from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from router.chat_router import chat_routers 

# Initialize FastAPI app
app = FastAPI()

# Add middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# Include the chat_router
app.include_router(chat_routers)

# Set up the Jinja2 template engine
templates = Jinja2Templates(directory="templates")


# Define a route to render the index.html page
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    # Render the index.html page using Jinja2
    return templates.TemplateResponse("index.html", {"request": request})
