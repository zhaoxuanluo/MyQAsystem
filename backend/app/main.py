"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.database import init_db
from app.api.v1 import knowledge, document, chat, agent, shortcut, llm_provider, memory
from app.mcp.server import router as mcp_router
from app.utils.webpage_publisher import ensure_published_pages_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

os.makedirs("uploads/published_pages", exist_ok=True)
app.mount("/published-pages", StaticFiles(directory="uploads/published_pages"), name="published_pages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(knowledge.router, prefix=settings.API_PREFIX, tags=["Knowledge Base"])
app.include_router(document.router, prefix=settings.API_PREFIX, tags=["Documents"])
app.include_router(chat.router, prefix=settings.API_PREFIX, tags=["Chat"])
app.include_router(agent.router, prefix=settings.API_PREFIX, tags=["Agents"])
app.include_router(shortcut.router, prefix=settings.API_PREFIX, tags=["Shortcuts"])
app.include_router(llm_provider.router, prefix=settings.API_PREFIX, tags=["LLM Providers"])
app.include_router(mcp_router, prefix="/mcp", tags=["MCP"])
app.include_router(memory.router, prefix=settings.API_PREFIX, tags=["Memory"])
app.mount("/published-pages", StaticFiles(directory=str(ensure_published_pages_dir())), name="published-pages")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
