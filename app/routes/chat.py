from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from app.models import ChatMessage

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/')
@login_required
def index():
    """Chat page"""
    return render_template('chat/index.html')

@bp.route('/messages/<room>')
@login_required
def get_messages(room):
    """Get chat messages for a room"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = ChatMessage.query.filter_by(room=room).order_by(
        ChatMessage.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    messages = pagination.items
    messages.reverse()  # Show oldest first
    
    return jsonify({
        'messages': [m.to_dict() for m in messages],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

# Socket.IO event handlers
@socketio.on('join')
def on_join(data):
    """User joins a chat room"""
    room = data.get('room', 'general')
    username = current_user.username if current_user.is_authenticated else 'Anonymous'
    
    join_room(room)
    emit('user_joined', {
        'username': username,
        'room': room,
        'message': f'{username} has joined the room.'
    }, room=room)

@socketio.on('leave')
def on_leave(data):
    """User leaves a chat room"""
    room = data.get('room', 'general')
    username = current_user.username if current_user.is_authenticated else 'Anonymous'
    
    leave_room(room)
    emit('user_left', {
        'username': username,
        'room': room,
        'message': f'{username} has left the room.'
    }, room=room)

@socketio.on('send_message')
def on_send_message(data):
    """User sends a message in a chat room"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'You must be logged in to send messages'})
        return
    
    room = data.get('room', 'general')
    message = data.get('message', '').strip()
    
    if not message:
        emit('error', {'message': 'Message cannot be empty'})
        return
    
    # Save message to database
    chat_message = ChatMessage(
        user_id=current_user.id,
        room=room,
        message=message
    )
    
    db.session.add(chat_message)
    db.session.commit()
    
    # Broadcast message to room
    emit('new_message', chat_message.to_dict(), room=room)

@socketio.on('typing')
def on_typing(data):
    """User is typing"""
    if not current_user.is_authenticated:
        return
    
    room = data.get('room', 'general')
    emit('user_typing', {
        'username': current_user.username,
        'room': room
    }, room=room, include_self=False)
