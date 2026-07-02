# Kwork Gig Studio

> Единый MCP-сервер для создания и публикации кворков на Kwork. От идеи до публикации за 15 минут.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)
[![GitHub stars](https://img.shields.io/github/stars/shekelstrong/kwork-gig-studio.svg)](https://github.com/shekelstrong/kwork-gig-studio)

**English version:** [README.en.md](README.en.md)

---

## 🎯 Что это

Kwork Gig Studio — это MCP-сервер, который объединяет весь опыт работы с Kwork в один инструмент. Вместо того чтобы держать в голове правила модерации, лимиты символов и приёмы обложки — просто вызываешь нужный tool.

**Все этапы создания кворка в одном пакете:**

- 🔍 **Исследование ниши** — анализ категории, тренды, конкуренты
- 📝 **Генерация текста** — название (≤70 символов), описание (≤1200), FAQ
- 🎨 **Генерация обложки** — через OpenRouter `google/gemini-2.5-flash-image`
- ✅ **Валидация обложки** — vision-чекер на триггер-слова и запрещённые бренды
- 🛡 **Проверка правил Kwork** — модерация, цены, бренды, ToS
- 🚀 **Публикация** — через Playwright (опционально)

---

## 📦 Установка

### Требования

- Python 3.11+
- OpenRouter API key (для генерации обложек и текста)
- Опционально: Playwright + Chromium (для автопубликации)

### Быстрый старт

```bash
# Клонировать
git clone https://github.com/shekelstrong/kwork-gig-studio.git
cd kwork-gig-studio

# Создать venv
python3 -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows

# Поставить зависимости
pip install -r requirements.txt

# Настроить
cp .env.example .env
# Открой .env и вставь OPENROUTER_API_KEY

# Запустить MCP-сервер
python -m mcp.server
```

### Установка как MCP-сервер для Claude / Hermes / Cursor

```json
// В settings.json вашего MCP-клиента:
{
  "mcpServers": {
    "kwork-gig-studio": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/kwork-gig-studio",
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

---

## 🛠 MCP Tools

После подключения в вашем агенте доступны следующие tools:

### 1. `create_gig_draft`

Генерация черновика кворка: название + описание + FAQ.

**Параметры:**
- `niche` (str) — описание ниши (например, "AI-аудит заявок для малого бизнеса")
- `price` (int) — желаемая цена в рублях
- `deadline_days` (int) — срок выполнения
- `target_audience` (str, optional) — кто покупатель

**Возвращает:**
```json
{
  "title": "Проведу ИИ-аудит заявок и найду где теряете деньги за 24ч",
  "description": "...",
  "faq": [
    {"q": "...", "a": "..."}
  ],
  "metadata": {
    "title_length": 65,
    "description_length": 980,
    "ats_score": 0.87
  }
}
```

### 2. `generate_cover`

Генерация обложки через OpenRouter gemini-2.5-flash-image.

**Параметры:**
- `title` (str) — название кворка
- `style` (str) — стиль (по умолчанию `"dark-saas"`, опции: `light`, `gradient`)
- `metrics` (list[str], optional) — метрики для отображения (например, `["24 часа", "5 000₽", "Отчёт в PDF"]`)
- `bullets` (list[str], optional) — 3 буллита для правой панели

**Возвращает:** путь к PNG-файлу (660×440 минимум, генерируется 1024×1024)

### 3. `validate_cover`

Vision-чекер обложки: проверка на триггер-слова, бренды, цену, кириллицу.

**Параметры:**
- `image_path` (str) — путь к PNG
- `strict_mode` (bool) — строгая проверка (по умолчанию `true`)

**Возвращает:**
```json
{
  "ok": false,
  "issues": [
    "Содержит запрещённый бренд: VK",
    "Содержит цену на обложке: 5000₽",
    "Кириллицы < 70%: 45%"
  ],
  "score": 0.62
}
```

### 4. `check_tos`

Проверка текста кворка на соответствие правилам Kwork.

**Параметры:**
- `text` (str) — название, описание или FAQ
- `check_type` (str) — `"title" | "description" | "faq" | "all"`

**Возвращает:** список нарушений с рекомендациями.

### 5. `publish_gig` (опционально)

Автопубликация через Playwright. Требует Kwork-сессию.

**Параметры:**
- `draft` (dict) — черновик из `create_gig_draft`
- `cover_path` (str) — путь к обложке
- `session_file` (str) — путь к сохранённой Playwright-сессии

⚠️ Используйте осторожно — нарушение правил = бан.

---

## 🚀 Использование

### Пример 1: Создание кворка "AI-аудит заявок"

```python
from mcp.server import create_gig_draft, generate_cover, validate_cover, check_tos

# 1. Генерируем черновик
draft = create_gig_draft(
    niche="AI-аудит заявок для интернет-магазинов",
    price=5000,
    deadline_days=1,
    target_audience="Владельцы интернет-магазинов с 50+ заявок/день"
)
print(draft["title"])  # "Проведу ИИ-аудит заявок..."

# 2. Генерируем обложку
cover_path = generate_cover(
    title=draft["title"],
    metrics=["24 часа", "5 000 ₽", "PDF-отчёт"],
    bullets=[
        "Найду узкие места в воронке",
        "Покажу потерянные деньги",
        "Дам план действий"
    ]
)

# 3. Проверяем обложку
result = validate_cover(cover_path)
if not result["ok"]:
    print("Проблемы:", result["issues"])
    # Перегенерировать обложку
```

Полные примеры в [`examples/`](examples/).

### Пример 2: Полный пайплайн (1 команда)

```python
from mcp.server import full_pipeline

result = full_pipeline(
    niche="Телеграм-бот с ИИ для поддержки клиентов",
    price=8000,
    deadline_days=5,
    auto_publish=False  # True = опубликует сам через Playwright
)
print(result["url"])  # https://kwork.ru/...
```

---

## 🎨 Стиль обложки (default: dark-saas)

Все обложки генерируются в едином стиле:

- **Фон:** `#0a0a0a` → `#161616` (radial vignette)
- **Акценты:** mint `#7ee787` + sky `#79c0ff`
- **Шрифт:** Inter / SF Pro Display, perfect Cyrillic
- **Layout:** 50/50 — заголовок + метрики слева, иллюстрация справа
- **Без:** лого Kwork, брендов (VK/Avito/...), цен, триггер-слов

Подробнее: [`references/cover-style.md`](references/cover-style.md).

---

## 🛡 Правила Kwork (жёсткий фильтр модерации)

`check_tos` проверяет **все** известные нам нарушения:

| Категория | Что нельзя |
|---|---|
| **Бренды** | VK, Avito, hh.ru, Ozon, WB, 2GIS, Yandex, T-Bank, QIWI |
| **Персональные данные** | Имена, телефоны, email (юрлица ОК) |
| **Цены** | Цифры с ₽/$/€ в названии/описании |
| **Триггер-слова** | "рилс/Reels", "сторис/Stories", "паблик", "SMM" |
| **Кириллица** | < 70% кириллицы в обложке |
| **Размеры** | Название > 70, описание > 1200, "от покупателя нужно" > 500 |

Исключения: в нишах «Информационные базы», «Парсинг», «SMM» бренд ВК пропускают.

Полный список: [`references/kwork-rules.md`](references/kwork-rules.md).

---

## 📁 Структура репо

```
kwork-gig-studio/
├── README.md                    # Этот файл
├── README.en.md                 # English version
├── LICENSE                      # MIT
├── SKILL.md                     # Hermes-формат
├── requirements.txt
├── .env.example
├── mcp/
│   ├── server.py                # MCP-сервер
│   └── tools/
│       ├── gig_create.py        # create_gig_draft
│       ├── cover_generate.py    # generate_cover
│       ├── cover_validate.py    # validate_cover
│       ├── text_generate.py     # генерация текста
│       ├── tos_check.py         # check_tos
│       └── publish.py           # publish_gig
├── examples/                    # Реальные примеры
├── templates/                   # Шаблоны текста
├── references/                  # Документация
├── scripts/                     # Утилиты
├── tests/                       # Тесты
└── .github/workflows/ci.yml     # CI
```

---

## 🤝 Contributing

PR приветствуются! Особенно:

- Новые правила модерации Kwork (Kwork регулярно их обновляет)
- Новые стили обложки
- Новые шаблоны для популярных ниш
- Улучшения vision-чекера

См. [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 📄 License

MIT © Vasiliy Nedopekin (shekelstrong)

---

## 🙏 Благодарности

- **nousresearch** за [Hermes Agent](https://github.com/nousresearch/hermes-agent)
- **OpenRouter** за унифицированный API к LLM
- **6 опубликованных кворков** на момент создания репо — на них обучены правила
