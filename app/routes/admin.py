from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Book, Review, ForumPost, ForumComment, Rating
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required', 'error')
            return redirect(url_for('books.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_books = Book.query.count()
    total_reviews = Review.query.count()
    total_ratings = Rating.query.count()
    total_forum_posts = ForumPost.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_books': total_books,
        'total_reviews': total_reviews,
        'total_ratings': total_ratings,
        'total_forum_posts': total_forum_posts
    }
    
    if request.is_json:
        return jsonify({
            'stats': stats,
            'recent_users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'created_at': u.created_at.isoformat()
            } for u in recent_users],
            'recent_books': [{
                'id': b.id,
                'title': b.title,
                'created_at': b.created_at.isoformat()
            } for b in recent_books]
        }), 200
    
    return render_template('admin/dashboard.html', stats=stats, 
                          recent_users=recent_users, recent_books=recent_books)

@bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = pagination.items
    
    if request.is_json:
        return jsonify({
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat(),
                'last_login': u.last_login.isoformat() if u.last_login else None
            } for u in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('admin/users.html', users=users, pagination=pagination)

@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'message': f'User admin status updated',
        'is_admin': user.is_admin
    }), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@bp.route('/books')
@login_required
@admin_required
def list_books():
    """List all books for management"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = Book.query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = pagination.items
    
    if request.is_json:
        return jsonify({
            'books': [{
                'id': b.id,
                'title': b.title,
                'is_manga': b.is_manga,
                'is_novel': b.is_novel,
                'average_rating': b.average_rating,
                'ratings_count': b.ratings_count,
                'created_at': b.created_at.isoformat()
            } for b in books],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('admin/books.html', books=books, pagination=pagination)

@bp.route('/books/<int:book_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get_or_404(book_id)
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'}), 200

@bp.route('/books/<int:book_id>/toggle-type', methods=['POST'])
@login_required
@admin_required
def toggle_book_type(book_id):
    """Toggle book type (manga/novel)"""
    book = Book.query.get_or_404(book_id)
    
    data = request.get_json() if request.is_json else request.form
    book_type = data.get('type')  # 'manga' or 'novel'
    
    if book_type == 'manga':
        book.is_manga = not book.is_manga
    elif book_type == 'novel':
        book.is_novel = not book.is_novel
    else:
        return jsonify({'error': 'Invalid book type'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book type updated',
        'is_manga': book.is_manga,
        'is_novel': book.is_novel
    }), 200

@bp.route('/forum/posts')
@login_required
@admin_required
def list_forum_posts():
    """List all forum posts for moderation"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = ForumPost.query.order_by(ForumPost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts = pagination.items
    
    if request.is_json:
        return jsonify({
            'posts': [{
                'id': p.id,
                'title': p.title,
                'author': p.author.username,
                'category': p.category,
                'is_pinned': p.is_pinned,
                'is_locked': p.is_locked,
                'created_at': p.created_at.isoformat()
            } for p in posts],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('admin/forum_posts.html', posts=posts, pagination=pagination)

@bp.route('/forum/posts/<int:post_id>/pin', methods=['POST'])
@login_required
@admin_required
def pin_post(post_id):
    """Pin/unpin a forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    post.is_pinned = not post.is_pinned
    db.session.commit()
    
    return jsonify({
        'message': 'Post pin status updated',
        'is_pinned': post.is_pinned
    }), 200

@bp.route('/forum/posts/<int:post_id>/lock', methods=['POST'])
@login_required
@admin_required
def lock_post(post_id):
    """Lock/unlock a forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    post.is_locked = not post.is_locked
    db.session.commit()
    
    return jsonify({
        'message': 'Post lock status updated',
        'is_locked': post.is_locked
    }), 200
