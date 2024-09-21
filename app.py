import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack, csr_matrix
import numpy as np

# Load CSV data
@st.cache_data
def load_data():
    collection_df = pd.read_csv('collection.csv')
    collection_to_tag_df = pd.read_csv('collection_to_tag.csv')
    activity_to_collection_df = pd.read_csv('activity_to_collection.csv')
    collection_result_df = pd.read_csv('collection_result.csv')
    user_to_org_df = pd.read_csv('user_to_org.csv')
    return collection_df, collection_to_tag_df, activity_to_collection_df, collection_result_df, user_to_org_df

# Define the recommendation function
def recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix, top_n=5):
    user_org_ids = user_to_org_df[user_to_org_df['userId'] == user_id]['orgId'].unique()
    org_collections = collection_df[collection_df['organizationId'].isin(user_org_ids)]
    user_collections = collection_result_df[
        (collection_result_df['userId'] == user_id) & 
        (collection_result_df['collectionId'].isin(org_collections['id']))
    ]['collectionId'].unique()
    
    if len(user_collections) == 0:
        return "No interactions found for this user in their organizations."
    
    filtered_collection_ids = org_collections['id'].values
    collection_id_to_idx = {collection_id: idx for idx, collection_id in enumerate(filtered_collection_ids)}
    
    filtered_cosine_sim_matrix = cosine_sim_matrix[
        np.ix_(
            [collection_id_to_idx[id] for id in filtered_collection_ids if id in collection_id_to_idx],
            [collection_id_to_idx[id] for id in filtered_collection_ids if id in collection_id_to_idx]
        )
    ]
    
    user_collections_idx = [collection_id_to_idx[collection_id] for collection_id in user_collections if collection_id in collection_id_to_idx]
    
    if len(user_collections_idx) > 0:
        mean_similarity_scores = np.mean(filtered_cosine_sim_matrix[user_collections_idx], axis=0)
        similar_collections_idx = np.argsort(mean_similarity_scores)[::-1]
        recommended_idx = [idx for idx in similar_collections_idx if idx not in user_collections_idx][:top_n]
        recommended_collection_ids = [filtered_collection_ids[idx] for idx in recommended_idx]
        recommended_collections = org_collections[org_collections['id'].isin(recommended_collection_ids)][['id', 'name', 'description']]
        return recommended_collections
    else:
        return "No valid collection data for recommendations."

# Main app
def main():
    st.title("Wellnify Recommendation System")
    
    # Load data
    collection_df, collection_to_tag_df, activity_to_collection_df, collection_result_df, user_to_org_df = load_data()
    
    # Sidebar for input
    st.sidebar.title("User Input")
    user_id = st.sidebar.number_input("Enter User ID", min_value=1, value=1, step=1)
    
    # Preprocess Tags, Collection Type, and Activities
    tag_df = collection_to_tag_df.merge(collection_df[['id']], left_on='collectionId', right_on='id', how='inner')
    tags_ohe = pd.get_dummies(tag_df['tagId'], prefix='tag')
    tags_ohe = tag_df[['collectionId']].join(tags_ohe).groupby('collectionId').sum().reset_index()
    
    collection_type_ohe = pd.get_dummies(collection_df['collectionType'], prefix='collection_type')
    collection_type_ohe = collection_df[['id']].join(collection_type_ohe)
    
    activity_df = activity_to_collection_df[['collectionId', 'activityId']].dropna()
    activity_ohe = pd.get_dummies(activity_df['activityId'], prefix='activity')
    activity_ohe = activity_df[['collectionId']].join(activity_ohe).groupby('collectionId').sum().reset_index()
    
    collection_features = collection_df[['id', 'name', 'description']]
    collection_features = collection_features.merge(tags_ohe, left_on='id', right_on='collectionId', how='left')
    collection_features = collection_features.merge(collection_type_ohe, left_on='id', right_on='id', how='left')
    collection_features = collection_features.merge(activity_ohe, left_on='id', right_on='collectionId', how='left')
    
    if 'collectionId' in collection_features.columns:
        collection_features = collection_features.drop(columns=['collectionId'])
    
    collection_features = collection_features.fillna(0)
    
    # Incorporate textual (TF-IDF) features
    collection_features['combined_text'] = collection_features['name'].fillna('') + ' ' + collection_features['description'].fillna('')
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(collection_features['combined_text'])
    
    non_text_features = collection_features.drop(columns=['id', 'name', 'description', 'combined_text'])
    non_text_features = non_text_features.astype(np.float64)
    non_text_features_sparse = csr_matrix(non_text_features.values)
    
    final_feature_matrix = hstack([tfidf_matrix, non_text_features_sparse])
    cosine_sim_matrix = cosine_similarity(final_feature_matrix, final_feature_matrix)
    
    # Get recommendations
    if st.sidebar.button("Get Recommendations"):
        recommendations = recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix)
        st.write("Recommended Collections:")
        st.write(recommendations)

if __name__ == "__main__":
    main()
