"""Tool: publish_gig — автопубликация через Playwright.

⚠️ ОПАСНЫЙ TOOL. Только для опытных пользователей.
Нарушение правил = бан аккаунта.
"""

import os
from pathlib import Path
from typing import Optional


async def run(
    draft: dict,
    cover_path: str,
    session_file: str,
    dry_run: bool = True,
) -> dict:
    """Публикует кворк через Playwright.

    Args:
        draft: Черновик из create_gig_draft.
        cover_path: Путь к обложке PNG.
        session_file: Путь к .pkl с cookies Kwork.
        dry_run: True = только проверяет что можно, не публикует.

    Returns:
        Словарь с status и (если опубликовано) url.
    """
    # Проверки
    if not os.path.exists(cover_path):
        return {"status": "error", "error": f"Обложка не найдена: {cover_path}"}

    if not os.path.exists(session_file):
        return {
            "status": "error",
            "error": f"Session-файл не найден: {session_file}. "
                    "Сначала залогинься в Kwork через Playwright и сохрани cookies.",
        }

    if dry_run:
        return {
            "status": "dry_run_ok",
            "would_publish": {
                "title": draft.get("title"),
                "price": draft.get("metadata", {}).get("price"),
                "cover": cover_path,
            },
            "next_step": "Чтобы реально опубликовать, вызови с dry_run=False",
        }

    # Реальная публикация — TODO
    return {
        "status": "not_implemented",
        "error": "Реальная публикация не реализована. "
                "Используй Playwright вручную или расширь этот tool.",
    }
