import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import json

class HybridRecommender:
    """
    Hybrid Recommendation System combining Content-Based and Collaborative Filtering
    """
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.content_similarity_matrix = None
        self.books_df = None
        self.ratings_matrix = None
        self.knn_model = None
        
    def fit(self, books, ratings):
        """
        Train the recommendation system
        
        Args:
            books: List of Book objects from database
            ratings: List of Rating objects from database
        """
        # Prepare books dataframe
        books_data = []
        for book in books:
            authors = json.loads(book.authors) if book.authors else []
            categories = json.loads(book.categories) if book.categories else []
            
            books_data.append({
                'id': book.id,
                'title': book.title,
                'authors': ' '.join(authors),
                'categories': ' '.join(categories),
                'description': book.description or '',
                'is_manga': book.is_manga,
                'is_novel': book.is_novel
            })
        
        self.books_df = pd.DataFrame(books_data)
        
        if len(self.books_df) > 0:
            # Content-based filtering: Create content features
            self.books_df['content'] = (
                self.books_df['title'] + ' ' +
                self.books_df['authors'] + ' ' +
                self.books_df['categories'] + ' ' +
                self.books_df['description']
            )
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.books_df['content'])
            
            # Calculate content-based similarity
            self.content_similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Collaborative filtering: Build user-item matrix
        if ratings:
            ratings_data = [{
                'user_id': r.user_id,
                'book_id': r.book_id,
                'score': r.score
            } for r in ratings]
            
            ratings_df = pd.DataFrame(ratings_data)
            
            # Create pivot table (user-item matrix)
            self.ratings_matrix = ratings_df.pivot_table(
                index='user_id',
                columns='book_id',
                values='score',
                fill_value=0
            )
            
            # Train KNN model for collaborative filtering
            if len(self.ratings_matrix) > 0:
                sparse_matrix = csr_matrix(self.ratings_matrix.values)
                self.knn_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=min(10, len(self.ratings_matrix)))
                self.knn_model.fit(sparse_matrix)
    
    def get_content_based_recommendations(self, book_id, top_n=10):
        """
        Get recommendations based on content similarity
        
        Args:
            book_id: ID of the book to find similar books for
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended book IDs with scores
        """
        if self.books_df is None or self.content_similarity_matrix is None:
            return []
        
        try:
            book_idx = self.books_df[self.books_df['id'] == book_id].index[0]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.content_similarity_matrix[book_idx]))
            
            # Sort by similarity score
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top N similar books (excluding itself)
            sim_scores = sim_scores[1:top_n+1]
            
            # Get book IDs and scores
            book_indices = [i[0] for i in sim_scores]
            recommendations = []
            
            for idx, score in sim_scores:
                book_id = self.books_df.iloc[idx]['id']
                recommendations.append({
                    'book_id': book_id,
                    'score': float(score)
                })
            
            return recommendations
        except (IndexError, KeyError):
            return []
    
    def get_collaborative_recommendations(self, user_id, top_n=10):
        """
        Get recommendations based on collaborative filtering
        
        Args:
            user_id: ID of the user to get recommendations for
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended book IDs with scores
        """
        if self.ratings_matrix is None or self.knn_model is None:
            return []
        
        try:
            # Check if user exists in ratings matrix
            if user_id not in self.ratings_matrix.index:
                return []
            
            user_idx = self.ratings_matrix.index.get_loc(user_id)
            user_ratings = self.ratings_matrix.iloc[user_idx].values.reshape(1, -1)
            
            # Find similar users
            distances, indices = self.knn_model.kneighbors(user_ratings, n_neighbors=min(10, len(self.ratings_matrix)))
            
            # Get books rated highly by similar users but not rated by current user
            similar_users_ratings = self.ratings_matrix.iloc[indices[0]]
            
            # Calculate weighted average of ratings
            weights = 1 - distances[0]  # Convert distance to similarity
            weighted_ratings = np.average(similar_users_ratings, axis=0, weights=weights)
            
            # Get books not yet rated by user
            user_rated_books = self.ratings_matrix.columns[self.ratings_matrix.iloc[user_idx] > 0].tolist()
            
            recommendations = []
            for book_id, score in zip(self.ratings_matrix.columns, weighted_ratings):
                if book_id not in user_rated_books and score > 0:
                    recommendations.append({
                        'book_id': book_id,
                        'score': float(score)
                    })
            
            # Sort by score and return top N
            recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:top_n]
            
            return recommendations
        except (IndexError, KeyError):
            return []
    
    def get_hybrid_recommendations(self, user_id, book_id=None, top_n=10, content_weight=0.5):
        """
        Get hybrid recommendations combining content-based and collaborative filtering
        
        Args:
            user_id: ID of the user to get recommendations for
            book_id: Optional book ID for content-based filtering
            top_n: Number of recommendations to return
            content_weight: Weight for content-based recommendations (0-1)
            
        Returns:
            List of recommended book IDs
        """
        collaborative_weight = 1 - content_weight
        
        # Get recommendations from both methods
        content_recs = []
        if book_id:
            content_recs = self.get_content_based_recommendations(book_id, top_n * 2)
        
        collab_recs = self.get_collaborative_recommendations(user_id, top_n * 2)
        
        # Combine recommendations
        combined_scores = {}
        
        # Add content-based scores
        for rec in content_recs:
            book_id = rec['book_id']
            combined_scores[book_id] = rec['score'] * content_weight
        
        # Add collaborative scores
        for rec in collab_recs:
            book_id = rec['book_id']
            if book_id in combined_scores:
                combined_scores[book_id] += rec['score'] * collaborative_weight
            else:
                combined_scores[book_id] = rec['score'] * collaborative_weight
        
        # Sort by combined score
        recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return [book_id for book_id, score in recommendations]
    
    def get_popular_books(self, top_n=10, is_manga=None, is_novel=None):
        """
        Get popular books based on ratings
        
        Args:
            top_n: Number of books to return
            is_manga: Filter for manga books
            is_novel: Filter for novel books
            
        Returns:
            List of book IDs
        """
        if self.books_df is None:
            return []
        
        df = self.books_df.copy()
        
        # Apply filters
        if is_manga is not None:
            df = df[df['is_manga'] == is_manga]
        if is_novel is not None:
            df = df[df['is_novel'] == is_novel]
        
        # If we have ratings, use them
        if self.ratings_matrix is not None and len(self.ratings_matrix) > 0:
            # Calculate average rating for each book
            book_ratings = self.ratings_matrix.mean(axis=0).sort_values(ascending=False)
            popular_books = [book_id for book_id in book_ratings.index if book_id in df['id'].values][:top_n]
            return popular_books
        
        # Otherwise, return books in order of ID (most recent first)
        return df['id'].tolist()[:top_n]
