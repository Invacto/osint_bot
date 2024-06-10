import sys
import time
import psutil
import threading
import psycopg2
from concurrent.futures import ThreadPoolExecutor
from scrape_username import process_username as original_process_username
import re

cpu_usages = []
memory_usages = []
bandwidth_sents = []
bandwidth_recvs = []
db_params = {
    'dbname': 'webscraper_dev_db',
    'user': 'dev',
    'password': 'Pineapple123!',
    'host': '172.18.0.2',
    'port': '5432'
}


# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


# Function to fetch usernames from the database based on index range
def fetch_usernames(conn, start_index, end_index):
    fetch_query = """
    SELECT index, u, profile_pic FROM usernames
    WHERE index >= %s AND index <= %s
    AND profile_pic IS NULL;
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(fetch_query, (start_index, end_index))
            usernames = cursor.fetchall()
        return [username[1] for username in usernames]
    except Exception as e:
        print(f"Error fetching usernames: {e}")
        return []


def process_username(username):
    start_time = time.time()
    return_code = original_process_username(username)
    end_time = time.time()
    return username, end_time - start_time, return_code


def get_system_stats():
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage, memory_usage


def get_network_stats():
    net_io_counters = psutil.net_io_counters()
    total_bytes_sent = net_io_counters.bytes_sent
    total_bytes_recv = net_io_counters.bytes_recv
    return total_bytes_sent, total_bytes_recv


def monitor_system_stats(interval):
    global cpu_usages, memory_usages, bandwidth_sents, bandwidth_recvs

    while True:
        cpu_usage, memory_usage = get_system_stats()
        bandwidth_sent, bandwidth_recv = get_network_stats()

        # Append stats to lists
        cpu_usages.append(cpu_usage)
        memory_usages.append(memory_usage)
        bandwidth_sents.append(bandwidth_sent)
        bandwidth_recvs.append(bandwidth_recv)

        time.sleep(interval)


def calculate_stats(data):
    if not data:
        return None, None, None

    low = min(data)
    mean = sum(data) / len(data)
    high = max(data)
    return low, mean, high
# Function to update user data in the database

def update_user_data(conn, username, column, url):
    update_query = f"""
    UPDATE usernames
    SET {column} = %s
    WHERE u = %s;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(update_query, (url, username))
        conn.commit()
        cursor.close()
        print(f"Updated {username}: {column} = {url}")
    except Exception as e:
        print(f"Error updating {username}: {e}")
        conn.rollback()

# Function to process the scraped data file and update the database

def process_scraped_data(conn, file_path):
    line_pattern = re.compile(r'([^:]+):"([^"]+)"="([^"]+)"')

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = line_pattern.match(line.strip())
                if match:
                    username, column, url = match.groups()
                    update_user_data(conn, username, column, url)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def main(start_index, end_index, monitor_interval):
    conn = connect_to_db()
    if not conn:
        return

    try:
        usernames = fetch_usernames(conn, start_index, end_index)

        with open('usernames.txt', 'w') as f:
            for username in usernames:
                f.write(f"{username}\n")

        monitor_thread = threading.Thread(target=monitor_system_stats, args=(monitor_interval,))
        monitor_thread.daemon = True
        monitor_thread.start()

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_username, usernames))

        cpu_low, cpu_mean, cpu_high = calculate_stats(cpu_usages)
        memory_low, memory_mean, memory_high = calculate_stats(memory_usages)
        bandwidth_sent_low, bandwidth_sent_mean, bandwidth_sent_high = calculate_stats(bandwidth_sents)
        bandwidth_recv_low, bandwidth_recv_mean, bandwidth_recv_high = calculate_stats(bandwidth_recvs)

        print("Output results here...")

        for username, duration, return_code in results:
            print(f"Username: {username}, Time taken: {duration:.2f} seconds, Return Code: {return_code}")

        print("System Stats:")
        print(f"CPU Usage (Low, Mean, High): {cpu_low}, {cpu_mean}, {cpu_high}")
        print(f"Memory Usage (Low, Mean, High): {memory_low}, {memory_mean}, {memory_high}")
        print(f"Bandwidth Sent (Low, Mean, High): {bandwidth_sent_low}, {bandwidth_sent_mean}, {bandwidth_sent_high}")
        print(
            f"Bandwidth Received (Low, Mean, High): {bandwidth_recv_low}, {bandwidth_recv_mean}, {bandwidth_recv_high}")

    finally:
        process_scraped_data(conn, 'scraped_data.txt')
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script_name.py <start_index> <end_index> <monitor_interval>")
        sys.exit(1)

    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])
    monitor_interval = float(sys.argv[3])
    main(start_index, end_index, monitor_interval)
