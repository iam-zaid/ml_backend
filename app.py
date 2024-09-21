import streamlit as st
from preprocess import load_and_preprocess_data
from rec_model import recommend_collections
import pandas as pd

def main():
    st.title("Wellnify Recommendation System")
    
    # Sidebar for input
    st.sidebar.title("User Input")
    user_id = st.sidebar.number_input("Enter User ID", min_value=1, value=1, step=1)
    
    # Load and preprocess data
    collection_df, collection_result_df, user_to_org_df, cosine_sim_matrix = load_and_preprocess_data()
    
    # Get recommendations
    if st.sidebar.button("Get Recommendations"):
        recommendations = recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix)
        st.write("Recommended Collections:")
        recommendations = recommendations.reset_index(drop=True)
        st.write(recommendations)
        # for idx, row in recommendations.iterrows():
        #         st.write(f"**ID:** {row['id']}")
        #         st.write(f"**Name:** {row['name']}")
        #         st.write(f"**Description:** {row['description']}")
        #         st.write("---")  # Separator line for readability


if __name__ == "__main__":
    main()
