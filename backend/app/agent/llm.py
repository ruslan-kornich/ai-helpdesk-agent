import time
from abc import ABC, abstractmethod
from typing import TypeVar

from loguru import logger
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
        logger.debug(
            "OpenAI structured request | model={model} schema={schema}\n"
            "--- system ---\n{system}\n--- user ---\n{user}",
            model=self.model,
            schema=schema.__name__,
            system=system_prompt,
            user=user_prompt,
        )
        started_at = time.perf_counter()
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            response_format=schema,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        parsed = response.choices[0].message.parsed
        logger.debug(
            "OpenAI structured response | elapsed_ms={elapsed:.0f} usage={usage} parsed={parsed}",
            elapsed=elapsed_ms,
            usage=response.usage.model_dump() if response.usage else None,
            parsed=parsed.model_dump() if parsed is not None else None,
        )
        if parsed is None:
            raise ValueError("LLM returned no parsed structured output")
        return parsed

    async def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug(
            "OpenAI text request | model={model}\n--- system ---\n{system}\n--- user ---\n{user}",
            model=self.model,
            system=system_prompt,
            user=user_prompt,
        )
        started_at = time.perf_counter()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        content = (response.choices[0].message.content or "").strip()
        logger.debug(
            "OpenAI text response | elapsed_ms={elapsed:.0f} usage={usage}\n"
            "--- content ---\n{content}",
            elapsed=elapsed_ms,
            usage=response.usage.model_dump() if response.usage else None,
            content=content,
        )
        return content
