# Jira MCP

Локальный MCP-сервер для Jira Server/Data Center. Дает Claude и Codex доступ к
задачам, комментариям, вложениям, статусам и переходам, worklog и связям между
задачами.

Сервер работает через Jira REST API v2 и Basic Auth. Токен не нужен.

## Различия ОС

Команды ниже даны в двух вариантах: **Linux/macOS** (bash/zsh) и **Windows**
(PowerShell). Главное отличие — расположение файлов в виртуальном окружении:

|                        | Linux/macOS                 | Windows                          |
|------------------------|-----------------------------|----------------------------------|
| Создать окружение      | `python3 -m venv .venv`     | `python -m venv .venv` или `py -m venv .venv` |
| Python окружения       | `.venv/bin/python`          | `.venv\Scripts\python.exe`       |
| pip окружения          | `.venv/bin/pip`             | `.venv\Scripts\pip.exe`          |
| Перенос строки команды | `\`                         | `` ` `` (обратная кавычка)       |
| Пример абсолютного пути | `/home/me/jira-mcp`        | `C:\Users\me\jira-mcp`           |

В JSON-файлах (Claude Desktop, `.mcp.json`) пути Windows пишите с прямыми
слэшами (`C:/Users/me/jira-mcp/main.py`) или удваивайте обратные
(`C:\\Users\\me\\jira-mcp\\main.py`). В TOML (Codex) используйте строки в
одинарных кавычках: `'C:\Users\me\jira-mcp\main.py'`.

## Установка

Linux/macOS:

```bash
git clone <URL_РЕПОЗИТОРИЯ> jira-mcp
cd jira-mcp

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest -v
```

Windows:

```powershell
git clone <URL_РЕПОЗИТОРИЯ> jira-mcp
cd jira-mcp

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest -v
```

Активировать окружение (`activate`) не нужно: MCP-клиент запускает
`python` из `.venv` по полному пути.

## Настройки

Сервер читает настройки из переменных окружения:

| Переменная         | Обязательна | По умолчанию | Описание                          |
|--------------------|-------------|--------------|-----------------------------------|
| `JIRA_URL`         | да          |              | `http://jira.company.local:8080`  |
| `JIRA_USER`        | да          |              | логин Jira                        |
| `JIRA_PASSWORD`    | да          |              | пароль Jira                       |
| `JIRA_VERIFY_SSL`  | нет         | `true`       | проверять TLS-сертификат          |
| `JIRA_TIMEOUT`     | нет         | `20`         | таймаут запроса, секунды          |
| `JIRA_MAX_RESULTS` | нет         | `50`         | потолок `max_results` в списках   |

Обычно их передает MCP-клиент при подключении сервера: `-e` в
`claude mcp add`, блок `env` в JSON/TOML-конфигурации. Так у каждого проекта
или подключения могут быть свои Jira и учётная запись. Каждое подключение
запускает отдельный процесс сервера со своими значениями. Примеры ниже.

Для запуска без клиента или как общие значения по умолчанию можно создать
`.env` рядом с `main.py`.

Linux/macOS:

```bash
cp .env.example .env
chmod 600 .env
```

Windows:

```powershell
Copy-Item .env.example .env
```

Переменные, переданные клиентом, имеют приоритет над `.env`. Файлы `.env` и
`.env.*` (кроме `.env.example`) находятся в `.gitignore`. Не коммитьте их.

## Claude Code

### Для одного проекта (рекомендуется)

Запустите из каталога **проекта**, в котором нужна Jira. `--scope local`
сохраняет сервер только для этого проекта и только у вас.

Linux/macOS:

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

Windows:

```powershell
$MCP_DIR = "C:\ABSOLUTE\PATH\jira-mcp"

claude mcp add `
  --transport stdio `
  --scope local `
  -e JIRA_URL=http://jira.company.local:8080 `
  -e JIRA_USER=firstname.lastname `
  -e JIRA_PASSWORD=your-password `
  jira -- `
  "$MCP_DIR\.venv\Scripts\python.exe" `
  "$MCP_DIR\main.py"
