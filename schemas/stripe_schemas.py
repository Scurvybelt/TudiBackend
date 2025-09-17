from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List

# Schemas para pagos únicos
class PaymentIntentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Monto en la moneda base (ej: 10.50)")
    currency: str = Field(default="usd", description="Código de moneda (usd, eur, etc.)")
    description: Optional[str] = None
    payment_method_types: List[str] = Field(..., description="Lista de métodos de pago (ej: ['oxxo'], ['card'])")
    
class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    payment_method_types: str
    status: Optional[str] = None
    description: Optional[str] = None
    # Campos opcionales para OXXO y transferencia
    oxxo_voucher_url: Optional[str] = None
    oxxo_barcode: Optional[str] = None
    oxxo_expires_at: Optional[int] = None
    bank_transfer_details: Optional[dict] = None

    # Campos opcionales generales de Stripe
    next_action: Optional[dict] = None
    receipt_url: Optional[str] = None
    created: Optional[int] = None
    customer: Optional[str] = None
    metadata: Optional[dict] = None
    
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
