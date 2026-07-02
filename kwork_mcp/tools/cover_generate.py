"""Tool: generate_cover — генерация обложки через OpenRouter."""

import os
from pathlib import Path
from typing import Optional
import httpx


OPENROUTER_URL = "https://openrouter.ai/api/v1/images"


async def run(
    title: str,
    style: str = "dark-saas",
    metrics: Optional[list] = None,
    bullets: Optional[list] = None,
    output_dir: str = "/tmp/kwork-covers",
) -> dict:
    """Генерирует обложку кворка.

    Args:
        title: Заголовок кворка.
        style: dark-saas / light / gradient.
        metrics: Список метрик (например, ["24 часа", "5 000₽"]).
        bullets: 3 буллита с выгодами.
        output_dir: Куда сохранить PNG.

    Returns:
        Словарь с image_path и prompt.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {
            "error": "OPENROUTER_API_KEY не задан. Установи в .env",
            "image_path": None,
        }

    # Собираем промпт в стиле dark-saas
    prompt = _build_prompt(title, style, metrics, bullets)

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "prompt": prompt,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            OPENROUTER_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        if resp.status_code != 200:
            return {"error": f"OpenRouter {resp.status_code}: {resp.text[:500]}"}

        data = resp.json()
        b64 = data.get("data", [{}])[0].get("b64_json")
        if not b64:
            return {"error": "No image in response", "raw": str(data)[:500]}

        # Сохраняем
        import base64
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"kwork-{title[:30].replace(' ', '-')}.png"
        out_path = Path(output_dir) / filename
        out_path.write_bytes(base64.b64decode(b64))

        return {
            "image_path": str(out_path),
            "prompt": prompt,
            "size": "1024x1024",
        }


def _build_prompt(title, style, metrics, bullets) -> str:
    """Собирает промпт для генератора обложки."""
    base = (
        "Cover image for Kwork freelance gig, modern dark SaaS style. "
        "Background: #0a0a0a → #161616 with radial vignette. "
        "Accent colors: mint #7ee787 and sky #79c0ff. "
        "Font: Inter or SF Pro Display, perfect Cyrillic. "
        "Layout 50/50: title and metrics on the left, abstract illustration on the right. "
        "Three bullet points with green checkmarks. "
        f"Title: '{title}'. "
    )
    if metrics:
        base += f"Metrics: {', '.join(metrics)}. "
    if bullets:
        base += f"Bullets: {', '.join(bullets)}. "
    base += (
        "NO brand logos, NO prices, NO trigger words, NO watermarks. "
        "Pure cyrillic typography. Professional, premium look."
    )
    return base
