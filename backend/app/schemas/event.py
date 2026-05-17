from datetime import datetime
from ipaddress import ip_address
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PacketEventCreate(BaseModel):
    scan_id: UUID
    timestamp: datetime
    source_ip: str
    destination_ip: str
    protocol: str = Field(min_length=1, max_length=20)
    source_port: int | None = Field(default=None, ge=1, le=65535)
    destination_port: int | None = Field(default=None, ge=1, le=65535)
    packet_size: int = Field(ge=1, le=65535)

    @field_validator("source_ip", "destination_ip")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        ip_address(value)
        return value

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, value: str) -> str:
        protocol = value.strip().upper()
        if not protocol:
            raise ValueError("protocol must not be empty")
        return protocol


class PacketEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scan_id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    protocol: str
    source_port: int | None
    destination_port: int | None
    packet_size: int
    created_at: datetime
