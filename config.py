# This class contains all the configuration settings to connect to DB / localhost server
# config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
