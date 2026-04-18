import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as routes_router, orchestrator
from api.auth import router as auth_router
from utils.telemetry import telemetry
import time
from fastapi import Request
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting Resume AI System...")
    await orchestrator.init_db()
    yield
    # Shutdown logic (if any)
    print("Shutting down Resume AI System...")

app = FastAPI(
    title="Resume AI - Multi Agent Talent Intelligence API",
    description="Parse resumes, normalize skills, and match candidates to jobs",
    version="1.0.0",
    lifespan=lifespan
)

# Add Telemetry Middleware
@app.middleware("http")
async def add_telemetry(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000 # ms
    
    # Log context: route and results
    route = request.url.path
    telemetry.log_request(route, process_time, response.status_code)
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Include router
app.include_router(auth_router)
app.include_router(routes_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
