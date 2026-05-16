from datetime import datetime
from ipaddress import ip_address
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_PROTOCOLS = {"TCP", "UDP", "ICMP"}


class PacketEventCreate(BaseModel):
    scan_id: UUID
    timestamp: datetime
    source_ip: str
    destination_ip: str
    protocol: str
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
        protocol = value.upper()
        if protocol not in ALLOWED_PROTOCOLS:
            raise ValueError("protocol must be TCP, UDP, or ICMP")
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
