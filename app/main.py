import time
import os
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base, get_db
from app.models import RequestLog

# Create all tables on startup if they don't already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Expose Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware that runs on every request. Times how long the request
    takes, then writes a RequestLog row to the database after the
    response is sent. Skips logging for /metrics to avoid noise.
    """
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    if request.url.path != "/metrics":
        db = next(get_db())
        try:
            log_entry = RequestLog(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time_ms=duration_ms,
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()

    return response


@app.get('/')
def read_root(request: Request):
    """Serves the landing page with navigation to all endpoints."""
    name = os.getenv("APP_OWNER_NAME", "World")
    return templates.TemplateResponse(
        name='index.html', request=request,
        context={'name': name}
    )


@app.get('/health')
def health_check():
    return {'status': 'ok'}


@app.get('/health/db')
def health_check_db(db: Session = Depends(get_db)):
    """Checks that the database connection is alive."""
    try:
        db.execute(func.now())
        return {'status': 'ok', 'database': 'connected'}
    except Exception as e:
        return {'status': 'error', 'database': str(e)}


@app.get('/items/{item_id}')
def get_item(item_id: int):
    return {'item_id': item_id, 'name': f'Item {item_id}'}


@app.get('/stats')
def get_stats(db: Session = Depends(get_db)):
    """
    Returns aggregate statistics from all logged requests:
    total count, average response time, and a breakdown by endpoint.
    """
    total_requests = db.query(RequestLog).count()

    avg_response_time = db.query(func.avg(RequestLog.response_time_ms)).scalar() or 0

    by_path = (
        db.query(RequestLog.path, func.count(RequestLog.id).label("count"))
        .group_by(RequestLog.path)
        .order_by(func.count(RequestLog.id).desc())
        .all()
    )

    return {
        'total_requests': total_requests,
        'avg_response_time_ms': round(avg_response_time, 2),
        'requests_by_endpoint': [{'path': p, 'count': c} for p, c in by_path],
    }
