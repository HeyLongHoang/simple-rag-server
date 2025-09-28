from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import index, query
from app.state import app_state

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Discover persisted indexes
    app_state.discover_persisted_indexes()
    # Hands over control to the fastapi app
    yield 
    # Shutdown: (Add any necessary cleanup here)

app = FastAPI(
    title="Faiss Vector Store API", 
    version="1.0.0",
    root_path="/index",
    lifespan=lifespan,
)
app.include_router(index.router)
app.include_router(query.router)

@app.get("/", response_model=dict)
async def read_root():
    return {
        'message': (
            'Faiss Vector Store API is running. '
            'To check the API documentation, visit /docs or /redoc.'
        ),
        'version': '1.0.0',
    }