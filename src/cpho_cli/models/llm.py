from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field


class LLMUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMResponse(BaseModel):
    content: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    raw: dict[str, Any] = Field(default_factory=dict)


class ChatTextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ChatImageURL(BaseModel):
    url: str


class ChatImageURLBlock(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ChatImageURL


class ChatFileData(BaseModel):
    filename: str
    file_data: str


class ChatFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: ChatFileData


ChatContentBlock: TypeAlias = ChatTextBlock | ChatImageURLBlock | ChatFileBlock
ChatMessageContent: TypeAlias = str | list[dict[str, Any]]
ChatMessage: TypeAlias = dict[str, str | ChatMessageContent]


class ModelCapabilities(BaseModel):
    input_modalities: set[str] = Field(default_factory=lambda: {"text"})
    supported_parameters: set[str] = Field(default_factory=set)

    @property
    def supports_image(self) -> bool:
        return "image" in self.input_modalities

    @property
    def supports_file(self) -> bool:
        return "file" in self.input_modalities
