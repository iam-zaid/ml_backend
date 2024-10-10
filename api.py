"""
#Class: api.py
#Description: This class contains Code for handling API to be consumed for getting recommendations from the system. 
Note: For makign sure the code works the first time, I have added a safety check in a way that before getting recommendations the first time, 
        we have to run the load_and_preproces_data API to make sure we have the preprocessed Required for
"""
from flask import Flask, request, jsonify
from recommendation import recommend_collections, preprocess_data
from services import TableLoaderService
import logging
from logging.handlers import TimedRotatingFileHandler
import os

app = Flask(__name__)

"""Debug log setup code starts"""
# Set up the debug_logs folder if it doesn't exist
if not os.path.exists('debug_logs'):
    os.makedirs('debug_logs')

# Configure logging
log_handler = logging.handlers.TimedRotatingFileHandler(
    filename='debug_logs/rec_system.log',
    when='midnight',
    interval=1, # Rotate every 1 day
    backupCount=30  # Keep logs for the last 7 days
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Set up the logger
logger = logging.getLogger('RecommendationAPI')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)

"""Debug log setup code ends"""


class RecommendationAPI:
    def __init__(self):
        self.collection_df = None
        self.cosine_sim_type_df = None
        self.cosine_sim_tag_df = None
        self.cosine_sim_activities_df = None
        self.cosine_sim_description_df = None
        self.merged_df = None
        self.user_to_org_df = None
        self.data_loaded = False  # Flag to check if data is loaded
        logger.info("RecommendationAPI initialized")

    def load_and_preprocess_data(self):
        try:
            logger.info("Started loading and preprocessing data")
            # Load and preprocess data
            collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df, tag_df = TableLoaderService.load_data()
            collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df, merged_df = preprocess_data(collection_df, collection_result_df, activity_to_collection_df, collection_to_tag_df, tag_df)
            
            # Set as class attributes
            self.collection_df = collection_df
            self.cosine_sim_type_df = cosine_sim_type_df
            self.cosine_sim_tag_df = cosine_sim_tag_df
            self.cosine_sim_activities_df = cosine_sim_activities_df
            self.cosine_sim_description_df = cosine_sim_description_df
            self.merged_df = merged_df
            self.user_to_org_df = user_to_org_df
            self.data_loaded = True  # Set flag to True after data is loaded
            
            logger.info("Data successfully loaded and preprocessed")
        except Exception as e:
            logger.error(f"Error during data loading and preprocessing: {str(e)}")
            raise


    def get_recommendations(self, user_id):
        try:
            logger.info(f"Fetching recommendations for user_id: {user_id}")
            # Ensure data is loaded before fetching recommendations
            if not self.data_loaded:
                logger.warning("Data has not been preprocessed yet. Preprocess the data first.")
                return "Please preprocess data first by calling the /preprocess_data API."

            # Generate recommendations
            recommended_collections = recommend_collections(
                user_id,
                self.collection_df,  
                self.cosine_sim_type_df,  
                self.cosine_sim_tag_df,  
                self.cosine_sim_activities_df,  
                self.cosine_sim_description_df,  
                self.merged_df,  
                self.user_to_org_df,  
                None  # Weights (if None, defaults will be used)
            )
            logger.info(f"Recommendations successfully generated for user_id: {user_id}")
            return recommended_collections
        except Exception as e:
            logger.error(f"Error generating recommendations for user_id {user_id}: {str(e)}")
            return str(e)


# Initialize the API class
recommendation_api = RecommendationAPI()

# Home page route
@app.route('/')
def home():
    logger.info("Home page accessed")
    return """
    Welcome to Wellnify API app for the recommendation system! 
    Please run the /preprocess_data API first to load and preprocess the data before getting recommendations.
    """

# API to load and preprocess data
@app.route('/preprocess_data', methods=['GET'])
def preprocess():
    try:
        recommendation_api.load_and_preprocess_data()
        logger.info("Preprocess data API successfully called")
        return jsonify({"message": "Data successfully loaded and preprocessed."})
    except Exception as e:
        logger.error(f"Preprocess data API failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# API to get recommendations by user ID
@app.route('/recommendations/<int:id>', methods=['GET'])
def get_recommendations(id):
    if id is None:
        logger.error("No user ID provided in the request")
        return jsonify({"error": "userId is required"}), 400
    
    # Get recommendations for the user
    recommendations = recommendation_api.get_recommendations(id)
    
    # If recommendations are a string, it means there's an error
    if isinstance(recommendations, str):
        logger.warning(f"Error in recommendation generation: {recommendations}")
        return jsonify({"message": recommendations}), 400
    
    # Convert recommendations DataFrame to a dictionary
    result = recommendations.to_dict(orient='records')
    
    # Return the recommendations as a JSON response
    logger.info(f"Recommendations successfully returned for user_id: {id}")
    return jsonify(result)

if __name__ == '__main__':
    logger.info("Starting the Flask app")
    app.run(debug=True)
