#!/usr/bin/env python3
"""
Kwork Gig Studio MCP Server.

Единый MCP-сервер для создания и публикации кворков на Kwork.
Запуск: python -m mcp.server
"""

import asyncio
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Импортируем наши tools (локальный пакет kwork_mcp, не путать с mcp SDK)
from kwork_mcp.tools import (
    gig_create,
    cover_generate,
    cover_validate,
    tos_check,
    publish,
)


app = Server("kwork-gig-studio")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Список всех доступных tools."""
    return [
        Tool(
            name="create_gig_draft",
            description="Генерация черновика кворка: название + описание + FAQ. "
                        "Учитывает лимиты Kwork (70/1200/500 символов).",
            inputSchema={
                "type": "object",
                "properties": {
                    "niche": {"type": "string", "description": "Описание ниши"},
                    "price": {"type": "integer", "description": "Цена в рублях"},
                    "deadline_days": {"type": "integer", "description": "Срок в днях"},
                    "target_audience": {"type": "string", "description": "Кто покупатель (опц.)"},
                },
                "required": ["niche", "price", "deadline_days"],
            },
        ),
        Tool(
            name="generate_cover",
            description="Генерация обложки кворка через OpenRouter gemini-2.5-flash-image. "
                        "Стиль dark-saas по умолчанию. Возвращает путь к PNG 1024x1024.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "style": {"type": "string", "enum": ["dark-saas", "light", "gradient"]},
                    "metrics": {"type": "array", "items": {"type": "string"}},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="validate_cover",
            description="Vision-чекер обложки: проверка на бренды, цены, "
                        "триггер-слова, кириллицу (< 70% = бан).",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"},
                    "strict_mode": {"type": "boolean", "default": True},
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="check_tos",
            description="Проверка текста кворка на соответствие правилам Kwork. "
                        "Бренды, цены, триггер-слова, лимиты символов.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "check_type": {"type": "string", "enum": ["title", "description", "faq", "all"]},
                },
                "required": ["text", "check_type"],
            },
        ),
        Tool(
            name="publish_gig",
            description="⚠️ Автопубликация через Playwright. Используйте осторожно. "
                        "Требует Kwork-сессию (cookies).",
            inputSchema={
                "type": "object",
                "properties": {
                    "draft": {"type": "object"},
                    "cover_path": {"type": "string"},
                    "session_file": {"type": "string"},
                    "dry_run": {"type": "boolean", "default": True},
                },
                "required": ["draft", "cover_path", "session_file"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Диспетчер вызовов tools."""
    try:
        if name == "create_gig_draft":
            result = await gig_create.run(**arguments)
        elif name == "generate_cover":
            result = await cover_generate.run(**arguments)
        elif name == "validate_cover":
            result = await cover_validate.run(**arguments)
        elif name == "check_tos":
            result = await tos_check.run(**arguments)
        elif name == "publish_gig":
            result = await publish.run(**arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        import json
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def main():
    """Запуск MCP-сервера через stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())