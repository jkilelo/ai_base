"""
Enhanced Main FastAPI Application with Plugin System

This integrates the plugin system with the existing FastAPI backend,
allowing dynamic loading of AI-powered applications.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import os
from typing import Dict, Any

# Import existing modules
from v1.backend.app.core.config import get_settings
from v1.backend.app.core.database import get_database_session
from v1.backend.app.api.health import router as health_router

# Import new core modules
from core.plugins import plugin_manager, BasePlugin
from core.llm import llm_manager, OpenAIProvider, LLMConfig, LLMProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting AI Base Platform...")

    # Initialize LLM manager
    await llm_manager.initialize()

    # Configure LLM providers
    settings = get_settings()
    if hasattr(settings, "openai_api_key") and settings.openai_api_key:
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            api_key=settings.openai_api_key,
            temperature=0.7,
            max_tokens=2000,
        )
        openai_provider = OpenAIProvider(openai_config)
        llm_manager.register_provider("openai", openai_provider)
        print("✅ OpenAI provider configured")

    # Discover and load plugins
    await load_plugins()

    # Register plugin routes
    await register_plugin_routes(app)

    print("✅ AI Base Platform started successfully!")
    print(f"📋 Loaded plugins: {list(plugin_manager.list_plugins().keys())}")

    yield

    # Shutdown
    print("🛑 Shutting down AI Base Platform...")
    for plugin_name in plugin_manager.get_active_plugins():
        await plugin_manager.unregister_plugin(plugin_name)
    print("✅ AI Base Platform shutdown complete")


async def load_plugins():
    """Discover and load all available plugins"""
    apps_dir = Path(__file__).parent / "apps"

    if not apps_dir.exists():
        print("⚠️ No apps directory found")
        return

    # Discover plugins
    discovered_plugins = await plugin_manager.discover_plugins(apps_dir)
    print(f"🔍 Discovered {len(discovered_plugins)} plugins")

    # Load each plugin
    for plugin_class in discovered_plugins:
        try:
            await plugin_manager.register_plugin(plugin_class, config={})
            print(f"✅ Loaded plugin: {plugin_class.__name__}")
        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_class.__name__}: {e}")


async def register_plugin_routes(app: FastAPI):
    """Register API routes from all active plugins"""
    api_routes = await plugin_manager.get_all_api_routes()

    for route_info in api_routes:
        app.include_router(
            route_info["router"],
            prefix=route_info["path"],
            tags=[route_info["path"].split("/")[-1]],
        )
        print(f"📡 Registered API route: {route_info['path']}")


# Create FastAPI app with lifespan
app = FastAPI(
    title="AI Base Platform",
    description="Extensible platform for AI-powered development tools",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing health router
app.include_router(health_router, prefix="/api/v1", tags=["health"])


# Enhanced health endpoint with plugin status
@app.get("/api/v1/health/plugins")
async def get_plugins_health():
    """Get health status of all plugins"""
    try:
        plugin_health = await plugin_manager.health_check_all()
        active_plugins = plugin_manager.get_active_plugins()

        return {
            "status": "healthy" if active_plugins else "no_plugins",
            "message": f"{len(active_plugins)} plugins active",
            "plugins": plugin_health,
            "active_plugins": active_plugins,
            "total_plugins": len(plugin_manager.list_plugins()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Plugin management endpoints
@app.get("/api/v1/plugins")
async def list_plugins():
    """List all registered plugins"""
    plugins = plugin_manager.list_plugins()
    return {
        "plugins": {
            name: {
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description,
                "status": metadata.status.value,
                "author": metadata.author,
                "dependencies": metadata.dependencies,
            }
            for name, metadata in plugins.items()
        },
        "total": len(plugins),
    }


@app.get("/api/v1/plugins/{plugin_name}/info")
async def get_plugin_info(plugin_name: str):
    """Get detailed information about a specific plugin"""
    plugin = plugin_manager.get_plugin(plugin_name)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")

    metadata = plugin.metadata
    health = await plugin.health_check()

    return {
        "name": metadata.name,
        "version": metadata.version,
        "description": metadata.description,
        "author": metadata.author,
        "status": metadata.status.value,
        "api_version": metadata.api_version,
        "dependencies": metadata.dependencies,
        "health": health,
        "api_routes": plugin.get_api_routes(),
        "frontend_routes": plugin.get_frontend_routes(),
    }


# Frontend routes discovery for the React app
@app.get("/api/v1/frontend/routes")
async def get_frontend_routes():
    """Get all frontend routes from plugins for React router"""
    routes = await plugin_manager.get_all_frontend_routes()
    return {"routes": routes, "total": len(routes)}


# LLM management endpoints
@app.get("/api/v1/llm/providers")
async def list_llm_providers():
    """List available LLM providers"""
    return {
        "providers": list(llm_manager._providers.keys()),
        "templates": list(llm_manager._templates.keys()),
    }


@app.get("/api/v1/llm/usage")
async def get_llm_usage(days: int = 7):
    """Get LLM usage statistics"""
    try:
        usage_stats = await llm_manager.get_usage_stats(days)
        return usage_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced root endpoint
@app.get("/")
async def root():
    """Root endpoint with platform information"""
    active_plugins = plugin_manager.get_active_plugins()
    return {
        "platform": "AI Base",
        "version": "2.0.0",
        "description": "Extensible platform for AI-powered development tools",
        "status": "running",
        "active_plugins": active_plugins,
        "total_plugins": len(plugin_manager.list_plugins()),
        "llm_providers": list(llm_manager._providers.keys()),
        "api_docs": "/docs",
        "frontend_url": "http://localhost:3000",
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "available_endpoints": [
                "/api/v1/health",
                "/api/v1/plugins",
                "/api/v1/llm/providers",
                "/docs",
            ],
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8001, reload=True, log_level="info")
