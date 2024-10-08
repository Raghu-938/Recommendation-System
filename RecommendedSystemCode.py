import zipfile
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error
from scipy.sparse.linalg import svds

# Extracting the dataset
with zipfile.ZipFile("ml-latest-small.zip", 'r') as zip_ref:
    zip_ref.extractall("sample_data")

# Loading the data
ratings = pd.read_csv("sample_data/ml-latest-small/ratings.csv")
movies = pd.read_csv("sample_data/ml-latest-small/movies.csv")
movies = movies[['movieId', 'title']]
ratings = pd.merge(ratings, movies, on="movieId")

# Creating user-movie matrix
user_movie_matrix1 = ratings.pivot_table(index='userId', columns='title', values='rating').fillna(0)
user_movie_matrix = user_movie_matrix1.values

# Splitting the data into training and testing sets
train_data, test_data = train_test_split(ratings, test_size=0.2, random_state=42)

# Calculating user similarity using cosine similarity
user_similarity = cosine_similarity(user_movie_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix1.index, columns=user_movie_matrix1.index)
print(user_similarity_df.head())

# Function to make predictions
def predictions(user_movie_matrix, user_similarity_matrix):
    mean_rating = user_movie_matrix.mean(axis=1)
    rating_diff = user_movie_matrix - mean_rating[:, np.newaxis]
    pred = mean_rating[:, np.newaxis] + user_similarity_matrix.dot(rating_diff) / np.array([np.abs(user_similarity_matrix).sum(axis=1)]).T
    return pred

# Making predictions
predicted_ratings = predictions(user_movie_matrix1.values, user_similarity_df.values)
print(predicted_ratings)

# Function to recommend movies
def recommend_movies(user_id, user_movie_matrix, predicted_ratings, movies, num_recommendations=5):
    user_ratings = user_movie_matrix.loc[user_id]
    unrated_movies = user_ratings[user_ratings == 0].index
    predicted_scores = pd.Series(predicted_ratings[user_id - 1], index=user_movie_matrix.columns)
    recommendations = predicted_scores.loc[unrated_movies].sort_values(ascending=False).head(num_recommendations)
    return recommendations

# Getting movie recommendations for user 1
print(recommend_movies(1, user_movie_matrix1, predicted_ratings, movies))

# Evaluating the model using RMSE
def evaluate_model(user_movie_matrix1, predicted_ratings):
    rated_movies = user_movie_matrix1.values
    rmse = np.sqrt(mean_squared_error(rated_movies[rated_movies.nonzero()], predicted_ratings[rated_movies.nonzero()]))
    return rmse

# Evaluating the model
print(evaluate_model(user_movie_matrix1, predicted_ratings))

# Applying SVD (Singular Value Decomposition)
u, sigma, vt = svds(user_movie_matrix1.values, k=50)
sigma = np.diag(sigma)

# Making predictions using SVD
predicted_ratings_svd = np.dot(np.dot(u, sigma), vt)
predicted_ratings_svd_df = pd.DataFrame(predicted_ratings_svd, index=user_movie_matrix1.index, columns=user_movie_matrix1.columns)
print(predicted_ratings_svd_df)

# Getting movie recommendations using SVD for user 1
print(recommend_movies(1, user_movie_matrix1, predicted_ratings_svd, movies))

# Evaluating the SVD model
print(evaluate_model(user_movie_matrix1, predicted_ratings_svd))
