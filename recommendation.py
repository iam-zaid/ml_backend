import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
import logging

# Configure logging
logging.basicConfig(filename='recommendation_system.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the tag_category is split into tag_list
def split_tags(collection_df):
    logging.info("Splitting 'tag_category' into tag_list.")
    collection_df['tag_list'] = collection_df['tag_category'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    return collection_df

# Parse tag components (split into tag type and specific value)
def split_tag_components(collection_df):
    logging.info("Parsing tag components.")
    def parse_tag(tag):
        components = tag.split('-')
        if len(components) == 2:
            return components[1], components[0]  # Return as (tag_type, specific_value)
        return None, None

    # Apply the parsing to each tag in the 'tag_list'
    tag_data = []
    for tag_list in collection_df['tag_list']:
        parsed_tags = [parse_tag(tag) for tag in tag_list]
        tag_data.append([tag for tag in parsed_tags if None not in tag])

    collection_df['parsed_tag_list'] = tag_data
    return collection_df

# Binarize tag types and specific values
def binarize_tags(collection_df):
    logging.info("Binarizing tag types and specific values.")
    mlb_tag_types = MultiLabelBinarizer()
    mlb_specific_values = MultiLabelBinarizer()

    tag_types_binarized = pd.DataFrame(mlb_tag_types.fit_transform(collection_df['tag_types']), columns=mlb_tag_types.classes_, index=collection_df.index)
    specific_values_binarized = pd.DataFrame(mlb_specific_values.fit_transform(collection_df['specific_values']), columns=mlb_specific_values.classes_, index=collection_df.index)

    return tag_types_binarized, specific_values_binarized

# Prepare activity features
def prepare_activity_features(activity_to_collection_df, collection_df):
    logging.info("Preparing activity features.")
    activity_df = activity_to_collection_df[['collectionId', 'activityId']].dropna()
    activity_ohe = pd.get_dummies(activity_df['activityId'], prefix='activity')
    activity_ohe = activity_df[['collectionId']].join(activity_ohe).groupby('collectionId').sum().reset_index()

    collection_df = pd.merge(collection_df, activity_ohe, on='collectionId', how='left', suffixes=('', '_activity'))
    collection_df.columns = [col.replace('activity_activity_', 'activity_') for col in collection_df.columns]

    return collection_df

# Preprocess the data
def preprocess_data(collection_df, collection_result_df, activity_to_collection_df,collection_to_tag_df, tag_df):

    logging.info("Starting data preprocessing.")
    
    collection_df = collection_df[collection_df['deletedAt'].isna()]

    # Merge Tags and collection
    merged_df1 = pd.merge(collection_to_tag_df, collection_df, left_on='collectionId', right_on='id', how='inner')
    final_merged_df = pd.merge(merged_df1, tag_df, left_on='tagId', right_on='id', how='inner')

    logging.info(f"Final merged DataFrame shape: {final_merged_df.shape}")

    # Dropping unnecessary columns (duplicate timestamps, ids, and nulls)
    columns_to_drop = [
        'createdAt_x', 'updatedAt_x', 'deletedAt_x', 'id_x',
        'createdAt_y', 'updatedAt_y', 'deletedAt_y', 'id_y',
        'id','coinPrice','quizId','desiredReturn','pbucksPrice',
        'status','updatedAt','createdAt','deletedAt','bannerImageId'
    ]
    
    # Dropping and renaming columns from the DataFrame
    cleaned_df = final_merged_df.drop(columns=columns_to_drop)
    cleaned_df.rename(columns={'text': 'tag'}, inplace=True)
    cleaned_df['tag'] = cleaned_df['tag'].str.replace(' ', '_')
    cleaned_df['category'] = cleaned_df['category'].str.replace(' ', '_')
    cleaned_df['tag_category'] = cleaned_df['tag'] + '-' + cleaned_df['category']

    grouped_collection_df = cleaned_df.groupby('collectionId').agg({
        'name': 'first', 
        'collectionType': 'first',
        'description': 'first',
        'organizationId': 'first',
        'tag_category': lambda x: ', '.join(x)  # Concatenate all tag-category pairs
    }).reset_index()
    
    grouped_collection_df['tag_category'] = grouped_collection_df['tag_category'].apply(lambda x: ','.join([tag.strip() for tag in x.split(',')]) if isinstance(x, str) else x)

    collection_df=grouped_collection_df

    logging.info(f"Processed collection DataFrame shape: {collection_df.shape}")
    
    # Split tags and components
    collection_df = split_tags(collection_df)
    collection_df = split_tag_components(collection_df)

    # Extract and binarize tag types and specific values
    collection_df['tag_types'] = collection_df['parsed_tag_list'].apply(lambda x: [tag[0] for tag in x])
    collection_df['specific_values'] = collection_df['parsed_tag_list'].apply(lambda x: [tag[1] for tag in x])
    
    tag_types_binarized, specific_values_binarized = binarize_tags(collection_df)

    # Prepare activity features and merge with collection data
    collection_df = prepare_activity_features(activity_to_collection_df, collection_df)

    # Compute cosine similarities
    logging.info("Calculating cosine similarities.")
    cosine_sim_type = cosine_similarity(tag_types_binarized, tag_types_binarized)
    cosine_sim_tag = cosine_similarity(specific_values_binarized, specific_values_binarized)
    cosine_sim_activities = cosine_similarity(collection_df.filter(like='activity_').fillna(0))

    # Convert cosine similarities to DataFrames for easy lookup
    cosine_sim_type_df = pd.DataFrame(cosine_sim_type, index=collection_df['name'], columns=collection_df['name'])
    cosine_sim_tag_df = pd.DataFrame(cosine_sim_tag, index=collection_df['name'], columns=collection_df['name'])
    cosine_sim_activities_df = pd.DataFrame(cosine_sim_activities, index=collection_df['name'], columns=collection_df['name'])

    # Compute TF-IDF for textual description
    logging.info("Computing TF-IDF for description.")
    tfidf_vectorizer_description = TfidfVectorizer(stop_words='english')
    tfidf_matrix_description = tfidf_vectorizer_description.fit_transform(collection_df['description'])
    cosine_sim_description = cosine_similarity(tfidf_matrix_description, tfidf_matrix_description)
    cosine_sim_description_df = pd.DataFrame(cosine_sim_description, index=collection_df['name'], columns=collection_df['name'])

    # Merge user interaction data with collection details
    merged_df = pd.merge(collection_result_df, collection_df[['collectionId', 'name']], on='collectionId')
    
    return collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df,merged_df

# Recommendation function with balanced tag weights
def recommend_collections(user_id, collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df, merged_df, user_to_org_df, weights=None, top_n=5):
    logging.info(f"Generating recommendations for user {user_id}.")
    if weights is None:
        weights = {'description': 0.2, 'type': 0.4, 'tag': 0.2, 'activities': 0.2}
    
    # Get the organizations the user is part of
    user_orgs = user_to_org_df[user_to_org_df['userId'] == user_id]['orgId'].unique()
    logging.debug(f"User {user_id} is part of organizations: {user_orgs}.")
    
    # Filter collections that belong to these organizations
    filtered_collections = collection_df[collection_df['organizationId'].isin(user_orgs)]
    
    # Get collections the user has interacted with from these organizations
    user_collections = merged_df[(merged_df['userId'] == user_id) & (merged_df['collectionId'].isin(filtered_collections['collectionId']))]['name'].unique()
    
    if len(user_collections) == 0:
        logging.info(f"No user interactions found for user {user_id}. Returning empty Data")
        return pd.DataFrame()
    
    # Filter the cosine similarity matrices to only include these collections
    sim_scores_description = cosine_sim_description_df.loc[filtered_collections['name'], user_collections].mean(axis=1)
    sim_scores_type = cosine_sim_type_df.loc[filtered_collections['name'], user_collections].mean(axis=1)
    sim_scores_tag = cosine_sim_tag_df.loc[filtered_collections['name'], user_collections].mean(axis=1)
    sim_scores_activities = cosine_sim_activities_df.loc[filtered_collections['name'], user_collections].mean(axis=1)
    
    # Combine the similarity scores using the provided weights
    combined_sim_scores = (
        weights['description'] * sim_scores_description +
        weights['type'] * sim_scores_type +
        weights['tag'] * sim_scores_tag +
        weights['activities'] * sim_scores_activities
    )
    
    # Sort the collections by similarity score, exclude the ones the user already interacted with
    combined_sim_scores = combined_sim_scores.drop(user_collections).sort_values(ascending=False)
    
    # Get the top N collection names
    top_collections = combined_sim_scores.head(top_n).index
    
    # Return the full collection rows for the recommended collections
    return filtered_collections[filtered_collections['name'].isin(top_collections)]