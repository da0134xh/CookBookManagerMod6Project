# Use the SQLite database
import sqlite3
from sqlite3 import Error

# Function to create a connection to the database
def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = sqlite3.connect('hipster_cookbooks.db')
        print(f"Successfully connected to SQLite {sqlite3.version} ")
        return conn
    except Error as e:
        print(f"Error establishing connection with the void: {e}")
        return None
    
# Function to create a table for storing the cookbooks
def create_table(conn):
    """Create a table structure"""
    try:
        sql_create_cookbooks_table = """
        CREATE TABLE IF NOT EXISTS cookbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year_published INTEGER,
            aesthetic_rating INTEGER,
            instagram_worthy BOOLEAN,
            cover_color TEXT
        );
        """
        
        # Create a new tags table with many-to-many relationship
        sql_create_tags_table = """
        CREATE TABLE IF NOT EXISTS tags (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag TEXT
        );
        """

        # Create junction table for many-to-many relationship
        sql_create_junction_tags_table = """
        CREATE TABLE IF NOT EXISTS tags_junction (
        cookbook_id INTEGER,
        tag_id INTEGER, 
        FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id),
        FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
        );
        """

        # Create a borrowing history table
        sql_create_tracking_table = """
        CREATE TABLE IF NOT EXISTS tracking_table (
        borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cookbook_id INTEGER,
        friend_name TEXT,
        date_borrowed TEXT,
        date_returned TEXT,
        FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id)
        );
        """

        # Calling the constructor for the cursor object to create a new cursor
        # (that lets us work with the database)
        cursor = conn.cursor()
        cursor.execute(sql_create_cookbooks_table)
        cursor.execute(sql_create_tags_table) # Creates new tag table
        cursor.execute(sql_create_junction_tags_table) # Creates new tag junction table
        cursor.execute(sql_create_tracking_table) # Creates new tracking table
        print("Successfully created a database structure")
    except Error as e:
        print(f"Error creating table: {e}")


# Function will insert a new cookbook record into the database table
def insert_cookbook(conn, cookbook):
    """Add a new cookbook to your shelf"""
    sql = '''INSERT INTO cookbooks(title, author, year_published, aesthetic_rating,
            instagram_worthy, cover_color)
            VALUES(?,?,?,?,?,?)'''
    
    # Use the connection to the database to insert the new record
    try:
        # Create a new cursor (this is like a pointer that lets us traverse our database)
        cursor = conn.cursor()
        cursor.execute(sql, cookbook)
        # Commit the changes
        conn.commit()
        print(f"Successfully curated cookbook with the id: {cursor.lastrowid}")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding to collection: {e}")
        return None
    
