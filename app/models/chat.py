from app import db
from datetime import datetime

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    room = db.Column(db.String(100), default='general', index=True)  # general, manga, novel, etc.
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'room': self.room,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} by User {self.user_id}>'
