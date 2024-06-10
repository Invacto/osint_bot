import psycopg2
import json

# Database connection parameters
db_params = {
    'dbname': 'webscraper_dev_db',
    'user': 'dev',
    'password': 'Pineapple123!',
    'host': 'localhost',
    'port': '5432'
}

# Path to your JSON file
json_file_path = 'instagram_users_dict.txt'


# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


# Function to create the table
def create_table(conn):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS usernames (
        index SERIAL PRIMARY KEY,
        id VARCHAR(100) NOT NULL,
        u VARCHAR(100),
        n VARCHAR(100),
        e VARCHAR(100),
        t VARCHAR(100),
        a TEXT,
        profile_pic TEXT,
        image_1 TEXT,
        image_2 TEXT,
        image_3 TEXT,
        image_4 TEXT,
        image_5 TEXT,
        image_6 TEXT,
        image_7 TEXT,
        image_8 TEXT,
        image_9 TEXT,
        image_10 TEXT,
        image_11 TEXT,
        image_12 TEXT
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        print("Table creation successful.")

        # Verify table creation
        cursor = conn.cursor()
        cursor.execute("SELECT to_regclass('public.usernames');")
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("Table 'usernames' exists.")
        else:
            print("Table 'usernames' does not exist.")
        cursor.close()

    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()


# Function to insert data into the table
def insert_data(conn, data):
    insert_query = """
    INSERT INTO usernames (id, u, n, e, t, a)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor = conn.cursor()
        for record in data:
            cursor.execute(insert_query, (
                record.get('id'),
                record.get('u'),
                record.get('n'),
                record.get('e'),
                record.get('t'),
                record.get('a')
            ))
        conn.commit()
        cursor.close()
        print("Data insertion successful.")

        # Verify data insertion
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usernames;")
        count = cursor.fetchone()[0]
        print(f"Number of records in 'usernames': {count}")
        cursor.close()

    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()


# Main function
def main():
    # Read JSON file
    try:
        with open(json_file_path, 'r') as file:
            data = [json.loads(line) for line in file]
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    # Connect to the database
    conn = connect_to_db()
    if not conn:
        return

    try:
        # Create table
        create_table(conn)

        # Insert data
        insert_data(conn, data)
    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
