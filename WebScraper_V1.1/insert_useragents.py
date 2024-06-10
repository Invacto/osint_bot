import psycopg2

# Database connection parameters
db_params = {
    'dbname': 'webscraper_dev_db',
    'user': 'dev',
    'password': 'Pineapple123!',
    'host': 'localhost',
    'port': '5432'
}

# Path to your user agents file
user_agents_file_path = 'user_agents.txt'


# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


# Function to create the useragents table
def create_useragents_table(conn):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS useragents (
        id SERIAL PRIMARY KEY,
        user_agent TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_user_agent ON useragents (user_agent);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        print("Useragents table creation successful.")
    except Exception as e:
        print(f"Error creating useragents table: {e}")
        conn.rollback()


# Function to insert user agents into the table
def insert_user_agents(conn, user_agents):
    insert_query = """
    INSERT INTO useragents (user_agent)
    VALUES (%s)
    """
    try:
        cursor = conn.cursor()
        for user_agent in user_agents:
            print(f"Inserting user agent: {user_agent}")
            cursor.execute(insert_query, (user_agent,))
        conn.commit()
        cursor.close()
        print("User agents insertion successful.")
    except Exception as e:
        print(f"Error inserting user agents: {e}")
        conn.rollback()


# Main function
def main():
    # Read user agents file
    try:
        with open(user_agents_file_path, 'r') as file:
            user_agents = [line.strip() for line in file.readlines()]
        print("User agents file reading successful. Data:")
        for user_agent in user_agents:
            print(user_agent)
    except Exception as e:
        print(f"Error reading user agents file: {e}")
        return

    # Connect to the database
    conn = connect_to_db()
    if not conn:
        return

    try:
        # Create useragents table
        create_useragents_table(conn)

        # Insert user agents
        insert_user_agents(conn, user_agents)
    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
