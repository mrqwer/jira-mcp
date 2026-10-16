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
```

Проверка:

```bash
.venv/bin/python -m unittest -v
```

Команды ниже приведены для Linux/macOS. На Windows используйте
`.venv\Scripts\python.exe` и абсолютные пути.

## Настройки

Сервер читает настройки из переменных окружения:

| Переменная         | Обязательна | По умолчанию | Описание                          |
|--------------------|-------------|--------------|-----------------------------------|
| `JIRA_URL`         | да          |              | `http://jira.company.local:8080`  |
| `JIRA_USER`        | да          |              | логин Jira                        |
| `JIRA_PASSWORD`    | да          |              | пароль Jira                       |
| `JIRA_VERIFY_SSL`  | нет         | `true`       | проверять TLS-сертификат          |
| `JIRA_TIMEOUT`     | нет         | `20`         | таймаут запроса, секунды          |
| `JIRA_MAX_RESULTS` | нет         | `50`         | максимум результатов поиска       |

Обычно их передает MCP-клиент при подключении сервера: `-e` в
`claude mcp add`, блок `env` в JSON/TOML-конфигурации. Так у каждого проекта
или подключения могут быть свои Jira и учётная запись. Примеры ниже.

Для запуска без клиента или как общие значения по умолчанию можно создать
`.env` рядом с `main.py`:

```bash
cp .env.example .env
chmod 600 .env
```

Переменные, переданные клиентом, имеют приоритет над `.env`. Файлы `.env` и
`.env.*` (кроме `.env.example`) находятся в `.gitignore`. Не коммитьте их.

## Claude Code

### Для одного проекта (рекомендуется)

Запустите из каталога **проекта**, в котором нужна Jira. `--scope local`
сохраняет сервер только для этого проекта и только у вас:

```bash
MCP_DIR="/ABSOLUTE/PATH/jira-mcp"

claude mcp add \
  --transport stdio \
  --scope local \
  -e JIRA_URL=http://jira.company.local:8080 \
  -e JIRA_USER=firstname.lastname \
  -e JIRA_PASSWORD=your-password \
  jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

### Общий `.mcp.json` в репозитории проекта

Чтобы подключение было у всей команды (`--scope project`), не записывайте в
`.mcp.json` пароль. Claude Code подставит значения `${VAR}` из окружения
каждого пользователя:

```json
{
  "mcpServers": {
    "jira": {
      "command": "${JIRA_MCP_DIR}/.venv/bin/python",
      "args": ["${JIRA_MCP_DIR}/main.py"],
      "env": {
        "JIRA_URL": "http://jira.company.local:8080",
        "JIRA_USER": "${JIRA_USER}",
        "JIRA_PASSWORD": "${JIRA_PASSWORD}"
      }
    }
  }
}
```

### Для всех проектов

Если настройки везде одинаковые, заполните `.env` рядом с `main.py` и
подключите сервер глобально:

```bash
MCP_DIR="/ABSOLUTE/PATH/jira-mcp"

claude mcp add \
  --transport stdio \
  --scope user \
  jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

Сервер с тем же именем в `local` или `project` перекрывает глобальный.

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
      "args": ["/ABSOLUTE/PATH/jira-mcp/main.py"],
      "env": {
        "JIRA_URL": "http://jira.company.local:8080",
        "JIRA_USER": "firstname.lastname",
        "JIRA_PASSWORD": "your-password"
      }
    }
  }
}
```

Блок `env` можно не указывать, если заполнен `.env` рядом с `main.py`. Для
нескольких Jira добавьте несколько серверов с разными именами (`jira-alpha`,
`jira-beta`) и своим `env`.

Если в файле уже есть другие серверы, добавьте только нужную секцию, не
перезаписывая остальную конфигурацию. После изменения полностью перезапустите
Claude Desktop.

## Codex CLI

```bash
MCP_DIR="/ABSOLUTE/PATH/jira-mcp"

codex mcp add jira \
  --env JIRA_URL=http://jira.company.local:8080 \
  --env JIRA_USER=firstname.lastname \
  --env JIRA_PASSWORD=your-password \
  -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

Конфигурация Codex общая для всех проектов (`~/.codex/config.toml`). Для
разных Jira добавьте серверы с разными именами (`jira-alpha`, `jira-beta`) и
своими `--env`.

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
- переменные окружения `JIRA_URL`, `JIRA_USER`, `JIRA_PASSWORD`

Ручная конфигурация выглядит так:

```toml
[mcp_servers.jira]
command = "/ABSOLUTE/PATH/jira-mcp/.venv/bin/python"
args = ["/ABSOLUTE/PATH/jira-mcp/main.py"]
env = { JIRA_URL = "http://jira.company.local:8080", JIRA_USER = "firstname.lastname", JIRA_PASSWORD = "your-password" }
```

## Проверка Jira

После подключения попросите агента:

```text
Покажи текущего пользователя Jira и доступные проекты.
```

Если MCP подключен, но Jira не отвечает, проверьте:

- доступ к внутренней сети или VPN;
- `JIRA_URL`, логин и пароль в `env` подключения MCP или в `.env`;
- права пользователя в нужном проекте;
- статус сервера через `/mcp`.

## Инструменты

| Раздел        | Чтение                                                            | Изменения                                          |
|---------------|-------------------------------------------------------------------|----------------------------------------------------|
| `users`       | `get_myself`, `find_users`                                        |                                                    |
| `projects`    | `list_projects`, `get_project_issue_types`, `get_create_fields`   |                                                    |
| `statuses`    | `get_project_statuses`, `get_all_statuses`                        |                                                    |
| `issues`      | `get_ticket`, `search_tickets`                                    | `create_ticket`, `update_ticket`, `assign_ticket`  |
| `comments`    |                                                                   | `add_comment`, `delete_comment`                    |
| `attachments` | `download_attachment`                                             | `add_attachment`, `delete_attachment`              |
| `transitions` | `list_transitions`                                                | `change_status`                                    |
| `worklogs`    |                                                                   | `add_worklog`                                      |
| `links`       | `get_link_types`, `get_remote_links`                              | `link_tickets`, `delete_link`                      |

Перед созданием задачи или сменой статуса агент должен сначала проверить
доступные типы, поля и переходы.

## Структура

```text
main.py                         # точка входа для MCP-клиентов
src/jira_mcp/
  app.py                        # экземпляр FastMCP
  config.py                     # настройки из env / .env
  client.py                     # HTTP-сессия Jira и общие хелперы
  server.py                     # регистрация инструментов и запуск
  tools/<раздел>/<команда>.py   # по одному файлу на инструмент
tests/                          # тесты по разделам
```

Сервер также запускается как модуль: `PYTHONPATH=src python -m jira_mcp`.

Чтобы добавить инструмент:

1. Создайте `src/jira_mcp/tools/<раздел>/<команда>.py` с функцией под
   `@mcp.tool()`. Запросы к Jira делайте через `client.request(...)`.
2. Импортируйте модуль в `src/jira_mcp/tools/<раздел>/__init__.py`. Для нового
   раздела добавьте его в `src/jira_mcp/tools/__init__.py`.
3. Добавьте имя в `EXPECTED_TOOLS` в `tests/test_server.py`, а тест — в
   `tests/test_<раздел>.py`. В тестах подменяйте `jira_mcp.client.request`.

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