# Function to retrieve the cookbooks from the database
def get_all_cookbooks(conn):
    """Browse your entire collection of cookbooks"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookbooks")
        # Put the resultset of cookbooks into a list called books
        books = cursor.fetchall()

        # Iterate through the list of books and display the info for each cookbook
        for book in books:
            print(f"ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Published: {book[3]}")
            print(f"Aesthetic Rating: {'⭐' * book[4]}")
            print(f"Instagrame Worthy: {'📸 Yes' if book[5] else 'Not aesthetic enough'}")
            print(f"Cover Color: {book[6]}")
            print("---")
        return books
    except Error as e:
        print(f"Error retrieving collection: {e}")
        return[]
    
def track_borrowed_cookbook(conn, record):
    """Track which friend borrowed your cookbook and when"""
    # Add borrowing record
    # Include return date tracking
    try:
        cursor = conn.cursor()
        sqlInsert = ("""
            INSERT INTO tracking_table (cookbook_id, friend_name, date_borrowed, date_returned)
            VALUES(?,?,?,?)""")
        cursor.execute(sqlInsert, record)
        conn.commit()
        print("\nAdded records to tracking table!")

    except Error as e:
        print(f"Error with tracking table {e}")
    

def add_recipe_tags(conn):
    """Add tags to a cookbook (e.g., 'gluten-free', 'plant-based', 'artisanal')"""
    # Implement tag addition functionality

    print("\nYour tag options are: gluten-free, plant-based, artisinal")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cookbooks")
        # Put the resultset of cookbooks into a list called books
        cookbook_ids = cursor.fetchall()

        # Insert same ids into tags table and junction table

        # Needed some help with this part of the code. Gemini.google
        # iterating through the existing cookbook ids and copying to new tabs table
        # Requesting user to insert tags for each cookbook id - separated by comma if mulitple
        for id in cookbook_ids:
            new_tag_id = id[0]
            print(f"Enter the tags for cookbook id {new_tag_id} (comma-separated): ")
            tags_input = input()
            tags = [tag.strip() for tag in tags_input.split(',')]

            # Check if tag for each bookid=tagid exists, do nothing.
            # Else add tag to tagid
            for tag in tags:
                cursor.execute("SELECT tag_id FROM tags WHERE tag = ?", (tag,))
                existing_tag = cursor.fetchone()

                if existing_tag:
                    tag_id = existing_tag[0]
                else:
                    cursor.execute("INSERT INTO tags (tag) VALUES (?)", (tag,))
                    tag_id = cursor.lastrowid
                
                # Inserts the tags and tag ids into the tags junction table to form many-to-many relationship
                cursor.execute("INSERT INTO tags_junction (cookbook_id, tag_id) VALUES (?, ?)", (new_tag_id, tag_id))
    
        conn.commit()
        print("Tags added successfully!")

    # failure status
    except Error as e:
        print(f"Error adding tags: {e}")

# Displays the records entered into the tracking table
def get_all_tracking(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracking_table")
        # Put the resultset of cookbooks into a list called books
        records = cursor.fetchall()

        for record in records:
            print(f"\n{record}")

    except Error as e:
        print(f"Error with tracking table display {e}")





# Main function is called when the program executes
# It directs the show
def main():
    # Establish connection to our cookbook database
    conn = create_connection()

    # Test if the connection is viable
    if conn is not None:
        #Drop the existing table
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS cookbooks")
        cursor.execute("DROP TABLE IF EXISTS tags")
        cursor.execute("DROP TABLE IF EXISTS tags_junction")
        cursor.execute("DROP TABLE IF EXISTS tracking_table")
        conn.commit()
        
        # Create our table
        create_table(conn)

        #Insert some carefully curated sample cookbooks
        cookbooks = [
            ('Foraged & Found: A Guide to Pretending You Know About Mushrooms',
             'Oak Wavelength', 2023, 5, True, 'Forest Green'),
             ('Small Batch: 50 Recipes You will Never Actually Make',
              'Sage Moonbeam', 2022, 4, True, 'Raw Linen'),
              ('The Artistic Toast: Advanced Avocado Techniques',
               'River Wildflower', 2023, 5, True, 'Recycled Brown'),
               ('Fremented Everything',
                'Jim Kombucha', 2021, 3, True, 'Denim'),
                ('The Deconstructed Sandwich: Making Simple Things Complicated',
                 'Juniper Vinegar-Smith', 2023, 5, True, 'Beige')
        ]

        # Display our list of books
        print("\n Curating your cookbook collection . . .")

        # Insert cookbooks into the database
        for cookbook in cookbooks:
            insert_cookbook(conn, cookbook)

        # Get the cookbooks from the database
        print("\nYour carefully curated collection:")
        get_all_cookbooks(conn)

        # Adds tags to existing cookbooks and saves tags in new tags table
        add_recipe_tags(conn)

        #Insert some borrowed history
        records = [
        (1, "Carlos", "02-26-2025", "02-27-2025"),
        (3, "Adam", "03-01-2025", "03-02-2025"),
        (7, "Alex", "01-01-2025", "03-05-2025")
        ]

        # Insert records into tracking table
        for record in records:
            track_borrowed_cookbook(conn, record)

        # Display tracking table
        get_all_tracking(conn)

        # Close the database connection
        conn.close()
        print("\nDatabase connection closed")

    else:
        print("Error! The universe is not aligned for database connections right now.")

# Code to call the main function
if __name__ == '__main__':
    main()
