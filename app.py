"""
#Class: app.py
#Description: This class contains Code for the streamlit app that can be used to demo the functionality for the recommendation system
Note: this was created for demo and checking the functionality from backend if there is any error or irregularity
Owner: Wellnify
"""
from services import TableLoaderService
import streamlit as st
from recommendation import preprocess_data, recommend_collections
import pandas as pd
from PIL import Image

def main():

    logo = Image.open("resources/wellnify_logo.png")  
    st.image(logo, width=200) 

    st.title("Recommendation System")
    
    # Sidebar for input
    st.sidebar.title("User Input")
    user_id = st.sidebar.number_input("Enter User ID", min_value=1, value=1, step=1)
    
    collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df,tag_df = TableLoaderService.load_data()

    # Preprocess the data
    collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df, merged_df = preprocess_data(collection_df, collection_result_df, activity_to_collection_df,collection_to_tag_df,tag_df)


    # Example: Get recommendations for user_id 564
    
    
    # Get recommendations
    if st.sidebar.button("Get Recommendations"):
        recommended_collections = recommend_collections(
        user_id,
        collection_df,  # Preprocessed collection DataFrame
        cosine_sim_type_df,  # Cosine similarity for type
        cosine_sim_tag_df,  # Cosine similarity for tags
        cosine_sim_activities_df,  # Cosine similarity for activities
        cosine_sim_description_df,  # Cosine similarity for description
        merged_df,  # Merged interaction DataFrame
        user_to_org_df,  # User-to-organization DataFrame
        None  # Weights (if None, defaults will be used)
          # Number of top recommendations
        )
        st.write("Recommended Collections:")
        st.write(recommended_collections)

        print(recommended_collections)


if __name__ == "__main__":
    main()
