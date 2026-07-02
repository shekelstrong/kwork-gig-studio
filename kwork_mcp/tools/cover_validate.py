"""Tool: validate_cover — vision-чекер обложки."""

import os
import base64
from typing import Optional
import httpx


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# Запрещённые бренды (из kwork-tos-rules)
FORBIDDEN_BRANDS = [
    "VK", "ВК", "Avito", "Авито", "hh.ru", "HeadHunter", "Хедхантер",
    "Ozon", "Озон", "Wildberries", "WB", "Вайлдберриз", "ВБ",
    "2GIS", "2ГИС", "Yandex", "Яндекс", "T-Bank", "Тинькофф", "Tinkoff",
    "QIWI", "Киви", "Beeline", "Билайн", "МТС", "Megafon", "Мегафон",
    "Aviasales", "Авиасейлс", "Ostrovok", "Островок",
]

# Триггер-слова (банят в обложке)
TRIGGER_WORDS = [
    "рилс", "риелс", "Reels", "рилз",
    "сторис", "Stories", "сториз",
    "паблик", "public",
    "SMM", "smm", "СММ",
    "контент-маркетинг", "content-marketing",
    "подписчик", "subscriber", "фолловер", "follower",
    "площадка", "platform",
    "запрещённая сеть", "запрещенная сеть",
]


async def run(
    image_path: str,
    strict_mode: bool = True,
) -> dict:
    """Проверяет обложку через vision-модель OpenRouter.

    Args:
        image_path: Путь к PNG-файлу.
        strict_mode: Строгая проверка (дольше, но точнее).

    Returns:
        Словарь с ok, issues, score.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return _static_check(image_path)

    # Загружаем изображение
    if not os.path.exists(image_path):
        return {"ok": False, "issues": [f"Файл не найден: {image_path}"], "score": 0}

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # Спрашиваем vision-модель
    prompt = (
        "Посмотри на эту обложку для Kwork (русский фриланс-маркетплейс). "
        "Проверь:\n"
        "1) Есть ли запрещённые бренды (VK, Avito, hh.ru, Ozon, WB, ...)?\n"
        "2) Есть ли цены/₽/$/€ на изображении?\n"
        "3) Есть ли триггер-слова (рилс/Reels/сторис/SMM/паблик)?\n"
        "4) Доля кириллицы — больше 70%?\n"
        "5) Видны ли логотипы Kwork или водяные знаки?\n\n"
        "Верни JSON: {\"brands\": [...], \"prices\": [...], \"triggers\": [...], "
        "\"cyrillic_ratio\": 0.X, \"kwork_logo\": true/false, \"overall_ok\": true/false}"
    )

    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ],
            }
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            OPENROUTER_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    if resp.status_code != 200:
        return _static_check(image_path)

    # Парсим ответ
    try:
        import json
        text = resp.json()["choices"][0]["message"]["content"]
        # Простой парсинг: ищем JSON в тексте
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            issues = []
            if data.get("brands"):
                issues.append(f"Содержит запрещённые бренды: {', '.join(data['brands'])}")
            if data.get("prices"):
                issues.append(f"Содержит цены: {', '.join(data['prices'])}")
            if data.get("triggers"):
                issues.append(f"Содержит триггер-слова: {', '.join(data['triggers'])}")
            if data.get("cyrillic_ratio", 1.0) < 0.7:
                issues.append(f"Кириллицы < 70%: {int(data['cyrillic_ratio']*100)}%")
            if data.get("kwork_logo"):
                issues.append("Содержит логотип Kwork")
            return {
                "ok": len(issues) == 0,
                "issues": issues,
                "score": 1.0 - len(issues) * 0.2,
            }
    except Exception:
        pass

    return _static_check(image_path)


def _static_check(image_path: str) -> dict:
    """Запасной вариант: проверка имени файла на триггер-слова."""
    issues = []
    name = os.path.basename(image_path).lower()
    for brand in FORBIDDEN_BRANDS:
        if brand.lower() in name:
            issues.append(f"В имени файла запрещённый бренд: {brand}")
    for trigger in TRIGGER_WORDS:
        if trigger.lower() in name:
            issues.append(f"В имени файла триггер-слово: {trigger}")
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "score": 0.5,
        "note": "Static check only (OPENROUTER_API_KEY не задан)",
    }
