import psycopg2

# Database connection parameters
db_params = {
    'dbname': 'webscraper_dev_db',
    'user': 'dev',
    'password': 'Pineapple123!',
    'host': 'localhost',
    'port': '5432'
}

# Path to your referrers file
referers_file_path = 'referers.txt'

# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to create the referers table
def create_referers_table(conn):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS referers (
        id SERIAL PRIMARY KEY,
        referer TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_referer ON referers (referer);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        print("Referers table creation successful.")
    except Exception as e:
        print(f"Error creating referers table: {e}")
        conn.rollback()

# Function to insert referrers into the table
def insert_referers(conn, referers):
    insert_query = """
    INSERT INTO referers (referer)
    VALUES (%s)
    """
    try:
        cursor = conn.cursor()
        for referer in referers:
            print(f"Inserting referer: {referer}")
            cursor.execute(insert_query, (referer,))
        conn.commit()
        cursor.close()
        print("Referers insertion successful.")
    except Exception as e:
        print(f"Error inserting referers: {e}")
        conn.rollback()

# Main function
def main():
    # Read referrers file
    try:
        with open(referers_file_path, 'r') as file:
            referers = [line.strip() for line in file.readlines()]
        print("Referers file reading successful. Data:")
        for referer in referers:
            print(referer)
    except Exception as e:
        print(f"Error reading referers file: {e}")
        return

    # Connect to the database
    conn = connect_to_db()
    if not conn:
        return

    try:
        # Create referers table
        create_referers_table(conn)

        # Insert referers
        insert_referers(conn, referers)
    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
