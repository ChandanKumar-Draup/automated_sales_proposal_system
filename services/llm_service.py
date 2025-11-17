"""LLM service for interacting with language models."""
import os
from typing import Optional, List, Dict, Any
from config import settings


class LLMService:
    """Service for LLM interactions."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM service."""
        self.provider = provider or settings.default_llm_provider
        self.model = model or settings.default_model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self.client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        elif self.provider == "anthropic":
            try:
                import anthropic
                api_key = settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")

                # Check if we have the new SDK (0.3.0+)
                if hasattr(anthropic, 'Anthropic'):
                    self.client = anthropic.Anthropic(api_key=api_key)
                else:
                    # Fallback for older versions
                    self.client = anthropic.Client(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic>=0.7.0")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using the LLM."""
        temp = temperature if temperature is not None else settings.temperature
        tokens = max_tokens if max_tokens is not None else settings.max_tokens

        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens,
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                # Use the Messages API (modern Anthropic API)
                kwargs = {
                    "model": self.model,
                    "max_tokens": tokens,
                    "temperature": temp,
                    "messages": [{"role": "user", "content": prompt}]
                }
                if system_prompt:
                    kwargs["system"] = system_prompt

                response = self.client.messages.create(**kwargs)
                return response.content[0].text

        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def generate_structured(
        self, prompt: str, system_prompt: Optional[str] = None, schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured output (JSON)."""
        import json

        structured_prompt = f"{prompt}\n\nRespond with valid JSON only."
        if schema:
            structured_prompt += f"\n\nExpected schema: {json.dumps(schema)}"

        response = self.generate(prompt=structured_prompt, system_prompt=system_prompt, temperature=0.3)

        # Try to extract JSON from response
        try:
            # Find JSON in response (might be wrapped in markdown code blocks)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback: try to find JSON in the response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON from response: {response}")

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Async version of generate (currently just wraps sync version)."""
        # For MVP, we'll use sync version. In production, use async clients
        return self.generate(prompt, system_prompt, temperature, max_tokens)
