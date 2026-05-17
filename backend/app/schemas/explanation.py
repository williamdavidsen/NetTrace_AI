from pydantic import BaseModel


class AlertExplanationResponse(BaseModel):
    alert_id: str
    rule_name: str
    summary: str
    pattern: str
    recommended_action: str
