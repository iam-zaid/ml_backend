import streamlit as st
from preprocess import load_and_preprocess_data
from rec_model import recommend_collections
import pandas as pd
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

def main():
    st.title("Wellnify Recommendation System")
    
    # Sidebar for input
    st.sidebar.title("User Input")
    user_id = st.sidebar.number_input("Enter User ID", min_value=1, value=1, step=1)

    # Load data
    collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df = load_data()
    
    # Preprocess data
    collection_df, collection_result_df, user_to_org_df, cosine_sim_matrix = load_and_preprocess_data(collection_df,collection_to_tag_df,activity_to_collection_df,collection_result_df,user_to_org_df)
    
    # Get recommendations
    if st.sidebar.button("Get Recommendations"):
        recommendations = recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix)
        st.write("Recommended Collections:")
        # recommendations = recommendations.reset_index(drop=True)
        st.write(recommendations)
        # for idx, row in recommendations.iterrows():
        #         st.write(f"**ID:** {row['id']}")
        #         st.write(f"**Name:** {row['name']}")
        #         st.write(f"**Description:** {row['description']}")
        #         st.write("---")  # Separator line for readability


if __name__ == "__main__":
    main()
