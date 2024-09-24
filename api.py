from flask import Flask, request, jsonify
from preprocess import load_and_preprocess_data
from rec_model import recommend_collections
import sqlalchemy
from dotenv import load_dotenv
from config import Config


load_dotenv()


#SQL Connection
def load_data():
    table_names=['collection','collection_result','collection_to_tag','activity_to_collection','user_to_org']
    engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)
    tables = {}
    for table_name in table_names:
        tables[table_name] = pd.read_sql_table(table_name, engine)

    collection_df=tables['collection']
    collection_result_df=tables['collection_result']
    collection_to_tag_df=tables['collection_to_tag']
    activity_to_collection_df=tables['activity_to_collection']
    user_to_org_df=tables['user_to_org']
    return collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df

app = Flask(__name__)

class RecommendationAPI:
    def __init__(self):
        # Load and preprocess data once
        # Load data
        collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df = load_data()
        self.collection_df, self.collection_result_df, self.user_to_org_df, self.cosine_sim_matrix = load_and_preprocess_data(collection_df,collection_to_tag_df,activity_to_collection_df,collection_result_df,user_to_org_df)


    def get_recommendations(self, user_id):
        # Generate recommendations using the same logic as Streamlit app
        recommendations = recommend_collections(user_id, self.collection_result_df, self.user_to_org_df, self.collection_df, self.cosine_sim_matrix)
        return recommendations

# Initialize the API class
recommendation_api = RecommendationAPI()

# Define the GET API endpoint
@app.route('/recommendations/<int:id>', methods=['GET'])
def get_recommendations(id):    
    if id is None:
        return jsonify({"error": "userId is required"}), 400
    
    # Get recommendations for the user
    recommendations = recommendation_api.get_recommendations(id)
    
    # If recommendations are a string, it means there's an error or no results
    if isinstance(recommendations, str):
        return jsonify({"message": recommendations})
    
    # Convert recommendations DataFrame to a dictionary
    result = recommendations.to_dict(orient='records')
    
    # Return the recommendations as a JSON response
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
