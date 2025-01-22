"""Class name: services.py
Description:Service class to load multiple tables from MySQL database using SQLAlchemy."
Owner: Wellnify"""

import pandas as pd
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from config import Config
from logger_config import LoggerConfig
from models import Recommendation

# Initialize logger
logger = LoggerConfig.initialize_logger()

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
    
    @staticmethod
    def save_recommendations_to_table(recommendations_df, table_name):
        """Saves df to database"""
        try:
            engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # List to keep track of rows that already exist in the database
            rows_to_remove = []
            
            # Loop through the DataFrame to check for existing recommendations
            for index, row in recommendations_df.iterrows():
                user_id = row['userId']
                collection_id = row['collectionId']
                
                # Check if the recommendation already exists
                existing_rec = session.query(Recommendation).filter_by(userId=user_id, collectionId=collection_id).first()
                
                if existing_rec:
                    print(f"Recommendation already exists for userId {user_id} and collectionId {collection_id}")
                    rows_to_remove.append(index)  # Add the index of the duplicate row
                    continue  # Skip inserting this row as it already exists
            
            # Drop the rows that already exist in the database
            recommendations_df = recommendations_df.drop(rows_to_remove)
            print(f"Dropped {len(rows_to_remove)} duplicate recommendations.")
            logger.info(f"Dropped {len(rows_to_remove)} duplicate recommendations.")

            # Save the DataFrame to the specified table
            recommendations_df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Successfully saved recommendations to table '{table_name}'.")
            logger.info(f"Successfully saved recommendations to table '{table_name}'")

        except ValueError as ve:
            raise Exception(f"Validation error: {str(ve)}")
        except IntegrityError as ie:
            # Handle any IntegrityError (like duplicates if not handled properly in previous code)
            session.rollback()  # Rollback the session in case of an error
            raise Exception(f"Database integrity error: {str(ie)}")
        except Exception as e:
            session.rollback()  # Rollback the session in case of any other error
            raise Exception(f"Unexpected error: {str(e)}")

    @staticmethod
    def initialize_user_recommendations_table():
        """Creates the user_recommendations table if it doesn't already exist."""
        try:
            engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)
            with engine.connect() as conn:
                # Check if the table exists
                result = conn.execute(text("SHOW TABLES LIKE 'user_recommendations';")).fetchall()
                if not result:
                    # Create the table
                    logger.info("Creating user_recommendations table...")
                    create_table_query = """
                    CREATE TABLE user_recommendations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        userId INT NOT NULL,
                        collectionId INT NOT NULL,
                        collectionType VARCHAR(255),
                        description TEXT,
                        name VARCHAR(255),
                        organizationId INT,
                        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                    conn.execute(text(create_table_query))
                    logger.info("user_recommendations table created successfully.")
                    print("user_recommendations table created successfully.")
                else:
                    logger.info("user_recommendations table already exists.")
        except Exception as e:
            logger.error(f"Error initializing user_recommendations table: {str(e)}")
            raise Exception(f"Error initializing user_recommendations table: {str(e)}")