from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection

# Step 1: Create an engine to connect to the SQLite database
DATABASE_URL = "sqlite:///example_sql.db"  # SQLite database path
engine = create_engine(DATABASE_URL)

# Step 2: Reflect the database schema into Python objects
metadata = MetaData()

# Reflect all the tables in the database
metadata.reflect(bind=engine)

# Step 3: Accessing tables dynamically
# For example, get a list of table names
table_names = metadata.tables.keys()
print("Tables in the database:", table_names)

# Step 4: Accessing data from a table dynamically
# Suppose you want to work with a specific table, let's say "users"
# Get the "users" table (if it exists)
if "Client ID" in metadata.tables:

    inspector = reflection.Inspector.from_engine(engine)
    columns = inspector.get_columns('Client ID')

    for column in columns:
        print(column)

    # Step 5: Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Step 6: Query the table dynamically
   # result = session.query(users_table).all()

    # Step 7: Print the result (this will print rows as tuples)
    #for row in result:
    #    print(row)

    # Close the session
    session.close()
else:
    print("Table 'users' does not exist in the database")







