# BizBuddy AI — Multi-Business Accounts

- Business registration with business name, unique username and password.
- Each business has isolated sales, expenses and inventory records.
- Dashboard calculations, forecasts, anomaly detection and alerts use only the signed-in account's data.
- CSV uploads replace only that account's dataset of the selected type.
- Passwords are hashed.
- Existing records in an upgraded database are assigned to the existing admin account during schema migration.

## Deploy
1. Replace `app.py`, `requirements.txt`, and `README.md` in GitHub with these files and commit.
2. Wait for Render to deploy the latest commit.
3. Configure `DATABASE_URL` to point to a persistent PostgreSQL database on Render.
4. Set a long random `SECRET_KEY` and strong `ADMIN_USERNAME` / `ADMIN_PASSWORD`.
5. If switching from SQLite to PostgreSQL, upload CSVs again; SQLite data is not automatically copied to PostgreSQL.
6. Open the site and choose **Create an account** for each business.

Default admin login only if environment variables have not changed:
- Username: `admin`
- Password: `BizBuddy@2026`

CSV formats:
- Sales: `date,product,quantity,price`
- Expenses: `date,category,amount`
- Inventory: `product,stock,reorder_level`

This is a student-project prototype. Test with two separate accounts before using real business data.
