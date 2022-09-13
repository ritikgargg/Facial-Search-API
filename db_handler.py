import psycopg2
import psycopg2.extras

class DBHandler:
    
    def __init__(self, hostname, database, username, password, port):
        """
        Creates a new database session and returns an instance of the connection class. 
        Creating a new cursor by using the connection object, to execute any SQL statements.

        Args:
            hostname: Database server address
            database: Name of the database to connect to
            username: Username used to authenticate
            password: Password used to authenticate
            port: Port number 
        """
        self.conn = None
        self.cur = None
        self.conn = psycopg2.connect(host = hostname, dbname = database, user = username, password = password, port = port) 
        self.cur = self.conn.cursor(cursor_factory = psycopg2.extras.DictCursor) 
        # DictCursor is used to access to the attributes of the retrieved records in a way similar to the Python dictionaries


    def executeQuery(self, query_string, parameters):
        """
        Function to execute any SQL query.

        Args:
        query_string: SQL query to be executed(may contain one or more placeholders)
        parameters: A tuple with values to replace the placeholders in the query_string           
        """
        self.cur.execute(query_string, parameters)

    def fetchAll(self):
        """Function to fetch all the rows in the result set """
        return self.cur.fetchall()

    def fetchOne(self):
        """Function to fetch the next row in the result set"""
        return self.cur.fetchone()

    def commitChanges(self):
        """Function to commit changes to the database."""
        self.conn.commit()

    def closeConnection(self):
        """Function to close the database connection"""
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()
