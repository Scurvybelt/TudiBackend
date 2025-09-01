import stripe
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from config.stripe_config import StripeConfig
from models import Payment, Product, User
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        """Inicializar el servicio de Stripe"""
        StripeConfig.validate_config()
        stripe.api_key = StripeConfig.STRIPE_SECRET_KEY
        
    def get_publishable_key(self) -> str:
        """Obtener la clave pública de Stripe"""
        return StripeConfig.STRIPE_PUBLISHABLE_KEY

    def create_or_get_customer(self, db: Session, user: User) -> str:
        """
        Crear o obtener un customer de Stripe para el usuario
        """
        try:
            # Buscar si ya existe un customer
            payment = db.query(Payment).filter(
                Payment.user_id == user.id,
                Payment.stripe_customer_id.isnot(None)
            ).first()
            
            if payment and payment.stripe_customer_id:
                return payment.stripe_customer_id
                
            # Crear nuevo customer en Stripe
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.name} {user.last_name}",
                metadata={"user_id": user.id}
            )
            
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise HTTPException(status_code=400, detail=f"Error creando customer: {str(e)}")

    def create_payment_intent(self, db: Session ,user: User, amount: float, 
                            currency: str = "usd", description: str = None) -> Dict[str, Any]:
       
        try:
            
            # Convertir amount a centavos (Stripe usa centavos)
            amount_cents = int(amount * 100)
            
            # Crear o obtener customer
            customer_id = self.create_or_get_customer(db, user)
            
            # Crear Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                customer=customer_id,
                description=description,
                automatic_payment_methods={"enabled": True},
                metadata={
                    "user_id": user.id,
                    "user_email": user.email
                }
            )
            
            #Guardar en la base de datos
            db_payment = Payment(
                user_id=user.id,
                stripe_payment_intent_id=payment_intent.id,
                stripe_customer_id=customer_id,
                amount=amount,
                currency=currency,
                status="pending",
                description=description
            )
            db.add(db_payment)
            db.commit()
            db.refresh(db_payment)
            
            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount,
                "currency": currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating payment intent: {e}")
            raise HTTPException(status_code=400, detail=f"Error creando pago: {str(e)}")

    def handle_webhook_event(self, db: Session, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Manejar eventos de webhook de Stripe
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, StripeConfig.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Manejar el evento
        if event["type"] == "payment_intent.succeeded":
            self._handle_payment_succeeded(db, event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            self._handle_payment_failed(db, event["data"]["object"])
        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return {"status": "success"}

    def _handle_payment_succeeded(self, db: Session, payment_intent: Dict[str, Any]):
        """Manejar pago exitoso"""
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent["id"]
        ).first()
        
        if payment:
            payment.status = "succeeded"
            payment.updated_at = datetime.utcnow()
            db.commit()

    def _handle_payment_failed(self, db: Session, payment_intent: Dict[str, Any]):
        """Manejar pago fallido"""
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent["id"]
        ).first()
        
        if payment:
            payment.status = "failed"
            payment.updated_at = datetime.utcnow()
            db.commit()

    # Métodos para productos
    def create_product_in_stripe(self, db: Session, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crear producto y precio en Stripe
        """
        try:
            # Crear producto en Stripe
            stripe_product = stripe.Product.create(
                name=product_data["name"],
                description=product_data.get("description"),
                metadata={"created_from_api": "true"}
            )
            
            # Crear precio para pago único
            stripe_price = stripe.Price.create(
                unit_amount=int(product_data["price"] * 100),  # Convertir a centavos
                currency=product_data.get("currency", "usd"),
                product=stripe_product.id,
            )
            
            return {
                "stripe_product_id": stripe_product.id,
                "stripe_price_id": stripe_price.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating product in Stripe: {e}")
            raise HTTPException(status_code=400, detail=f"Error creando producto: {str(e)}")

# Instancia global del servicio
stripe_service = StripeService()