```

### Общий `.mcp.json` в репозитории проекта

Чтобы подключение было у всей команды (`--scope project`), не записывайте в
`.mcp.json` пароль и пути, зависящие от ОС. Claude Code подставит значения
`${VAR}` из окружения каждого пользователя:

```json
{
  "mcpServers": {
    "jira": {
      "command": "${JIRA_MCP_PYTHON}",
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

Каждый участник один раз задает переменные у себя.

Linux/macOS (добавьте в `~/.bashrc` или `~/.zshrc`):

```bash
export JIRA_MCP_DIR="/ABSOLUTE/PATH/jira-mcp"
export JIRA_MCP_PYTHON="$JIRA_MCP_DIR/.venv/bin/python"
export JIRA_USER="firstname.lastname"
export JIRA_PASSWORD="your-password"
```

Windows (сохраняется для пользователя, действует в новых терминалах):

```powershell
setx JIRA_MCP_DIR "C:/ABSOLUTE/PATH/jira-mcp"
setx JIRA_MCP_PYTHON "C:/ABSOLUTE/PATH/jira-mcp/.venv/Scripts/python.exe"
setx JIRA_USER "firstname.lastname"
setx JIRA_PASSWORD "your-password"
```

После `setx` перезапустите терминал и Claude Code.

### Для всех проектов

Если настройки везде одинаковые, заполните `.env` рядом с `main.py` и
подключите сервер глобально.

Linux/macOS:

```bash
MCP_DIR="/ABSOLUTE/PATH/jira-mcp"

claude mcp add --transport stdio --scope user \
  jira -- "$MCP_DIR/.venv/bin/python" "$MCP_DIR/main.py"
```

Windows:

```powershell
$MCP_DIR = "C:\ABSOLUTE\PATH\jira-mcp"

claude mcp add --transport stdio --scope user `
  jira -- "$MCP_DIR\.venv\Scripts\python.exe" "$MCP_DIR\main.py"
```

Сервер с тем же именем в `local` или `project` перекрывает глобальный.

Проверка (одинаково на всех ОС):

```bash
claude mcp get jira
claude mcp list
```

В новой сессии Claude Code выполните `/mcp`.

## Claude Desktop

Откройте **Settings → Developer → Edit Config**. Откроется файл:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Добавьте сервер.

macOS:

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

Windows:

```json
{
  "mcpServers": {
    "jira": {
      "command": "C:/ABSOLUTE/PATH/jira-mcp/.venv/Scripts/python.exe",
      "args": ["C:/ABSOLUTE/PATH/jira-mcp/main.py"],
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
перезаписывая остальную конфигурацию. После изменения полностью закройте
Claude Desktop (на Windows — также из трея) и откройте снова.

## Codex CLI

Linux/macOS:

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

Windows:

```powershell
$MCP_DIR = "C:\ABSOLUTE\PATH\jira-mcp"

codex mcp add jira `
  --env JIRA_URL=http://jira.company.local:8080 `
  --env JIRA_USER=firstname.lastname `
  --env JIRA_PASSWORD=your-password `
  -- `
  "$MCP_DIR\.venv\Scripts\python.exe" `
  "$MCP_DIR\main.py"
```

Конфигурация Codex общая для всех проектов: `~/.codex/config.toml`
(на Windows — `%USERPROFILE%\.codex\config.toml`). Для разных Jira добавьте
серверы с разными именами (`jira-alpha`, `jira-beta`) и своими `--env`.

Проверка (одинаково на всех ОС):

```bash
codex mcp get jira
codex mcp list
```

В новой сессии Codex выполните `/mcp`.

## Codex Desktop

Codex Desktop, Codex CLI и IDE-расширение используют общий `config.toml`
(путь см. выше). Если сервер уже добавлен через `codex mcp add`, повторная
настройка не нужна: перезапустите приложение.

Также сервер можно добавить через **Settings → MCP servers → Add server**:

- Name: `jira`
- Type: `STDIO`
- Command: абсолютный путь к Python окружения (см. «Различия ОС»)
- Args: абсолютный путь к `main.py`
- переменные окружения `JIRA_URL`, `JIRA_USER`, `JIRA_PASSWORD`

Ручная конфигурация, Linux/macOS:

```toml
[mcp_servers.jira]
command = "/ABSOLUTE/PATH/jira-mcp/.venv/bin/python"
args = ["/ABSOLUTE/PATH/jira-mcp/main.py"]
env = { JIRA_URL = "http://jira.company.local:8080", JIRA_USER = "firstname.lastname", JIRA_PASSWORD = "your-password" }
```

Windows:

```toml
[mcp_servers.jira]
command = 'C:\ABSOLUTE\PATH\jira-mcp\.venv\Scripts\python.exe'
args = ['C:\ABSOLUTE\PATH\jira-mcp\main.py']
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
- статус сервера через `/mcp`;
- что путь к Python указывает на окружение проекта: `.venv/bin/python` на
  Linux/macOS, `.venv\Scripts\python.exe` на Windows.

## Инструменты

| Раздел        | Чтение                                                            | Изменения                                          |
|---------------|-------------------------------------------------------------------|----------------------------------------------------|
| `users`       | `get_myself`, `find_users`, `find_assignable_users`, `get_my_permissions` |                                            |
| `projects`    | `list_projects`, `get_project_issue_types`, `get_create_fields`   |                                                    |
| `statuses`    | `get_project_statuses`, `get_all_statuses`                        |                                                    |
| `reference`   | `get_priorities`, `get_resolutions`, `get_issue_types`            |                                                    |
| `fields`      | `get_fields`                                                      |                                                    |
| `issues`      | `get_ticket`, `search_tickets`, `get_edit_fields`, `get_issue_history` | `create_ticket`, `update_ticket`, `assign_ticket`, `notify_issue` |
| `comments`    | `get_comments`                                                    | `add_comment`, `delete_comment`                    |
| `attachments` | `download_attachment`                                             | `add_attachment`, `delete_attachment`              |
| `transitions` | `list_transitions`                                                | `change_status`                                    |
| `worklogs`    | `get_worklogs`                                                    | `add_worklog`, `update_worklog`, `delete_worklog`  |
| `links`       | `get_link_types`, `get_remote_links`                              | `link_tickets`, `delete_link`, `add_remote_link`, `delete_remote_link` |
| `watchers`    | `get_watchers`                                                    | `add_watcher`, `remove_watcher`                    |
| `filters`     | `list_favourite_filters`, `run_filter`                            |                                                    |
| `boards`      | `list_boards`, `get_board_config`, `get_board_issues`, `get_backlog` | `rank_issues`                                   |
| `sprints`     | `list_sprints`, `get_sprint_issues`                               | `move_to_sprint`, `move_to_backlog`, `create_sprint`, `start_sprint`, `close_sprint` |
| `epics`       | `list_epics`, `get_epic_issues`                                   | `add_to_epic`                                      |
| `versions`    | `list_versions`                                                   | `create_version`, `release_version`                |
| `components`  | `list_components`                                                 | `create_component`                                 |

Перед созданием задачи или сменой статуса агент должен сначала проверить
доступные типы, поля и переходы:

- `get_fields` сопоставляет `customfield_XXXXX` с человеческими именами и
  JQL-именами;
- `get_edit_fields` показывает, какие поля задачи можно менять и какими
  операциями. `update_ticket` принимает `fields` (замена значения) и `update`
  (операции `add`/`remove`/`set`, например добавить метку, не трогая
  остальные);
- `list_transitions` показывает поля экрана перехода. Обязательные поля,
  чаще всего `resolution` при закрытии, передаются в `change_status` через
  `fields`, а комментарий к переходу через `comment`.

Списки (`get_comments`, `get_worklogs`) возвращаются постранично:
`{items, start_at, max_results, total, next_start_at}`. Для следующей
страницы передайте `next_start_at` как `start_at`. `get_issue_history`
показывает, кто, когда и что менял в задаче, с фильтром по полю, например
`field="status"`. Для назначения задачи используйте `find_assignable_users`:
`find_users` находит и тех, на кого назначить нельзя. Если Jira отклонила
действие, `get_my_permissions` покажет, каких прав не хватает.

Доски, спринты и эпики работают через Agile API (`/rest/agile/1.0`, нужен
Jira Software):

- колонка доски и статус — разные вещи. `get_board_config` показывает, какие
  статусы попадают в каждую колонку;
- у канбан-досок нет спринтов и бэклога: `list_sprints` и `get_backlog`
  работают только со скрам-досками, для канбана Jira вернет ошибку;
- групповые операции (`move_to_sprint`, `move_to_backlog`, `add_to_epic`,
  `rank_issues`) принимают до 50 задач за вызов.

Списки досок, спринтов, эпиков и задач на них тоже постраничные, в том же
формате `{items, ..., next_start_at}`.

## Структура

```text
main.py                         # точка входа для MCP-клиентов
src/jira_mcp/
  app.py                        # экземпляр FastMCP
  settings.py                   # настройки из env / .env
  client.py                     # HTTP-сессия Jira и общие хелперы
  formatting.py                 # компактный вид задач в Agile-списках
  server.py                     # регистрация инструментов и запуск
  tools/<раздел>/<команда>.py   # по одному файлу на инструмент
tests/                          # тесты по разделам
```

Сервер также запускается как модуль.

Linux/macOS:

```bash
PYTHONPATH=src .venv/bin/python -m jira_mcp
```

Windows:

```powershell
$env:PYTHONPATH = "src"; .venv\Scripts\python.exe -m jira_mcp
```

Чтобы добавить инструмент:

1. Создайте `src/jira_mcp/tools/<раздел>/<команда>.py` с функцией под
   `@mcp.tool()`. Запросы к Jira делайте через `client.request(...)`:
   - по умолчанию запрос идет в `/rest/api/2`; для досок, спринтов и эпиков
     передайте `api="agile"` (`/rest/agile/1.0`);
   - для списков используйте `client.page(path, items_key, start_at=...,
     max_results=...)`. Он возвращает одну страницу в едином формате
     `{items, start_at, max_results, total, next_start_at}` для обоих API.
     Чтобы получить следующую страницу, передайте `next_start_at` как
     `start_at`; на последней странице он равен `null`.
2. Импортируйте модуль в `src/jira_mcp/tools/<раздел>/__init__.py`. Для нового
   раздела добавьте его в `src/jira_mcp/tools/__init__.py`.
3. Добавьте имя в `EXPECTED_TOOLS` в `tests/test_server.py`, а тест — в
   `tests/test_<раздел>.py`. В тестах подменяйте `jira_mcp.client.request`.

## Обновление

Linux/macOS:

```bash
git pull
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest -v
```

Windows:

```powershell
git pull
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest -v
```

Повторно добавлять MCP не нужно, пока путь к каталогу не изменился.

Если раньше настройки лежали в `config.py`, перенесите значения в `.env` (те
же имена, формат `JIRA_URL=...`) или в `env` подключения MCP. Затем удалите
`config.py`: сервер его больше не читает.

## Ссылки

Документация по клиентам:

- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)
