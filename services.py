"""Class name: services.py
Description:Service class to load multiple tables from MySQL database using SQLAlchemy."
Owner: Wellnify"""

import pandas as pd
import sqlalchemy
from config import Config

class TableLoaderService:

    @staticmethod
    def load_data():
        """Loads multiple tables from the database into pandas DataFrames."""
        try:
            table_names = ['collection', 'collection_result', 'collection_to_tag', 'activity_to_collection', 'user_to_org','tag']
            engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)

            # print(engine)
            tables = {}

            # Load each table into a Pandas DataFrame
            for table_name in table_names:
                tables[table_name] = pd.read_sql_table(table_name, engine)

            # Extract the required tables
            collection_df = tables['collection']
            collection_result_df = tables['collection_result']
            collection_to_tag_df = tables['collection_to_tag']
            activity_to_collection_df = tables['activity_to_collection']
            user_to_org_df = tables['user_to_org']
            tag_df = tables['tag']

            # Return the DataFrames
            return collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df, tag_df

        except Exception as e:
            raise Exception(f"Error loading data from the database: {str(e)}")
