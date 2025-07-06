import psycopg2
from psycopg2.extras import RealDictCursor

def get_sample_destination():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname="your_database_name",
            user="your_username",
            password="your_password",
            host="localhost",  # Update if hosted elsewhere
            port="5432"         # Default PostgreSQL port
        )

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Query to fetch a sample destination
        query = "SELECT * FROM destinations LIMIT 1;"
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()
        if result:
            print("Sample Destination:")
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print("No destinations found in the database.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    get_sample_destination()
