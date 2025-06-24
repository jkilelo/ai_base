"""
LLM Abstraction Layer for AI Base Platform

This module provides a unified interface for working with different LLM providers
(OpenAI, Azure OpenAI, Anthropic, Hugging Face, etc.) with features like:
- Provider abstraction
- Token usage tracking
- Cost optimization
- Prompt template management
- Response caching
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
import aioredis
from pydantic import BaseModel


class LLMProvider(Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging_face"
    LOCAL = "local"


class MessageRole(Enum):
    """Message roles in conversation"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    """LLM message structure"""

    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response structure"""

    content: str
    provider: LLMProvider
    model: str
    tokens_used: int
    cost: float
    latency_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """LLM configuration"""

    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    retry_attempts: int = 3
    cache_ttl: int = 3600  # Cache TTL in seconds


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    async def generate_stream(
        self, messages: List[LLMMessage], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM"""
        pass

    @abstractmethod
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate the cost for token usage"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate the connection to the LLM provider"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        import openai

        self.client = openai.AsyncOpenAI(api_key=config.api_key)

    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = datetime.now()

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=openai_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs,
            )

            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            tokens_used = response.usage.total_tokens
            cost = self.calculate_cost(tokens_used, self.config.model)

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency,
                metadata={
                    "completion_tokens": response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                },
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def generate_stream(
        self, messages: List[LLMMessage], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API"""
        openai_messages = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=openai_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")

    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost based on OpenAI pricing"""
        # Simplified pricing - update with actual rates
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }

        if model in pricing:
            # Simplified calculation - in practice, separate input/output tokens
            rate = (pricing[model]["input"] + pricing[model]["output"]) / 2
            return (tokens / 1000) * rate

        return 0.0

    async def validate_connection(self) -> bool:
        """Validate OpenAI connection"""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False


class PromptTemplate:
    """Template for LLM prompts with variable substitution"""

    def __init__(self, template: str, variables: List[str] = None):
        self.template = template
        self.variables = variables or []

    def render(self, **kwargs) -> str:
        """Render the template with provided variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


class LLMManager:
    """Central manager for LLM operations with caching and cost tracking"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._templates: Dict[str, PromptTemplate] = {}
        self._redis_url = redis_url
        self._redis = None

    async def initialize(self):
        """Initialize the LLM manager"""
        try:
            self._redis = await aioredis.from_url(self._redis_url)
        except Exception:
            print("Warning: Redis not available, caching disabled")
            self._redis = None

    def register_provider(self, name: str, provider: BaseLLMProvider):
        """Register an LLM provider"""
        self._providers[name] = provider

    def register_template(self, name: str, template: PromptTemplate):
        """Register a prompt template"""
        self._templates[name] = template

    async def generate(
        self,
        provider_name: str,
        messages: Union[List[LLMMessage], str],
        template_name: str = None,
        template_vars: Dict[str, Any] = None,
        use_cache: bool = True,
        **kwargs,
    ) -> LLMResponse:
        """Generate LLM response with caching and cost tracking"""

        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")

        provider = self._providers[provider_name]

        # Handle template rendering
        if template_name:
            if template_name not in self._templates:
                raise ValueError(f"Template {template_name} not found")

            template = self._templates[template_name]
            rendered_content = template.render(**(template_vars or {}))

            if isinstance(messages, str):
                messages = rendered_content
            else:
                # Add rendered template as system message
                messages.insert(
                    0, LLMMessage(role=MessageRole.SYSTEM, content=rendered_content)
                )

        # Convert string to message format
        if isinstance(messages, str):
            messages = [LLMMessage(role=MessageRole.USER, content=messages)]

        # Check cache
        cache_key = None
        if use_cache and self._redis:
            cache_key = self._generate_cache_key(provider_name, messages, kwargs)
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                return cached_response

        # Generate response
        response = await provider.generate(messages, **kwargs)

        # Cache response
        if use_cache and self._redis and cache_key:
            await self._cache_response(cache_key, response)

        # Track usage
        await self._track_usage(provider_name, response)

        return response

    async def generate_stream(
        self, provider_name: str, messages: Union[List[LLMMessage], str], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")

        provider = self._providers[provider_name]

        if isinstance(messages, str):
            messages = [LLMMessage(role=MessageRole.USER, content=messages)]

        async for chunk in provider.generate_stream(messages, **kwargs):
            yield chunk

    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        if not self._redis:
            return {"error": "Usage tracking not available"}

        # Implementation would aggregate usage data from Redis
        # This is a simplified version
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_provider": {},
            "by_model": {},
        }

    def _generate_cache_key(
        self, provider_name: str, messages: List[LLMMessage], kwargs: Dict[str, Any]
    ) -> str:
        """Generate cache key for request"""
        content = json.dumps(
            {
                "provider": provider_name,
                "messages": [(m.role.value, m.content) for m in messages],
                "kwargs": kwargs,
            },
            sort_keys=True,
        )

        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"

    async def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response"""
        try:
            cached = await self._redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return LLMResponse(**data)
        except Exception:
            pass
        return None

    async def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache response"""
        try:
            data = {
                "content": response.content,
                "provider": response.provider.value,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
                "metadata": response.metadata,
            }
            await self._redis.setex(
                cache_key,
                self._providers[response.provider.value].config.cache_ttl,
                json.dumps(data),
            )
        except Exception:
            pass

    async def _track_usage(self, provider_name: str, response: LLMResponse):
        """Track LLM usage for analytics"""
        try:
            if self._redis:
                usage_key = (
                    f"usage:{datetime.now().strftime('%Y-%m-%d')}:{provider_name}"
                )
                await self._redis.hincrby(usage_key, "requests", 1)
                await self._redis.hincrby(usage_key, "tokens", response.tokens_used)
                await self._redis.hincrbyfloat(usage_key, "cost", response.cost)
                await self._redis.expire(usage_key, 86400 * 30)  # Keep for 30 days
        except Exception:
            pass


# Global LLM manager instance
llm_manager = LLMManager()
