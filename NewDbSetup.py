import psycopg2

# Replace with your RDS details
db_host = "thunder-buddy-db.cpoussw6oxmf.us-east-2.rds.amazonaws.com"  # Found in the AWS RDS console
db_name = "postgres"
db_user = "thunder_buddy"
db_password = "thunder_buddy"
db_port = "5432"  # Default PostgreSQL port

try:
    # Establish connection
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    print("✅ Connected to PostgreSQL successfully!")

    # Create a cursor to run SQL commands
    cur = conn.cursor()
    cur.execute("SELECT version();")  # Get PostgreSQL version
    version = cur.fetchone()
    print("PostgreSQL version:", version)

    # Close the connection
    cur.close()
    conn.close()
    print("✅ Connection closed.")
    

except Exception as e:
    print("❌ Error connecting to PostgreSQL:", e)
