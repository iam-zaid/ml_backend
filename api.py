from flask import Flask, request, jsonify
from recommendation import recommend_collections,preprocess_data
from services import TableLoaderService


app = Flask(__name__)

class RecommendationAPI:
    def __init__(self):
        # Load and preprocess data once
        # self.collection_df, self.collection_result_df, self.user_to_org_df, self.cosine_sim_matrix = load_and_preprocess_data()
        collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df,tag_df = TableLoaderService.load_data()
        collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df, merged_df = preprocess_data(collection_df, collection_result_df, activity_to_collection_df,collection_to_tag_df,tag_df)
        print("Inside the init of recommendation class")
        # Set as class attributes
        self.collection_df = collection_df
        self.cosine_sim_type_df = cosine_sim_type_df
        self.cosine_sim_tag_df = cosine_sim_tag_df
        self.cosine_sim_activities_df = cosine_sim_activities_df
        self.cosine_sim_description_df = cosine_sim_description_df
        self.merged_df = merged_df
        self.user_to_org_df = user_to_org_df

    def get_recommendations(self, user_id):
        # Generate recommendations using the same logic as Streamlit app
        # recommendations = recommend_collections(user_id, self.collection_result_df, self.user_to_org_df, self.collection_df, self.cosine_sim_matrix)
        recommended_collections = recommend_collections(
        user_id,
        self.collection_df,  # Preprocessed collection DataFrame
        self.cosine_sim_type_df,  # Cosine similarity for type
        self.cosine_sim_tag_df,  # Cosine similarity for tags
        self. cosine_sim_activities_df,  # Cosine similarity for activities
        self.cosine_sim_description_df,  # Cosine similarity for description
        self. merged_df,  # Merged interaction DataFrame
        self.user_to_org_df,  # User-to-organization DataFrame
        None  # Weights (if None, defaults will be used)
          # Number of top recommendations
        )
        print("#$#$ Called recommendation#$#$")
        return recommended_collections

# Initialize the API class
recommendation_api = RecommendationAPI()

#Home page for default route
@app.route('/')
def home():
    print("###Inside the home of Flask###")
    app.logger.info("Home page accessed")
    return "Welcome to Wellnify API app for recommendation system "


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
    print("$$$Inside MAIN$$$")
    app.run(debug=True)
    
