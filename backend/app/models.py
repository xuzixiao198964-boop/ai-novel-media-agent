from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class SubscriptionTier(str, enum.Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    subscription_tier = Column(String(20), default="basic")
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="user")
    novels = relationship("Novel", back_populates="user")
    videos = relationship("Video", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    current_agent = Column(String(100))
    input_data = Column(JSON)
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="tasks")

class Novel(Base):
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    genre = Column(String(50))
    category = Column(String(50))
    word_count = Column(Integer, default=0)
    outline = Column(Text)
    content = Column(Text)
    content_path = Column(String(500))
    status = Column(String(20), default="draft")
    is_public = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="novels")

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    source_type = Column(String(50))
    video_type = Column(String(50))
    episode_count = Column(Integer, default=1)
    file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    duration = Column(Integer)
    status = Column(String(20), default="draft")
    is_public = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="videos")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(50))
    payment_method = Column(String(50))
    status = Column(String(20), default="pending")
    transaction_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)

    user = relationship("User", back_populates="payments")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    permissions = Column(JSON)
    rate_limit = Column(Integer, default=100)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)

    user = relationship("User", back_populates="api_keys")

class PublishRecord(Base):
    __tablename__ = "publish_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_type = Column(String(20))
    content_id = Column(Integer)
    content_title = Column(String(200))
    platform = Column(String(50))
    status = Column(String(20), default="pending")
    platform_id = Column(String(100))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20))
    module = Column(String(100))
    message = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    log_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
