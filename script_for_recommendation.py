from datetime import datetime
import pandas as pd
from services import TableLoaderService  # Handles database operations
from recommendation import recommend_collections, preprocess_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_user_ids(user_to_org_df):
    """
    Extracts all unique user IDs from the user_to_org DataFrame.
    """
    try:
        user_ids = user_to_org_df['userId'].dropna().unique()
        return user_ids.tolist()
    except Exception as e:
        logger.error(f"Error extracting user IDs: {e}")
        return []

def process_recommendations_for_all_users():
    """
    Generate and save recommendations for all users using TableLoaderService and Recommendation class.
    """
    try:
        logger.info("Starting the recommendation process for all users.")

        # Load and preprocess data
        logger.info("Loading data from the database.")
        (
            collection_df, 
            collection_result_df, 
            collection_to_tag_df, 
            activity_to_collection_df, 
            user_to_org_df, 
            tag_df
        ) = TableLoaderService.load_data()

        # recommendation_system = recommendation()

        logger.info("Preprocessing data for recommendations.")
        collection_df, cosine_sim_type_df, cosine_sim_tag_df, cosine_sim_activities_df, cosine_sim_description_df, merged_df=preprocess_data(collection_df,collection_result_df,activity_to_collection_df,collection_to_tag_df,tag_df)

        user_ids = get_all_user_ids(user_to_org_df)
        
        if not user_ids:
            logger.error("No user IDs found.")
            return

        logger.info(f"Found {len(user_ids)} users to generate recommendations for.")

        recommendations_list = []

        for user_id in user_ids:
            try:
                logger.info(f"Generating recommendations for user ID: {user_id}.")
                recommendations = recommend_collections(user_id,collection_df,cosine_sim_type_df,cosine_sim_tag_df,cosine_sim_activities_df,cosine_sim_description_df,merged_df,  user_to_org_df,None)

                if recommendations.empty:
                    logger.warning(f"No recommendations generated for user ID: {user_id}.")
                    continue

                # Add metadata to recommendations
                recommendations['userId'] = user_id
                recommendations['createdAt'] = datetime.now()

                recommendations_list.append(recommendations)
                logger.info(f"Recommendations generated for user ID: {user_id}.")
            
            except Exception as e:
                logger.error(f"Error generating recommendations for user ID {user_id}: {e}")

        if recommendations_list:
            logger.info("Combining and saving all recommendations.")
            final_recommendations = pd.concat(recommendations_list)[
                ['userId', 'collectionId', 'collectionType', 'description', 'name', 'organizationId', 'createdAt']
            ]

            TableLoaderService.save_recommendations_to_table(final_recommendations, "user_recommendations")
            logger.info("All recommendations saved successfully.")
        else:
            logger.warning("No recommendations to save.")

    except Exception as e:
        logger.error(f"Error in processing recommendations: {e}")

if __name__ == "__main__":
    # Ensure the user_recommendations table is ready
    TableLoaderService.initialize_user_recommendations_table()

    # Process recommendations
    process_recommendations_for_all_users()
