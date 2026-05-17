from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanCreate(BaseModel):
    target_name: str = Field(min_length=1, max_length=200)

    @field_validator("target_name")
    @classmethod
    def validate_target_name(cls, value: str) -> str:
        target_name = value.strip()
        if not target_name:
            raise ValueError("target_name must not be empty")
        return target_name


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    target_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    created_at: datetime
