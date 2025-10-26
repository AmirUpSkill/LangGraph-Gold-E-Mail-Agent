from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import get_settings
from app.api.endpoints import router as email_router

# --- Initialization ---
settings = get_settings()

app = FastAPI(
    title="Cold Email Generator API",
    description="Multi-agent email drafting with branching synthesis powered by LangGraph.",
    version="0.1.0",
    debug=settings.debug
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(email_router)

@app.get("/health")
async def health_check():
    """
        Simple health check endpoint.
    """
    return {"status": "ok", "version": app.version}