from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Book, Review, Rating

bp = Blueprint('reviews', __name__)

@bp.route('/books/<int:book_id>/reviews')
def get_reviews(book_id):
    """Get all reviews for a book"""
    book = Book.query.get_or_404(book_id)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    pagination = Review.query.filter_by(book_id=book_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    reviews = pagination.items
    
    if request.is_json:
        return jsonify({
            'reviews': [{
                'id': r.id,
                'user': {
                    'id': r.user.id,
                    'username': r.user.username
                },
                'title': r.title,
                'content': r.content,
                'likes_count': r.likes_count,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat()
            } for r in reviews],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('reviews/list.html', reviews=reviews, book=book, pagination=pagination)

@bp.route('/books/<int:book_id>/reviews', methods=['POST'])
@login_required
def create_review(book_id):
    """Create a new review for a book"""
    book = Book.query.get_or_404(book_id)
    
    data = request.get_json() if request.is_json else request.form
    
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': 'Review content is required'}), 400
    
    # Check if user already reviewed this book
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if existing_review:
        return jsonify({'error': 'You have already reviewed this book'}), 400
    
    review = Review(
        user_id=current_user.id,
        book_id=book_id,
        title=title,
        content=content
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': {
            'id': review.id,
            'title': review.title,
            'content': review.content,
            'created_at': review.created_at.isoformat()
        }
    }), 201

@bp.route('/reviews/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    """Update a review"""
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() if request.is_json else request.form
    
    if 'title' in data:
        review.title = data['title']
    if 'content' in data:
        review.content = data['content']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': {
            'id': review.id,
            'title': review.title,
            'content': review.content,
            'updated_at': review.updated_at.isoformat()
        }
    }), 200

@bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """Delete a review"""
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200

@bp.route('/books/<int:book_id>/rating', methods=['POST', 'PUT'])
@login_required
def rate_book(book_id):
    """Rate a book (1-5 stars)"""
    book = Book.query.get_or_404(book_id)
    
    data = request.get_json() if request.is_json else request.form
    score = data.get('score')
    
    if not score:
        return jsonify({'error': 'Rating score is required'}), 400
    
    try:
        score = int(score)
        if score < 1 or score > 5:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Rating score must be between 1 and 5'}), 400
    
    # Check if user already rated this book
    rating = Rating.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if rating:
        # Update existing rating
        rating.score = score
        message = 'Rating updated successfully'
    else:
        # Create new rating
        rating = Rating(
            user_id=current_user.id,
            book_id=book_id,
            score=score
        )
        db.session.add(rating)
        message = 'Rating created successfully'
    
    db.session.commit()
    
    # Update book's average rating
    book.update_average_rating()
    db.session.commit()
    
    return jsonify({
        'message': message,
        'rating': {
            'score': rating.score,
            'book_average': book.average_rating,
            'book_ratings_count': book.ratings_count
        }
    }), 200

@bp.route('/books/<int:book_id>/rating', methods=['DELETE'])
@login_required
def delete_rating(book_id):
    """Delete a book rating"""
    book = Book.query.get_or_404(book_id)
    
    rating = Rating.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if not rating:
        return jsonify({'error': 'Rating not found'}), 404
    
    db.session.delete(rating)
    db.session.commit()
    
    # Update book's average rating
    book.update_average_rating()
    db.session.commit()
    
    return jsonify({'message': 'Rating deleted successfully'}), 200
