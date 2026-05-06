"""
main.py
-------
FastAPI entry point for the Multi-Agent Stock Research System.

Routes:
  GET  /              → serves the HTML dashboard
  POST /analyze       → blocking analysis, returns full final_state JSON
  GET  /health        → health check
"""

import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.models import AnalyzeRequest, AnalyzeResponse, HealthResponse, ErrorResponse
from api.pipeline import run_research_pipeline
from api.config import get_settings


# ── Helpers ───────────────────────────────────────────────────────────

def _to_dict(obj) -> dict | None:
    """
    Coerce an agent output to a plain dict regardless of whether the
    pipeline returned a Pydantic model instance, a dataclass, or an
    already-plain dict.  Returns None if obj is None.
    """
    if obj is None:
        return None
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    # Pydantic v1
    if hasattr(obj, "dict"):
        return obj.dict()
    # dataclass
    if hasattr(obj, "__dataclass_fields__"):
        import dataclasses
        return dataclasses.asdict(obj)
    # Already a dict
    if isinstance(obj, dict):
        return obj
    # Last resort: try __dict__
    return vars(obj) if hasattr(obj, "__dict__") else None

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("stock_research.main")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Stock Research API starting up…")
    yield
    logger.info("👋 Stock Research API shutting down…")


# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Stock Research API",
    description="LangGraph-powered parallel research pipeline: Fundamentals · Technical · News → Synthesis → Critic",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static assets (CSS/JS if ever extracted)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ── Routes ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    """Serve the single-page research dashboard."""
    html_path = Path(__file__).parent / "templates" / "dashboard.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="Dashboard template not found.")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/health", response_model=HealthResponse, tags=["Meta"])
async def health():
    """Liveness probe."""
    return HealthResponse(status="ok", version=app.version)

@app.get("/stocks", tags=["Meta"])
async def get_stocks():
    """Return all NSE stock codes for autocomplete."""
    try:
        from nsetools import Nse
        nse = Nse()
        all_stocks = nse.get_stock_codes()
        return JSONResponse(content=[t for t in all_stocks if t])
    except Exception as exc:
        logger.warning("Failed to fetch stock codes: %s", exc)
        raise HTTPException(status_code=500, detail=f"Could not load stock list: {exc}")


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Research"],
    summary="Run full multi-agent stock research",
    description=(
        "Accepts a stock ticker (e.g. `SBIN.NS`, `RELIANCE.NS`, `AAPL`) and an optional "
        "depth level, runs the parallel LangGraph pipeline "
        "(Fundamentals + Technical + News → Synthesis → Critic), "
        "and returns the complete `final_state` JSON."
    ),
)
async def analyze(request: AnalyzeRequest):
    """
    Blocking endpoint: waits for all agents to complete before returning.
    Typical latency: 20–60 s depending on ticker and model.
    """

    ticker = request.ticker.strip().upper()
    logger.info("▶ /analyze  ticker=%s  depth=%s", ticker, None)

    t0 = time.perf_counter()
    try:
        final_state = await run_research_pipeline(ticker=ticker, depth=None)
    except ValueError as exc:
        logger.warning("Validation error for %s: %s", ticker, exc)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Pipeline failed for %s", ticker)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    elapsed = round(time.perf_counter() - t0, 2)
    logger.info("✅ /analyze  ticker=%s  elapsed=%.2fs", ticker, elapsed)

    return AnalyzeResponse(
        ticker=ticker,
        elapsed_seconds=elapsed,
        fundamentals_output=_to_dict(final_state.get("fundamentals_output")),
        technical_output=_to_dict(final_state.get("technical_output")),
        news_output=_to_dict(final_state.get("news_output")),
        synthesis_output=_to_dict(final_state.get("synthesis_output")),
        critic_output=_to_dict(final_state.get("critic_output")),
    )