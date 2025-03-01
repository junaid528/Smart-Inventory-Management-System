import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.models.user_behavior import UserBehavior  # Ensure UserBehavior is imported

def generate_product_recommendations(user_id):
    # Fetch user behavior data
    user_behavior = UserBehavior.query.filter_by(user_id=user_id).all()
    
    if not user_behavior:
        print(f"No behavior data for user {user_id}. No recommendations can be made.")
        return []  # No data available for recommendations
    
    # Create a user-item matrix (assuming user_behavior is a list of interactions with product IDs)
    data = pd.DataFrame([(entry.user_id, entry.product_id, entry.rating) for entry in user_behavior],
                        columns=['user_id', 'product_id', 'rating'])
    
    # Pivot the table to create the user-item matrix
    user_item_matrix = data.pivot(index='user_id', columns='product_id', values='rating')
    
    print(f"User-item matrix for user {user_id}:\n{user_item_matrix}")  # Debugging
    
    # If the matrix is empty, return an empty list
    if user_item_matrix.shape[0] == 0:
        print("User-item matrix is empty. No recommendations can be made.")
        return []
    
    # Ensure NaN values are filled with 0s (or use other imputation methods)
    user_item_matrix = user_item_matrix.fillna(0)

    # Compute cosine similarity between users (rows)
    cosine_sim = cosine_similarity(user_item_matrix)

    # Process the similarities and generate recommendations (You might need to implement this logic)
    recommendations = process_similarities(cosine_sim, user_behavior)
    return recommendations
