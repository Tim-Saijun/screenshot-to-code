from typing import Awaitable, Callable, List
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk

MODEL_GPT_4_VISION = "gpt-4-vision-preview"


async def stream_openai_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    base_url: str | None,
    callback: Callable[[str], Awaitable[None]],
) -> str:
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    model = MODEL_GPT_4_VISION

    # Base parameters
    params = {"model": model, "messages": messages, "stream": True, "timeout": 600}

    # Add 'max_tokens' only if the model is a GPT4 vision model
    if model == MODEL_GPT_4_VISION:
        params["max_tokens"] = 4096
        params["temperature"] = 0

    total_tokens = 0  # Initialize token counter
    stream = await client.chat.completions.create(**params)  # type: ignore
    full_response = ""
    async for chunk in stream:  # type: ignore
        assert isinstance(chunk, ChatCompletionChunk)
        content = chunk.choices[0].delta.content or ""
        estimated_tokens = len(content) / 4  # Rough estimate of tokens
        total_tokens += estimated_tokens  # Accumulate token count
        full_response += content
        await callback(content)

    await client.close()

    print(f"💧💧💧 Estimated total tokens consumed: {total_tokens}")  # Print estimated total tokens consumed

    return full_response
