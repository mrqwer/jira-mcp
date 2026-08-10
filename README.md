# Jira MCP

Локальный MCP-сервер для Jira Server/Data Center. Дает Claude и Codex доступ к
задачам, комментариям, переходам, worklog и связям между задачами.

Сервер работает через Jira REST API v2 и Basic Auth. Токен не нужен.

## Установка

```bash
git clone <URL_РЕПОЗИТОРИЯ> jira-mcp
cd jira-mcp

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.example.py config.py
chmod 600 config.py
```

Заполните `config.py`:

```python
JIRA_URL = "http://jira.company.local:8080"
JIRA_USER = "firstname.lastname"
JIRA_PASSWORD = "your-password"
```

`config.py` находится в `.gitignore`. Не коммитьте его.

Проверка:

```bash
.venv/bin/python -m unittest -v
```

Команды ниже приведены для Linux/macOS. На Windows используйте
`.venv\Scripts\python.exe` и абсолютные пути.

## Claude Code

Запустите из каталога `jira-mcp`:

```bash
MCP_DIR="$(pwd)"

claude mcp add \
  --transport stdio \
  --scope user \
  jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

Проверка:

```bash
claude mcp get jira
claude mcp list
```

В новой сессии Claude Code выполните `/mcp`.

## Claude Desktop

Откройте **Settings → Developer → Edit Config** и добавьте сервер:

```json
{
  "mcpServers": {
    "jira": {
      "command": "/ABSOLUTE/PATH/jira-mcp/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/jira-mcp/main.py"
      ]
    }
  }
}
```

Если в файле уже есть другие серверы, добавьте только секцию `jira`, не
перезаписывая остальную конфигурацию. После изменения полностью перезапустите
Claude Desktop.

## Codex CLI

Запустите из каталога `jira-mcp`:

```bash
MCP_DIR="$(pwd)"

codex mcp add jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

Проверка:

```bash
codex mcp get jira
codex mcp list
```

В новой сессии Codex выполните `/mcp`.

## Codex Desktop

Codex Desktop, Codex CLI и IDE-расширение используют общий
`~/.codex/config.toml`. Если сервер уже добавлен через `codex mcp add`, повторная
настройка не нужна: перезапустите приложение.

Также сервер можно добавить через **Settings → MCP servers → Add server**:

- Name: `jira`
- Type: `STDIO`
- Command: абсолютный путь к `.venv/bin/python`
- Args: абсолютный путь к `main.py`

Ручная конфигурация выглядит так:

```toml
[mcp_servers.jira]
command = "/ABSOLUTE/PATH/jira-mcp/.venv/bin/python"
args = ["/ABSOLUTE/PATH/jira-mcp/main.py"]
```

## Проверка Jira

После подключения попросите агента:

```text
Покажи текущего пользователя Jira и доступные проекты.
```

Если MCP подключен, но Jira не отвечает, проверьте:

- доступ к внутренней сети или VPN;
- `JIRA_URL`, логин и пароль в `config.py`;
- права пользователя в нужном проекте;
- статус сервера через `/mcp`.

## Инструменты

Чтение:

- `get_myself`
- `list_projects`
- `get_ticket`
- `search_tickets`
- `get_project_issue_types`
- `get_create_fields`
- `find_users`
- `list_transitions`
- `get_link_types`
- `get_remote_links`

Изменения:

- `create_ticket`
- `update_ticket`
- `assign_ticket`
- `add_comment`
- `change_status`
- `add_worklog`
- `link_tickets`

Перед созданием задачи или сменой статуса агент должен сначала проверить
доступные типы, поля и переходы.

## Обновление

```bash
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest -v
```

Повторно добавлять MCP не нужно, пока путь к каталогу не изменился.

## Развитие

Документация по клиентам:

- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)
