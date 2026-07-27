import subprocess
import time
import sys
import os

print("Waiting for database to be ready...")
for i in range(30):
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="ludo_legends", user="postgres", password="postgres", host="db", port="5432"
        )
        conn.close()
        print("Database is ready!")
        break
    except Exception:
        print(f"  Waiting... ({i+1}/30)")
        time.sleep(2)
else:
    print("WARNING: Could not verify DB connection, proceeding anyway...")

print("Running Alembic migrations...")
result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Alembic output: {result.stderr.strip()}")
else:
    print("Migrations applied successfully.")

print("Running seed data...")
result = subprocess.run([sys.executable, "-m", "seed"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0 and result.stderr:
    print(f"Seed errors: {result.stderr}")

print("Starting API server...")
os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])
