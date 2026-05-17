from pydantic import BaseModel


class MetricsResponse(BaseModel):
    processed_events_total: int
    generated_alerts_total: int
    active_scans_total: int
