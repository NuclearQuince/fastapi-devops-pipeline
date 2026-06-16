from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class RequestLog(Base):
    """
    Represents a single logged HTTP request.
    Every request to the app gets written as one row in this table,
    which powers the /stats endpoint and Grafana dashboards.
    """
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)          # Unique row ID
    method = Column(String, index=True)                          # HTTP method, e.g. GET, POST
    path = Column(String, index=True)                             # Endpoint path that was called
    status_code = Column(Integer)                                  # HTTP response status code
    response_time_ms = Column(Float)                               # How long the request took, in ms
    timestamp = Column(DateTime(timezone=True), server_default=func.now())  # When the request happened