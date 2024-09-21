from flask import Flask, request, jsonify
from preprocess import load_and_preprocess_data
from rec_model import recommend_collections

app = Flask(__name__)

class RecommendationAPI:
    def __init__(self):
        # Load and preprocess data once
        self.collection_df, self.collection_result_df, self.user_to_org_df, self.cosine_sim_matrix = load_and_preprocess_data()

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
