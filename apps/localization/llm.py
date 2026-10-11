"""
Claude API istemcisi — tüm AI üretim/çeviri çağrıları buradan geçer.

- Structured outputs (output_config.format) ile JSON şeması garantili cevap
- Streaming + get_final_message() (uzun blog içeriklerinde timeout olmasın)
- Server-side fallback: güvenlik sınıflandırıcısı reddederse otomatik başka modele düşer
- Prompt caching: kaynak içerik bloğu cache'lenir → aynı yazının 15 dile çevirisi
  kaynak metni tekrar tekrar faturalamaz
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class LLMError(Exception):
    pass


class LLMNotConfigured(LLMError):
    pass


_client = None


def get_client():
    global _client
    if _client is None:
        import anthropic

        if not settings.ANTHROPIC_API_KEY:
            raise LLMNotConfigured("ANTHROPIC_API_KEY .env içinde tanımlı değil.")
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, max_retries=4)
    return _client


def is_configured() -> bool:
    return bool(settings.ANTHROPIC_API_KEY)


def generate_json(*, system: str, blocks: list, schema: dict, effort: str = "medium",
                  max_tokens: int = 32000) -> dict:
    """JSON şemasına uyan bir cevap üretir.

    blocks: user mesajının içerik blokları. Sabit (cache'lenebilir) bloklar başta,
    değişken bloklar sonda olmalı. Bir bloğa {"cache": True} verilirse cache noktası olur.
    """
    import anthropic

    client = get_client()
    content = []
    for b in blocks:
        block = {"type": "text", "text": b["text"]}
        if b.get("cache"):
            block["cache_control"] = {"type": "ephemeral"}
        content.append(block)

    try:
        with client.beta.messages.stream(
            model=settings.CONTENT_MACHINE_MODEL,
            max_tokens=max_tokens,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": content}],
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        ) as stream:
            message = stream.get_final_message()
    except anthropic.RateLimitError as e:
        raise LLMError(f"Rate limited: {e}") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError(f"Connection error: {e}") from e

    if message.stop_reason == "refusal":
        category = getattr(message.stop_details, "category", None) if message.stop_details else None
        raise LLMError(f"Model refused (category={category})")
    if message.stop_reason == "max_tokens":
        raise LLMError("Output truncated (max_tokens). Increase max_tokens or split the content.")

    text = "".join(b.text for b in message.content if b.type == "text")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"Invalid JSON from model: {e}") from e

    usage = message.usage
    logger.info("LLM ok model=%s in=%s out=%s cache_read=%s", message.model, usage.input_tokens,
                usage.output_tokens, getattr(usage, "cache_read_input_tokens", 0))
    return data
