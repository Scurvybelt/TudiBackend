from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Payment, Product
from schemas.stripe_schemas import (
    PaymentIntentCreate, PaymentIntentResponse, PaymentResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    StripeConfigResponse
)
from services.stripe_service import stripe_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

# Configuración
@router.get("/config", response_model=StripeConfigResponse)
def get_stripe_config():
    """
    Obtener la clave pública de Stripe para el frontend
    """
    return StripeConfigResponse(
        publishable_key=stripe_service.get_publishable_key()
    )



@router.post("/create-payment-intent-transfer")
def create_payment_intent_transfer(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un Payment Intent para transferencia bancaria (customer_balance)
    Se confirma automáticamente en el backend
    """
    # Validar que el tipo de pago sea customer_balance
    if 'customer_balance' not in payment_data.payment_method_types:
        raise HTTPException(
            status_code=400, 
            detail="Este endpoint solo acepta pagos por customer_balance"
        )
    
    try:
        return stripe_service.create_payment_intent_transfer(
            db=db,
            user=current_user,
            amount=payment_data.amount,
            currency=payment_data.currency,
            description=payment_data.description,
            return_url=getattr(payment_data, 'return_url', None)
        )
    except Exception as e:
        logger.error(f"Error creating transfer payment intent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Pagos únicos
@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un Payment Intent para un pago único
    Usar con Stripe Elements en el frontend
    """
    return stripe_service.create_payment_intent(
        db=db,
        user=current_user,
        amount=payment_data.amount,
        currency=payment_data.currency,
        description=payment_data.description,
        payment_method_types=payment_data.payment_method_types
        
    )

@router.get("/payment-history", response_model=List[PaymentResponse])
def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de pagos del usuario
    """
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()
    return payments

@router.get("/payment/{payment_intent_id}", response_model=PaymentResponse)
def get_payment_by_id(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un pago específico por ID
    """
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return payment

# Productos (para administradores)
@router.post("/products", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Implementar si necesitas admin
):
    """
    Crear un nuevo producto (solo administradores)
    """
    try:
        # Crear producto en Stripe
        stripe_data = stripe_service.create_product_in_stripe(db, product_data.dict())
        
        # Crear producto en la base de datos
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            currency=product_data.currency,
            stripe_product_id=stripe_data["stripe_product_id"],
            stripe_price_id=stripe_data["stripe_price_id"]
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return db_product
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=400, detail=f"Error creando producto: {str(e)}")

@router.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """
    Listar todos los productos activos
    """
    products = db.query(Product).filter(Product.is_active == True).all()
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtener un producto específico
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin_user)  # Implementar si necesitas admin
):
    """
    Actualizar un producto (solo administradores)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizar campos
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

# Verificar si el usuario tiene un pago activo
@router.get("/has-paid")
def has_paid(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar si el usuario tiene al menos un pago exitoso (status = 'succeeded')
    """
    try:
        # Buscar si el usuario tiene al menos un pago con status 'succeeded'
        payment = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.status == "succeeded"
        ).first()
        
        has_active_payment = payment is not None
        
        logger.info(f"User {current_user.email} payment check: {has_active_payment}")
        
        return {
            "has_paid": has_active_payment,
            "user_id": current_user.id,
            "email": current_user.email
        }
        
    except Exception as e:
        logger.error(f"Error checking payment status for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error verificando estado de pago"
        )

# Webhook de Stripe
@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recibir webhooks de Stripe
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        return stripe_service.handle_webhook_event(db, payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
