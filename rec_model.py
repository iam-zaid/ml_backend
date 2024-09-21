import numpy as np

def recommend_collections(user_id, collection_result_df, user_to_org_df, collection_df, cosine_sim_matrix, top_n=5):
    # Get the organization ID(s) associated with the user
    user_org_ids = user_to_org_df[user_to_org_df['userId'] == user_id]['orgId'].unique()
    
    # Filter collections to include only those that belong to the user's organization(s)
    org_collections = collection_df[collection_df['organizationId'].isin(user_org_ids)]
    
    # Get the collections the user has interacted with that are within the same organizations
    user_collections = collection_result_df[
        (collection_result_df['userId'] == user_id) & 
        (collection_result_df['collectionId'].isin(org_collections['id']))
    ]['collectionId'].unique()
    
    if len(user_collections) == 0:
        return "No interactions found for this user in their organizations."
    
    # Map collection IDs to indices in the filtered collection matrix
    filtered_collection_ids = org_collections['id'].values
    collection_id_to_idx = {collection_id: idx for idx, collection_id in enumerate(filtered_collection_ids)}
    
    # Subset the similarity matrix to include only collections from the user's organization(s)
    filtered_cosine_sim_matrix = cosine_sim_matrix[
        np.ix_(
            [collection_id_to_idx[id] for id in filtered_collection_ids if id in collection_id_to_idx],
            [collection_id_to_idx[id] for id in filtered_collection_ids if id in collection_id_to_idx]
        )
    ]
    
    # Get the indices of these collections in the filtered similarity matrix
    user_collections_idx = [collection_id_to_idx[collection_id] for collection_id in user_collections if collection_id in collection_id_to_idx]
    
    # Calculate the mean similarity score for all collections the user interacted with
    if len(user_collections_idx) > 0:
        mean_similarity_scores = np.mean(filtered_cosine_sim_matrix[user_collections_idx], axis=0)
        similar_collections_idx = np.argsort(mean_similarity_scores)[::-1]
        recommended_idx = [idx for idx in similar_collections_idx if idx not in user_collections_idx][:top_n]
        
        # Get the recommended collection IDs
        recommended_collection_ids = [filtered_collection_ids[idx] for idx in recommended_idx]
        recommended_collections = org_collections[org_collections['id'].isin(recommended_collection_ids)][['id', 'name', 'description']]
        recommended_collections = recommended_collections.reset_index(drop=True)
        return recommended_collections
    else:
        return "No valid collection data for recommendations."
