from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Schemas para pagos únicos
class PaymentIntentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Monto en la moneda base (ej: 10.50)")
    currency: str = Field(default="usd", description="Código de moneda (usd, eur, etc.)")
    description: Optional[str] = None
    
class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    
class PaymentResponse(BaseModel):
    id: int
    stripe_payment_intent_id: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para productos
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    currency: str = Field(default="usd")

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    currency: str
    stripe_product_id: Optional[str]
    stripe_price_id: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema para el webhook de Stripe
class StripeWebhookPayload(BaseModel):
    """Payload recibido desde Stripe webhook"""
    pass  # El contenido se procesará como dict raw

# Schema para respuestas de configuración
class StripeConfigResponse(BaseModel):
    publishable_key: str
