import psycopg2

DB_CONFIG = {
    "dbname": "hospital_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

FILES = {
    "doctors": "./doctor.csv",
    "patients": "./patients.csv",
    "appointments": "./appointments.csv"
}

def load_csv(table, file_path, conn):
    with conn.cursor() as cur:
        with open(file_path, "r") as f:
            cur.copy_expert(
                sql=f"COPY {table} FROM STDIN WITH CSV HEADER",
                file=f
            )
    conn.commit()
    print(f"Loaded {table}")

def main():
    conn = psycopg2.connect(**DB_CONFIG)

    # FK-safe order
    load_csv("doctors", FILES["doctors"], conn)
    load_csv("patients", FILES["patients"], conn)
    load_csv("appointments", FILES["appointments"], conn)

    conn.close()

if __name__ == "__main__":
    main()
