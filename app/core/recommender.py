import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pickle
import os

class CollaborativeFilteringRecommender:
    def __init__(self, ratings_filepath, restaurants_filepath):
        self.ratings_filepath = ratings_filepath
        self.model_path = 'models/surprise_model.pkl'
        self.model = None
        self.trainset = None
        self._load_model()

    def _load_model(self):
        """Loads the model from disk if it exists."""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)

    def train_and_save_model(self):
        """Trains the SVD model on the entire dataset and saves it."""
        df = pd.read_csv(self.ratings_filepath)
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'restaurant_id', 'rating']], reader)
        
        # Use the entire dataset for training the final model
        self.trainset = data.build_full_trainset()
        
        # SVD (Matrix Factorization) is a great choice
        self.model = SVD(n_factors=150, n_epochs=30, lr_all=0.005, reg_all=0.04)
        self.model.fit(self.trainset)
        
        # Save the trained model artifact
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print("Model trained and saved successfully.")

    def get_top_n_recommendations(self, user_id, n=10):
        """Gets top N recommendations for a user."""
        if not self.model or not self.trainset:
            print("Model not trained yet. Please train the model first.")
            return []

        # Get a list of all restaurant IDs
        all_restaurant_ids = pd.read_csv('data/restaurants.csv')['restaurant_id'].unique()
        
        # Get restaurant IDs that the user has already rated
        rated_restaurant_ids = pd.read_csv(self.ratings_filepath)
        rated_restaurant_ids = rated_restaurant_ids[rated_restaurant_ids['user_id'] == user_id]['restaurant_id']

        # Predict ratings for all restaurants the user has not yet rated
        predictions = []
        for restaurant_id in all_restaurant_ids:
            if restaurant_id not in rated_restaurant_ids.values:
                # Surprise uses internal IDs, so we check for their existence
                try:
                    internal_resto_id = self.trainset.to_inner_iid(restaurant_id)
                    predictions.append(self.model.predict(user_id, restaurant_id))
                except ValueError:
                    # This restaurant was not in the original training set
                    continue

        # Sort the predictions by estimated rating
        predictions.sort(key=lambda x: x.est, reverse=True)

        # Get the top N restaurant IDs
        top_n_restaurant_ids = [pred.iid for pred in predictions[:n]]
        return top_n_restaurant_ids