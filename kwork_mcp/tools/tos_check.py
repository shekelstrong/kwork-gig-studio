"""Tool: check_tos — проверка текста кворка на правила Kwork."""

import re
from typing import Literal


# Те же списки что в cover_validate
FORBIDDEN_BRANDS = [
    "VK", "ВК", "Avito", "Авито", "hh.ru", "HeadHunter", "Хедхантер",
    "Ozon", "Озон", "Wildberries", "WB", "Вайлдберриз", "ВБ",
    "2GIS", "2ГИС", "Yandex", "Яндекс", "T-Bank", "Тинькофф", "Tinkoff",
    "QIWI", "Киви", "Beeline", "Билайн", "МТС", "Megafon", "Мегафон",
]

TRIGGER_WORDS = [
    "рилс", "риелс", "Reels", "рилз",
    "сторис", "Stories", "сториз",
    "паблик", "public",
    "SMM", "smm", "СММ",
    "контент-маркетинг",
    "площадка",
]

LIMITS = {
    "title": 70,
    "description": 1200,
    "buyer_needs": 500,
}

# Ниши где бренд ВК пропускают
VK_EXCEPTIONS = [
    "Информационные базы",
    "Парсинг",
    "SMM",
    "VK",
    "ВКонтакте",
]


async def run(
    text: str,
    check_type: Literal["title", "description", "faq", "all"] = "all",
) -> dict:
    """Проверяет текст кворка на правила модерации.

    Args:
        text: Текст для проверки.
        check_type: Тип проверяемого текста.

    Returns:
        Словарь с violations и recommendations.
    """
    violations = []

    # 1. Лимит символов
    limit = LIMITS.get(check_type) if check_type in LIMITS else None
    if limit and len(text) > limit:
        violations.append({
            "type": "length",
            "severity": "high",
            "message": f"Превышен лимит {check_type}: {len(text)} > {limit} символов",
            "fix": f"Сократи до {limit} символов (нужно убрать {len(text) - limit})",
        })

    # 2. Запрещённые бренды
    for brand in FORBIDDEN_BRANDS:
        if brand.lower() in text.lower():
            # Проверяем исключения для ВК
            if brand in ["VK", "ВК", "ВКонтакте"]:
                # ВК пропускают в определённых нишах
                if any(exc.lower() in text.lower() for exc in VK_EXCEPTIONS):
                    continue
            violations.append({
                "type": "brand",
                "severity": "high",
                "message": f"Запрещённый бренд: {brand}",
                "fix": "Убери упоминание бренда или замени на 'мессенджер' / 'площадку' / 'таблицы'",
            })

    # 3. Триггер-слова
    for trigger in TRIGGER_WORDS:
        if trigger.lower() in text.lower():
            violations.append({
                "type": "trigger",
                "severity": "high",
                "message": f"Триггер-слово: {trigger}",
                "fix": "Замени: 'рилс' → 'короткое видео', 'сторис' → 'раздел', 'паблик' → 'канал'",
            })

    # 4. Цены в неположенном месте
    if check_type in ("title", "description"):
        price_patterns = [
            r"\d+\s*₽",  # 5000₽
            r"\d+\s*руб",  # 5000 руб
            r"\d+\s*\$",  # 5000$
            r"\d+\s*€",  # 5000€
        ]
        for pattern in price_patterns:
            if re.search(pattern, text):
                violations.append({
                    "type": "price",
                    "severity": "high",
                    "message": f"Цена в {check_type} (запрещено)",
                    "fix": "Укажи цену в полях цены кворка, не в названии/описании",
                })
                break

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "score": max(0, 1.0 - len(violations) * 0.25),
    }
