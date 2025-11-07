from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import ForumPost, ForumComment

bp = Blueprint('forum', __name__, url_prefix='/forum')

@bp.route('/')
def index():
    """List all forum posts"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category = request.args.get('category')
    
    query = ForumPost.query
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(
        ForumPost.is_pinned.desc(),
        ForumPost.updated_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    posts = pagination.items
    
    if request.is_json:
        return jsonify({
            'posts': [{
                'id': p.id,
                'title': p.title,
                'author': {
                    'id': p.author.id,
                    'username': p.author.username
                },
                'category': p.category,
                'views_count': p.views_count,
                'likes_count': p.likes_count,
                'comments_count': p.comments.count(),
                'is_pinned': p.is_pinned,
                'is_locked': p.is_locked,
                'created_at': p.created_at.isoformat(),
                'updated_at': p.updated_at.isoformat()
            } for p in posts],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('forum/index.html', posts=posts, pagination=pagination)

@bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    """Create a new forum post"""
    data = request.get_json() if request.is_json else request.form
    
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', 'general')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    post = ForumPost(
        user_id=current_user.id,
        title=title,
        content=content,
        category=category
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'message': 'Post created successfully',
        'post': {
            'id': post.id,
            'title': post.title,
            'category': post.category,
            'created_at': post.created_at.isoformat()
        }
    }), 201

@bp.route('/posts/<int:post_id>')
def get_post(post_id):
    """Get a forum post with comments"""
    post = ForumPost.query.get_or_404(post_id)
    
    # Increment view count
    post.views_count += 1
    db.session.commit()
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    pagination = ForumComment.query.filter_by(post_id=post_id).order_by(
        ForumComment.created_at.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    comments = pagination.items
    
    if request.is_json:
        return jsonify({
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': {
                    'id': post.author.id,
                    'username': post.author.username
                },
                'category': post.category,
                'views_count': post.views_count,
                'likes_count': post.likes_count,
                'is_pinned': post.is_pinned,
                'is_locked': post.is_locked,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            },
            'comments': [{
                'id': c.id,
                'author': {
                    'id': c.author.id,
                    'username': c.author.username
                },
                'content': c.content,
                'likes_count': c.likes_count,
                'created_at': c.created_at.isoformat()
            } for c in comments],
            'total_comments': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('forum/post.html', post=post, comments=comments, pagination=pagination)

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """Update a forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if post.is_locked and not current_user.is_admin:
        return jsonify({'error': 'Post is locked'}), 403
    
    data = request.get_json() if request.is_json else request.form
    
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    if 'category' in data:
        post.category = data['category']
    
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'}), 200

@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete a forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def create_comment(post_id):
    """Create a comment on a forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    if post.is_locked and not current_user.is_admin:
        return jsonify({'error': 'Post is locked'}), 403
    
    data = request.get_json() if request.is_json else request.form
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Comment content is required'}), 400
    
    comment = ForumComment(
        post_id=post_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment created successfully',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        }
    }), 201

@bp.route('/comments/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """Update a forum comment"""
    comment = ForumComment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() if request.is_json else request.form
    content = data.get('content')
    
    if content:
        comment.content = content
        db.session.commit()
        return jsonify({'message': 'Comment updated successfully'}), 200
    
    return jsonify({'error': 'Comment content is required'}), 400

@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a forum comment"""
    comment = ForumComment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200
