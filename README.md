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
cp .env.example .env
chmod 600 .env
```

Заполните `.env`:

```dotenv
JIRA_URL=http://jira.company.local:8080
JIRA_USER=firstname.lastname
JIRA_PASSWORD=your-password
```

Необязательные параметры: `JIRA_VERIFY_SSL` (по умолчанию `true`),
`JIRA_TIMEOUT` (секунды, `20`), `JIRA_MAX_RESULTS` (`50`).

Файлы `.env` и `.env.*` (кроме `.env.example`) находятся в `.gitignore`. Не
коммитьте их.

## Настройки для каждого проекта

Сервер ищет настройки в таком порядке:

1. Переменные окружения процесса. Например, блок `env` в конфигурации
   MCP-клиента. Они всегда имеют приоритет над файлом.
2. Файл из аргумента `--env-file /path/to/file`.
3. Файл из переменной `JIRA_ENV_FILE`.
4. `.env` рядом с `main.py`, если ничего из перечисленного не задано.

Если файл указан явно, но не найден, сервер не запустится. Указывайте
абсолютные пути: каталог, из которого клиент запускает сервер, зависит от
клиента.

Поэтому одну установку `jira-mcp` можно подключить к разным проектам с
разными Jira или учётными записями. Положите в каждый проект свой файл,
например `<проект>/.env.jira` (добавьте его в `.gitignore` проекта), и
передайте его через `--env-file` при подключении MCP. Примеры ниже.

Проверка:

```bash
.venv/bin/python -m unittest -v
```

Команды ниже приведены для Linux/macOS. На Windows используйте
`.venv\Scripts\python.exe` и абсолютные пути.

## Claude Code

### Для одного проекта (рекомендуется)

Запустите из каталога **проекта**, в котором нужна Jira. `--scope local`
сохраняет сервер только для этого проекта и только у вас, а не глобально:

```bash
MCP_DIR="/ABSOLUTE/PATH/jira-mcp"

claude mcp add \
  --transport stdio \
  --scope local \
  jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py" \
  --env-file "$(pwd)/.env.jira"
```

Вместо файла можно передать переменные напрямую:

```bash
claude mcp add --transport stdio --scope local \
  -e JIRA_URL=http://jira.company.local:8080 \
  -e JIRA_USER=firstname.lastname \
  -e JIRA_PASSWORD=your-password \
  jira -- "$MCP_DIR/.venv/bin/python" "$MCP_DIR/main.py"
```

Для общего `.mcp.json` в репозитории проекта (`--scope project`) не
записывайте пароль в сам файл. Оставьте там только `--env-file`, а секреты
держите в неотслеживаемом `.env.jira`.

### Для всех проектов

Чтобы подключить сервер глобально с `.env` рядом с `main.py`, запустите из
каталога `jira-mcp`:

```bash
MCP_DIR="$(pwd)"

claude mcp add \
  --transport stdio \
  --scope user \
  jira -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py"
```

Настройка `local` или `project` для конкретного проекта перекрывает
глобальную, если у них одинаковое имя.

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
        "/ABSOLUTE/PATH/jira-mcp/main.py",
        "--env-file",
        "/ABSOLUTE/PATH/project/.env.jira"
      ]
    }
  }
}
```

Пара `--env-file` необязательна: без неё используется `.env` рядом с
`main.py`. В Claude Desktop нет проектов. Чтобы работать с несколькими Jira,
добавьте несколько серверов с разными именами (`jira-alpha`, `jira-beta`) и
разными `--env-file`. Вместо файла можно указать блок `"env": {"JIRA_URL": ...}`.

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

Конфигурация Codex общая для всех проектов (`~/.codex/config.toml`). Чтобы
у разных проектов были разные настройки, добавьте отдельный сервер на каждый
проект со своим файлом:

```bash
codex mcp add jira-alpha -- \
  "$MCP_DIR/.venv/bin/python" \
  "$MCP_DIR/main.py" \
  --env-file /ABSOLUTE/PATH/alpha/.env.jira
```

Можно также передать переменные через `--env JIRA_URL=...`.

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
args = ["/ABSOLUTE/PATH/jira-mcp/main.py", "--env-file", "/ABSOLUTE/PATH/project/.env.jira"]

# или переменные напрямую:
# env = { JIRA_URL = "http://jira.company.local:8080", JIRA_USER = "firstname.lastname", JIRA_PASSWORD = "your-password" }
```

## Проверка Jira

После подключения попросите агента:

```text
Покажи текущего пользователя Jira и доступные проекты.
```

Если MCP подключен, но Jira не отвечает, проверьте:

- доступ к внутренней сети или VPN;
- `JIRA_URL`, логин и пароль в `.env` (или в файле из `--env-file`);
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
- `download_attachment`
- `list_transitions`
- `get_link_types`
- `get_remote_links`

Изменения:

- `create_ticket`
- `update_ticket`
- `assign_ticket`
- `add_comment`
- `delete_comment`
- `add_attachment`
- `delete_attachment`
- `change_status`
- `add_worklog`
- `link_tickets`
- `delete_link`

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
