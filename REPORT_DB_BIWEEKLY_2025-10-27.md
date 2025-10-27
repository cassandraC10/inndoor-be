Bi-Weekly Database Report — 2025-10-27

Period: 2025-10-13 to 2025-10-27
Date prepared: 2025-10-27

1) Summary
- Prepared project to support MySQL (per mentor request) and added DB indexes for performance.
- Installed PyMySQL in the virtual environment and registered it for Django on Windows.
- Generated and applied migrations locally (applied to SQLite during this session as no MySQL `DATABASE_URL` was provided).

2) Changes made
- Models:
  - `users.Property`: added `db_index=True` to `city` and `status` fields.
- Project settings:
  - `inndoor_be/settings.py` updated to parse `DATABASE_URL` environment variable and support both Postgres and MySQL schemes; falls back to SQLite when `DATABASE_URL` is not set.
- Environment example:
  - `.env.example` updated with a MySQL `DATABASE_URL` example.
- DB driver:
  - `PyMySQL` installed and `pymysql.install_as_MySQLdb()` added to `inndoor_be/__init__.py` to allow Django to use PyMySQL as a MySQL driver.

3) Configuration
- Current effective DB for this session: SQLite at `db.sqlite3` (no `DATABASE_URL` was set in the environment when migrations were run).
- To use MySQL, set `DATABASE_URL` in the format:
  - `mysql://<user>:<password>@<host>:<port>/<dbname>`
  - Example (PowerShell):
    $env:DATABASE_URL = "mysql://root:localpassword@localhost:3306/inndoor_db"

4) Packages / Drivers
- Installed `PyMySQL` in the virtual environment (suitable for Windows dev; `mysqlclient` is an alternative native driver).

5) Migration details
- Generated migration: `users/0002_alter_property_city_alter_property_status.py` (adds indexes to `city` and `status`).
- Applied migrations to local DB during this session.

6) Backups & Maintenance
- Not set up in this period. Recommendation: schedule `mysqldump` (for MySQL) or managed DB backups when moving to production.

7) Performance & Indexes
- Added indexes on `Property.city` and `Property.status` to improve filter queries. Consider adding indexes for other high-filter columns (e.g., `price`, `property_type`) as usage patterns become clearer.

8) Next steps / Recommendations
- Provision a MySQL instance (local or managed), create DB and user, then set `DATABASE_URL` and run migrations there.
- For production, consider installing `mysqlclient` on servers for better performance or use `PyMySQL` if compiling native libs is not desired.
- Configure automated backups, retention policy, and monitoring.
- Add unit/integration tests that run migrations and validate model behavior in CI.

9) Risks / Issues
- Linter in the editor flagged unresolved import for `pymysql` (IDE environment mismatch). The package is installed in the project's virtualenv; ignore if migrations run successfully.
- If you plan to use `mysqlclient` in production, you may need to install system-level dependencies (build tools) during deployment.

10) Attachments
- Migration file: `users/migrations/0002_alter_property_city_alter_property_status.py`
- Config changed: `inndoor_be/settings.py`, `inndoor_be/__init__.py`, `.env.example`, `users/models.py`

---
Actions taken during this session (commands run):
- `python manage.py makemigrations users`
- `python manage.py migrate`
- `pip install PyMySQL`

If you'd like, I can now:
- Create the MySQL database and user SQL snippet for local or cloud providers.
- Run migrations against your MySQL instance if you provide `DATABASE_URL` or set it in `.env` and ask me to run them here.
- Create a short git-ready commit message and commit the changes for you, then push to your remote if you'd like me to run that here.
