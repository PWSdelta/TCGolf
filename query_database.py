import psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',  # Change to your DB host
    'port': 5432          # Default PostgreSQL port
}

def query_database(query, params=None):
    """Execute a query on the PostgreSQL database."""
    connection = None
    cursor = None  # Initialize cursor to None

    try:
        # Connect to the database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query, params)

        # Fetch results if it's a SELECT query
        if query.strip().lower().startswith('select'):
            results = cursor.fetchall()
            return results

        # Commit changes for non-SELECT queries
        connection.commit()
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    # Example query: Fetch destination data
    sample_query = """
    SELECT id, name, region, country
    FROM destinations
    WHERE country = %s
    LIMIT 10;
    """

    # Replace 'United States' with the desired country
    country = 'United States'

    print(f"Querying destinations in {country}...")
    results = query_database(sample_query, (country,))

    if results:
        print("\nResults:")
        for row in results:
            print(row)
    else:
        print("No results found or an error occurred.")
