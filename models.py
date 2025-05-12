from flask_sqlalchemy import SQLAlchemy
import uuid  # Для генерации уникальных токенов
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    profilePicture = db.Column(db.String(255), default='default_profile_picture.png')

    # Связь с токенами сессий
    tokens = db.relationship('SessionToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.login}>"

class SessionToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))  # UUID для токена
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(hours=24)
    )  # Токен действует 24 часа

    def is_valid(self):
        """Проверяет, действителен ли токен (не истек ли его срок)."""
        return datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f"<SessionToken {self.token[:8]}... for user {self.user_id}>"
