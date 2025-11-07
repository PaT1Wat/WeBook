from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Book, Rating
from app.ml import HybridRecommender
import json

bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')

# Global recommender instance
recommender = HybridRecommender()

@bp.route('/train', methods=['POST'])
@login_required
def train_recommender():
    """Train the recommendation system (admin only or periodic task)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    books = Book.query.all()
    ratings = Rating.query.all()
    
    recommender.fit(books, ratings)
    
    return jsonify({'message': 'Recommender trained successfully'}), 200

@bp.route('/for-you')
@login_required
def get_recommendations():
    """Get personalized recommendations for current user"""
    # Train recommender if not already trained
    if recommender.books_df is None:
        books = Book.query.all()
        ratings = Rating.query.all()
        recommender.fit(books, ratings)
    
    # Get user's most recent highly rated book for content-based filtering
    recent_rating = Rating.query.filter_by(user_id=current_user.id).filter(
        Rating.score >= 4
    ).order_by(Rating.created_at.desc()).first()
    
    book_id = recent_rating.book_id if recent_rating else None
    
    # Get hybrid recommendations
    recommended_ids = recommender.get_hybrid_recommendations(
        user_id=current_user.id,
        book_id=book_id,
        top_n=20
    )
    
    # If no recommendations from ML, get popular books
    if not recommended_ids:
        recommended_ids = recommender.get_popular_books(top_n=20)
    
    # Fetch book objects
    books = []
    if recommended_ids:
        books = Book.query.filter(Book.id.in_(recommended_ids)).all()
        # Sort by recommendation order
        book_dict = {b.id: b for b in books}
        books = [book_dict[book_id] for book_id in recommended_ids if book_id in book_dict]
    
    if request.is_json:
        return jsonify({
            'recommendations': [{
                'id': b.id,
                'title': b.title,
                'authors': json.loads(b.authors) if b.authors else [],
                'thumbnail_url': b.thumbnail_url,
                'average_rating': b.average_rating,
                'is_manga': b.is_manga,
                'is_novel': b.is_novel
            } for b in books]
        }), 200
    
    return render_template('recommendations/for_you.html', books=books)

@bp.route('/similar/<int:book_id>')
def get_similar_books(book_id):
    """Get books similar to a given book"""
    book = Book.query.get_or_404(book_id)
    
    # Train recommender if not already trained
    if recommender.books_df is None:
        books = Book.query.all()
        ratings = Rating.query.all()
        recommender.fit(books, ratings)
    
    # Get content-based recommendations
    recommendations = recommender.get_content_based_recommendations(book_id, top_n=20)
    
    if not recommendations:
        # Fallback to books in same categories
        categories = json.loads(book.categories) if book.categories else []
        if categories:
            similar_books = Book.query.filter(
                Book.id != book_id,
                Book.categories.contains(categories[0])
            ).limit(20).all()
        else:
            similar_books = []
    else:
        recommended_ids = [r['book_id'] for r in recommendations]
        similar_books = Book.query.filter(Book.id.in_(recommended_ids)).all()
        # Sort by recommendation order
        book_dict = {b.id: b for b in similar_books}
        similar_books = [book_dict[book_id] for book_id in recommended_ids if book_id in book_dict]
    
    if request.is_json:
        return jsonify({
            'similar_books': [{
                'id': b.id,
                'title': b.title,
                'authors': json.loads(b.authors) if b.authors else [],
                'thumbnail_url': b.thumbnail_url,
                'average_rating': b.average_rating,
                'is_manga': b.is_manga,
                'is_novel': b.is_novel
            } for b in similar_books]
        }), 200
    
    return render_template('recommendations/similar.html', book=book, similar_books=similar_books)

@bp.route('/popular')
def get_popular():
    """Get popular books"""
    category = request.args.get('category')  # 'manga', 'novel', or None
    top_n = int(request.args.get('top_n', 20))
    
    # Train recommender if not already trained
    if recommender.books_df is None:
        books = Book.query.all()
        ratings = Rating.query.all()
        recommender.fit(books, ratings)
    
    is_manga = None
    is_novel = None
    
    if category == 'manga':
        is_manga = True
    elif category == 'novel':
        is_novel = True
    
    popular_ids = recommender.get_popular_books(
        top_n=top_n,
        is_manga=is_manga,
        is_novel=is_novel
    )
    
    books = []
    if popular_ids:
        books = Book.query.filter(Book.id.in_(popular_ids)).all()
        # Sort by recommendation order
        book_dict = {b.id: b for b in books}
        books = [book_dict[book_id] for book_id in popular_ids if book_id in book_dict]
    
    if request.is_json:
        return jsonify({
            'popular_books': [{
                'id': b.id,
                'title': b.title,
                'authors': json.loads(b.authors) if b.authors else [],
                'thumbnail_url': b.thumbnail_url,
                'average_rating': b.average_rating,
                'ratings_count': b.ratings_count,
                'is_manga': b.is_manga,
                'is_novel': b.is_novel
            } for b in books]
        }), 200
    
    return render_template('recommendations/popular.html', books=books, category=category)
