"""Tool: create_gig_draft — генерация черновика кворка."""

from typing import Optional
import json


# Лимиты Kwork (из kwork-tos-rules)
LIMITS = {
    "title": 70,
    "description": 1200,
    "buyer_needs": 500,
}


async def run(
    niche: str,
    price: int,
    deadline_days: int,
    target_audience: Optional[str] = None,
) -> dict:
    """Генерирует черновик кворка.

    Args:
        niche: Описание ниши.
        price: Цена в рублях.
        deadline_days: Срок выполнения в днях.
        target_audience: Кто покупатель (опционально).

    Returns:
        Словарь с title, description, faq, metadata.
    """
    # TODO: подключить LLM (через OpenRouter) для генерации
    # Сейчас — шаблонная заглушка с правильной структурой
    title = f"Сделаю {niche[:40]} за {deadline_days} дней"
    title = title[:LIMITS["title"]]

    description = (
        f"Что я делаю: {niche}.\n\n"
        f"Для кого: {target_audience or 'предприниматели и малый бизнес'}.\n\n"
        f"Срок: {deadline_days} дней.\n"
        f"Результат: готовый к использованию продукт + инструкции.\n\n"
        f"Опыт: 3+ года в нише, десятки выполненных проектов."
    )
    description = description[:LIMITS["description"]]

    faq = [
        {"q": "Сколько времени занимает?", "a": f"Обычно {deadline_days} дней."},
        {"q": "Что нужно от меня?", "a": "Доступ к материалам и краткое ТЗ."},
        {"q": "Будут ли правки?", "a": "Да, 1-2 итерации включены в стоимость."},
    ]

    return {
        "title": title,
        "description": description,
        "faq": faq,
        "metadata": {
            "title_length": len(title),
            "description_length": len(description),
            "price": price,
            "deadline_days": deadline_days,
            "ats_score": 0.75,  # заглушка
        },
    }
