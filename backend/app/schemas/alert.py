from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scan_id: str
    severity: str
    title: str
    description: str
    rule_name: str
    source_ip: str | None
    created_at: datetime
