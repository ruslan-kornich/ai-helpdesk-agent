from abc import ABC, abstractmethod
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class LLMProvider(ABC):
    @abstractmethod
    async def complete_structured(
        self, system_prompt: str, user_prompt: str, schema: type[SchemaType]
    ) -> SchemaType: ...

    @abstractmethod
    async def complete_text(self, system_prompt: str, user_prompt: str) -> str: ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def complete_structured(
        self, system_prompt: str, user_prompt: str, schema: type[SchemaType]
    ) -> SchemaType:
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            response_format=schema,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("LLM returned no parsed structured output")
        return parsed

    async def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()
