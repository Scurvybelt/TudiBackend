from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class CoursePhaseStatus(enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Relación con pagos
    payments = relationship("Payment", back_populates="user")
    # Relación con progreso del curso
    course_progress = relationship("UserCourseProgress", back_populates="user")
    

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_payment_intent_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), nullable=True)
    amount = Column(Float)  # Cantidad en la moneda base (ej: 10.50 para $10.50)
    currency = Column(String(3), default="usd")  # usd, eur, etc.
    status = Column(String(50))  # pending, succeeded, failed, canceled
    description = Column(String(255), nullable=True)
    payment_method_types = Column(String(50), nullable=True)  # oxxo, bank_transfer, card, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario
    user = relationship("User", back_populates="payments")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(Float)  # Precio en la moneda base
    currency = Column(String(3), default="usd")
    stripe_product_id = Column(String(255), unique=True, nullable=True)
    stripe_price_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class CoursePhase(Base):
    __tablename__ = "course_phases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    phase_order = Column(Integer, unique=True)  # Orden secuencial de las fases (1, 2, 3, etc.)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con progreso del usuario
    user_progress = relationship("UserCourseProgress", back_populates="phase")

class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phase_id = Column(Integer, ForeignKey("course_phases.id"))
    status = Column(Enum(CoursePhaseStatus), default=CoursePhaseStatus.LOCKED)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    progress_percentage = Column(Float, default=0.0)  # 0-100 para progreso dentro de la fase
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="course_progress")
    phase = relationship("CoursePhase", back_populates="user_progress")
    
    # Índice único para evitar duplicados
    __table_args__ = (
        {"extend_existing": True}
    )