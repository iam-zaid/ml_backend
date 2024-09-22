import streamlit as st
from preprocess import load_and_preprocess_data
from rec_model import recommend_collections
import pandas as pd
from PIL import Image

def main():

    logo = Image.open("resources/wellnify_logo.png")  
    st.image(logo, width=200) 

    st.title("Recommendation System")
    
    # Sidebar for input
    st.sidebar.title("User Input")
    user_id = st.sidebar.number_input("Enter User ID", min_value=1, value=1, step=1)
    
    # Load and preprocess data
    collection_df, collection_result_df, user_to_org_df, cosine_sim_matrix = load_and_preprocess_data()
    
    # Get recommendations
    if st.sidebar.button("Get Recommendations"):
        recommendations = recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix)
        recommendations = recommendations.rename(columns={'id':'ID','name':'Collection Name','description':'Description'})
        st.write("Recommended Collections:")
        st.write(recommendations)
        # for idx, row in recommendations.iterrows():
        #         st.write(f"**ID:** {row['id']}")
        #         st.write(f"**Name:** {row['name']}")
        #         st.write(f"**Description:** {row['description']}")
        #         st.write("---")  # Separator line for readability


if __name__ == "__main__":
    main()
