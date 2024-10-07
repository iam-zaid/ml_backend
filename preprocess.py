import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services import TableLoaderService

def load_and_preprocess_data():
    # # Load CSV data
    # collection_df = pd.read_csv('data_csv/collection.csv')
    # collection_to_tag_df = pd.read_csv('data_csv/collection_to_tag.csv')
    # activity_to_collection_df = pd.read_csv('data_csv/activity_to_collection.csv')
    # collection_result_df = pd.read_csv('data_csv/collection_result.csv')
    # user_to_org_df = pd.read_csv('data_csv/user_to_org.csv')
    collection_df, collection_result_df, collection_to_tag_df, activity_to_collection_df, user_to_org_df = TableLoaderService.load_data()
    
    # Preprocess Tags, Collection Type, and Activities
    tag_df = collection_to_tag_df.merge(collection_df[['id']], left_on='collectionId', right_on='id', how='inner')
    tags_ohe = pd.get_dummies(tag_df['tagId'], prefix='tag')
    tags_ohe = tag_df[['collectionId']].join(tags_ohe).groupby('collectionId').sum().reset_index()
    
    collection_type_ohe = pd.get_dummies(collection_df['collectionType'], prefix='collection_type')
    collection_type_ohe = collection_df[['id']].join(collection_type_ohe)
    
    activity_df = activity_to_collection_df[['collectionId', 'activityId']].dropna()
    activity_ohe = pd.get_dummies(activity_df['activityId'], prefix='activity')
    activity_ohe = activity_df[['collectionId']].join(activity_ohe).groupby('collectionId').sum().reset_index()
    
    # Merge features with collection dataframe
    collection_features = collection_df[['id', 'name', 'description']]
    collection_features = collection_features.merge(tags_ohe, left_on='id', right_on='collectionId', how='left')
    collection_features = collection_features.merge(collection_type_ohe, left_on='id', right_on='id', how='left')
    collection_features = collection_features.merge(activity_ohe, left_on='id', right_on='collectionId', how='left')
    
    if 'collectionId' in collection_features.columns:
        collection_features = collection_features.drop(columns=['collectionId'])
    
    collection_features = collection_features.fillna(0)
    
    # Incorporating textual (TF-IDF) features
    collection_features['combined_text'] = collection_features['name'].fillna('') + ' ' + collection_features['description'].fillna('')
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(collection_features['combined_text'])
    
    non_text_features = collection_features.drop(columns=['id', 'name', 'description', 'combined_text'])
    non_text_features = non_text_features.astype(np.float64)
    non_text_features_sparse = csr_matrix(non_text_features.values)
    
    final_feature_matrix = hstack([tfidf_matrix, non_text_features_sparse])
    
    # Cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(final_feature_matrix, final_feature_matrix)
    
    return collection_df, collection_result_df, user_to_org_df, cosine_sim_matrix
