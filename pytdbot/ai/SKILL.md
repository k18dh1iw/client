---
name: pytdbot
description: >
    Write Telegram bots and userbots with Pytdbot (async TDLib Python client).
    Use when the user works with Pytdbot, TDLib, or pytdbot.Client.
---

# Pytdbot

Async [TDLib](https://github.com/tdlib/td) wrapper for Telegram users/bots in Python. It is not the HTTP Bot API — use Pytdbot/TDLib names and types only.

## `python -m pytdbot.docs` (use this for the API)

Before calling an unfamiliar method or building a type, run the docs CLI. It searches the installed library and prints parameters, types, and descriptions.

| Command             | When to use                                  | Example                                          |
| ------------------- | -------------------------------------------- | ------------------------------------------------ |
| `search <query>`    | Find symbols by keyword                      | `python -m pytdbot.docs search "send photo"`     |
| `function <name>`   | Full TDLib method signature                  | `python -m pytdbot.docs function sendMessage`    |
| `type <name>`       | Fields of a TDLib type                       | `python -m pytdbot.docs type message`            |
| `class <name>`      | Abstract class → concrete types              | `python -m pytdbot.docs class InputFile`         |
| `update <name>`     | Update payload shape                         | `python -m pytdbot.docs update updateNewMessage` |
| `helper [name]`     | Pytdbot bound methods, Client helpers, utils | `python -m pytdbot.docs helper reply_text`       |
| `helper -q <query>` | Search helpers only                          | `python -m pytdbot.docs helper -q escape`        |
| `stats`             | Counts / TDLib version                       | `python -m pytdbot.docs stats`                   |

Workflow: `search` → pick a name → `function` / `type` / `class` / `helper` for full detail.  
Flags: `--json` for machine-readable output; `search --kind function` (or `type`, `class`, `update`, `helper`) to narrow results.  
Also available as `pytdbot-docs` after install. Same commands either way.

## Preference order

1. Bound methods — `message.reply_text`, `message.reply_photo`, `message.text`, …
2. Client helpers — `sendTextMessage`, `sendPhoto`, `sendAlbum`, `parseText`, …
3. `pytdbot.utils` — formatting, callback data, escapes, …
4. TDLib methods on `Client` — `sendMessage`, `getChat`, … (camelCase)

## Basic bot

```python
import asyncio
from pytdbot import Client, types

client = Client(
    token="BOT_TOKEN",
    api_id=0,
    api_hash="API_HASH",
    files_directory="BotDB",
    database_encryption_key="change-me",
)

@client.on_message()
async def on_msg(c: Client, message: types.Message):
    if message.text:
        await message.reply_text(message.text)

asyncio.run(client.run())
```

Userbot: `user_bot=True` (no token) and handle authorization — see `examples/userbot.py`.

## Handlers

- `async def handler(client, update_or_message)`
- `@client.on_message()` → `types.Message`
- `@client.on_updateNewMessage()` / other `on_update…` → full update
- Filters: `from pytdbot import filters` → `filters.create(...)` then `@client.on_message(filters=my_filter)`

## Common patterns

```python
@client.on_message()
async def echo(c: Client, message: types.Message):
    if isinstance(message.content, types.MessageText):
        await message.reply_text(message.text, entities=message.entities)
    elif isinstance(message.content, types.MessagePhoto):
        await message.reply_photo(message.remote_file_id, caption=message.caption)
```

Parse mode on helpers: `"html"`, `"markdown"`, `"markdownv2"` (or `default_parse_mode=` on `Client`).

```python
await message.reply_text("<b>hi</b>", parse_mode="html")
```

Inline keyboard + callback (with `utils.callback_data`):

```python
from pytdbot import utils

await message.reply_text(
    "Pick",
    reply_markup=types.ReplyMarkupInlineKeyboard(
        rows=[[
            types.InlineKeyboardButton(
                text="OK",
                type=types.InlineKeyboardButtonTypeCallback(
                    data=utils.callback_data("ok", {"id": 1})
                ),
            ),
        ]]
    ),
)

@client.on_updateNewCallbackQuery()
async def on_cb(c: Client, update: types.UpdateNewCallbackQuery):
    cb = utils.load_callback_data(update.payload.data)
    # cb.action, cb.data
    await update.answer(text="done")
```

```python
async with message.action("typing"):
    await asyncio.sleep(1)
    await message.reply_text("Done")
```

```python
await client.sendPhoto(chat_id, photo="path_or_remote_id", caption="Hi", parse_mode="html")
```

Raw TDLib: look up with `function` / `type` first, then call; build objects with `types.*`.

```python
chat = await client.getChat(chat_id=chat_id)
if not chat:  # Error is falsy; success types are truthy
    return
# use chat...
```

## `pytdbot.utils`

Import: `from pytdbot import utils` (or `from pytdbot.utils import bold, escape_html, …`).  
Signatures: `python -m pytdbot.docs helper bold` / `helper -q webapp`.

- **Text format** (HTML by default; MarkdownV2 with `html=False`): `bold`, `italic`, `underline`, `strikethrough`, `spoiler`, `code`, `pre`, `pre_code`, `hyperlink`, `mention`, `custom_emoji`, `quote`, `rtl`, `ltr`
- **Escape**: `escape_html`, `escape_markdown`
- **Callback buttons**: `callback_data(action, data=None)` → `bytes` (max 64); `load_callback_data(data)` → `.action` / `.data`
- **Mini Apps (Web App)**: `create_webapp_secret_key(bot_token)` → secret; `parse_webapp_data(secret_key, init_data, max_data_age=60)` → validated `dict` (raises `WebAppDataInvalid` / `WebAppDataOutdated` / `WebAppDataMismatch` from `pytdbot.exception`)
- **Flood / retry**: `get_retry_after_time(error_message)`
- **Other**: `get_bot_id_from_token`, `get_message_sender_id`
- **Rich messages**: builders (`paragraph`, `heading`, `image`, …) and `rich_message_to_html` for rich / `sendRichMessage` flows

```python
from pytdbot import utils

text = f"Hello {utils.bold(name)} — {utils.hyperlink('site', url)}"
await message.reply_text(text, parse_mode="html")

# Mini App initData validation
secret = utils.create_webapp_secret_key(bot_token)
data = utils.parse_webapp_data(secret, init_data)
```

## Plugins

Split handlers into modules under a folder; pass `types.Plugins` into `Client`.

```python
from pytdbot import Client, types

client = Client(
    token="BOT_TOKEN",
    api_id=0,
    api_hash="API_HASH",
    files_directory="BotDB",
    database_encryption_key="change-me",
    plugins=types.Plugins(
        folder="plugins/",
        # optional: only these modules (dotted path = folder + file)
        # include=["plugins.rules", "plugins.admin.ban"],
        # optional: skip modules
        # exclude=["plugins.experimental"],
    ),
)
```

**`Plugins`**

| Arg       | Meaning                                                                                    |
| --------- | ------------------------------------------------------------------------------------------ |
| `folder`  | Directory to scan for `*.py` (recursive)                                                   |
| `include` | If set, only load modules whose path matches (e.g. `plugins.rules` for `plugins/rules.py`) |
| `exclude` | If set (and no `include`), skip these module paths                                         |

**Plugin module** (`plugins/ping.py`) — decorate with `Client.…` (no client instance); those handlers are picked up when the client starts with `plugins=…`:

```python
from pytdbot import Client, types, filters

private = filters.create(lambda _, m: m.chat_id > 0)

@Client.on_message(filters=private)
async def ping(c: Client, message: types.Message):
    if message.text == "/ping":
        await message.reply_text("pong")

@Client.on_updateNewCallbackQuery()
async def on_cb(c: Client, update: types.UpdateNewCallbackQuery):
    await update.answer(text="ok")
```

Same decorator API as on a live client: `on_message`, `on_updateNewMessage`, `on_updateNewCallbackQuery`, `initializer`, `finalizer`, other `on_update…`, plus `filters=`, `position=`, `timeout=`. Handlers must be `async`.

**Runtime**

- Loaded when `Client` is constructed with `plugins=…` (folder must be importable; usually run from project root so `plugins.*` imports work).
- `client.reload_plugins()` — reloads plugin modules (**dev only**, not for production). Handlers registered on the client instance itself are left alone.
- `client.remove_handler(func)` — remove a specific handler function.

## Details

- Types: `from pytdbot import Client, types` → `types.SomeType(...)`.
- Bots: `token=`; userbots: `user_bot=True` + authorization updates.
- `files_directory` + `database_encryption_key` required; one live client per directory.
