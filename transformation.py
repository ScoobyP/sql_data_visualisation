import mysql.connector
from sqlalchemy import create_engine
import os
import pandas as pd
from dotenv import load_dotenv

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.db_url_template = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
        self.user = os.getenv('aiven_user_name')
        self.password = os.getenv('aiven_user_pass')
        self.host = os.getenv('aiven_url1')
        self.port = os.getenv('aiven_port')
        self.db1 = os.getenv('aiven_db1')
        self.db2 = os.getenv('aiven_db2')
        self.engine = None
        self.mydb = None
        self.my_cursor = None

    def create_engine(self, db_name):
        db_url = self.db_url_template.format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            db=db_name
        )
        self.engine = create_engine(db_url)

    def load_data_from_db(self, table_name):
        try:
            self.create_engine(self.db1)
            df = pd.read_sql_table(table_name, con=self.engine)
            print(f"Table {table_name} successfully loaded from DB")
            return df
        except Exception as e:
            print(f"Error loading or connecting to/from database server: {e}")
            return None

    def replace_team_names(self, df):
        replacements = {
            'Rising Pune Supergiant': 'Rising Pune Supergiants',
            'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
            'Kings XI Punjab': 'Punjab Kings',
            'Delhi Daredevils': 'Delhi Capitals'
        }
        df.replace(replacements, inplace=True)
        return df

    def create_database(self, db_name):
        try:
            self.mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.my_cursor = self.mydb.cursor()
            self.my_cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
            self.mydb.commit()
            print(f'Database {db_name} created successfully')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if self.my_cursor:
                self.my_cursor.close()
            if self.mydb:
                self.mydb.close()

    def upload_data_to_db(self, df, table_name):
        try:
            self.create_engine(self.db2)
            df.to_sql(table_name, con=self.engine, if_exists='replace', chunksize=1000, index=False)
            print(f"Table {table_name} successfully loaded to DB")
        except Exception as e:
            print(f"Error loading or connecting to database server: {e}")

# Main execution
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Load data from the first database
    df1 = db_manager.load_data_from_db('all_deliveries')
    df2 = db_manager.load_data_from_db('all_matches')

    if df1 is not None and df2 is not None:
        # Replace team names
        df1 = db_manager.replace_team_names(df1)
        df2 = db_manager.replace_team_names(df2)

        # Create new database
        db_manager.create_database('ipl_OLAP')

        # Upload formatted data to the new database
        db_manager.upload_data_to_db(df1, 'all_deliveries')
        db_manager.upload_data_to_db(df2, 'all_matches')
