# BizBuddy AI — Persistent Database + Modern Login

This updated package adds:
- A redesigned, responsive sign-in page. It shows blank username/password fields, not the credentials themselves.
- PostgreSQL support through `DATABASE_URL` for persistent hosted data.
- SQLite fallback for local development.
- Password hashing in the users table.
- Dashboard, CSV uploads, alerts, mode selector, and basic sales anomaly detection.

## 1. Local run
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

Local default account:
- Username: `admin`
- Password: `BizBuddy@2026`

Change these before public use by setting `ADMIN_USERNAME` and `ADMIN_PASSWORD`.

## 2. Connect persistent database on Render
Important: Render Free web services have ephemeral filesystems, so SQLite data disappears after restarts/redeploys/spin-downs. Use Render Postgres instead.

1. In Render Dashboard, select **New + → PostgreSQL**.
2. Create a database in the same region as the BizBuddy web service.
3. Copy its **Internal Database URL** (use the internal URL when the app and database are in the same Render region).
4. Open your `bizbuddy-ai` web service → **Environment**.
5. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: paste the database's Internal Database URL
6. Add/update these environment variables:
   - `SECRET_KEY` = a long random secret value
   - `ADMIN_USERNAME` = your chosen login username
   - `ADMIN_PASSWORD` = a strong password
7. Save changes and redeploy.

Render Free Postgres currently expires after 30 days, so for data that must remain available beyond that period, use a paid database plan or another durable managed database. The database connection makes the app persistent, but it does not automatically migrate data from the old SQLite file. Upload your CSVs again after connecting the database.

## 3. Update the GitHub repository
Replace the repository's `app.py`, `requirements.txt`, and `README.md` with the files in this ZIP, then commit the changes. Render should redeploy automatically if auto-deploy is enabled.

## CSV columns
- Sales: `date,product,quantity,price`
- Expenses: `date,category,amount`
- Inventory: `product,stock,reorder_level`

Each new upload replaces the existing dataset for that type. This is a student-project prototype; do not upload sensitive real business data.
