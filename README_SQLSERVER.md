## Подключение SQL Server Express (SSMS)

Проект уже работает с SQLite (файл `db.sqlite3`). Ниже — как переключиться на SQL Server Express.

> Примечание по совместимости: `mssql-django 1.6` требует Django ветки **< 5.3**.
> Поэтому в `requirements.txt` закреплён Django **5.2.x**.

### 1) Создай базу данных в SSMS

- Подключись к серверу `.\SQLEXPRESS`
- Создай БД, например `info_flow`

### 2) Установи драйвер ODBC

Нужен Microsoft ODBC Driver:
- **ODBC Driver 18 for SQL Server** (рекомендуется) или
- ODBC Driver 17 for SQL Server

Проверка наличия драйвера (PowerShell):

```powershell
Get-OdbcDriver -Name "*SQL Server*" | Select-Object Name
```

### 3) Установи Python-зависимости

```powershell
cd "d:\Рабочий стол\info_flow"
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4) Задай переменные окружения (быстрый способ)

В этом же окне PowerShell:

```powershell
$env:DB_ENGINE="mssql"
$env:MSSQL_HOST=".\SQLEXPRESS"
$env:MSSQL_NAME="info_flow"
$env:MSSQL_DRIVER="ODBC Driver 18 for SQL Server"
$env:MSSQL_EXTRA_PARAMS="TrustServerCertificate=yes"
```

Если у тебя **SQL логин** (не Windows Auth), добавь:

```powershell
$env:MSSQL_USER="your_user"
$env:MSSQL_PASSWORD="your_password"
```

### 5) Выполни миграции уже в SQL Server

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Примечания

- Если используется Windows Authentication, обычно `MSSQL_USER`/`MSSQL_PASSWORD` можно не задавать.
- Если с Driver 18 будут проблемы с сертификатом, параметр `TrustServerCertificate=yes` это решает для локальной разработки.

