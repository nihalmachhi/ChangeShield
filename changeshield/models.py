from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Link(BaseModel):
    source: str
    target: str
    enabled: bool = True
    config_line: str = Field(default="topology", max_length=240)


class UnsupportedLine(BaseModel):
    device: str
    line_number: int = Field(ge=1)
    text: str = Field(max_length=1000)


class Snapshot(BaseModel):
    nodes: list[str] = Field(min_length=1, max_length=500)
    links: list[Link] = Field(default_factory=list, max_length=5000)
    unsupported_lines: list[UnsupportedLine] = Field(default_factory=list, max_length=500)

    @model_validator(mode="after")
    def validate_links(self):
        known = set(self.nodes)
        for link in self.links:
            if link.source not in known or link.target not in known:
                raise ValueError("Every link endpoint must be declared in nodes")
        return self


class Intent(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    source: str
    destination: str
    property: Literal["reachable", "isolated"] = "reachable"
    critical: bool = True


class ChangeRequest(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    before: Snapshot
    after: Snapshot
    intents: list[Intent] = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_intents(self):
        for intent in self.intents:
            if intent.source not in self.after.nodes or intent.destination not in self.after.nodes:
                raise ValueError("Intent endpoints must be declared in the after snapshot")
        return self
