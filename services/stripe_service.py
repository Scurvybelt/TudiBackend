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




    def create_payment_intent_transfer(self, db: Session, user: User, amount: float,
                                        currency: str, description: str = None,
                                        return_url: str = None):
        """
        Crear Payment Intent para transferencia bancaria
        """
        try:

            amount_cents = int(amount * 100)
            # Crear o obtener customer de Stripe
            customer_id = self.create_or_get_customer(db, user)
            
            # Configurar parámetros específicos para transferencia
            intent_params = {
                'amount': amount_cents,
                'currency': currency,
                'customer': customer_id,
                'payment_method_types': ['customer_balance'],
                'payment_method_data': {
                    'type': 'customer_balance'
                },
                'confirm': True,  # Confirmar inmediatamente
                'metadata': {
                    'user_id': str(user.id),
                    'description': description or 'Pago por transferencia'
                }
            }
            
            # Agregar return_url si se proporciona
            if return_url:
                intent_params['return_url'] = return_url
                
            # Agregar customer_details
            intent_params['payment_method_options'] = {
                'customer_balance': {
                    'funding_type': 'bank_transfer',
                    'bank_transfer': {
                        'type': 'mx_bank_transfer'  
                    }
                }
            }
            
             # Crear Payment Intent
            payment_intent = stripe.PaymentIntent.create(**intent_params)
            
            payment = Payment(
                user_id=user.id,
                stripe_payment_intent_id=payment_intent.id,
                stripe_customer_id=customer_id,
                amount=amount,
                currency=currency,
                status=payment_intent.status,
                payment_method_types='customer_balance',
                description=description
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            # Preparar respuesta para el frontend
            response = {
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'status': payment_intent.status,
                'amount': amount,
                'currency': currency,
                'payment_method_types': ['customer_balance']
            }

            # Extraer información de transferencia bancaria si está disponible
            if payment_intent.next_action and payment_intent.next_action.get('display_bank_transfer_instructions'):
                bank_instructions = payment_intent.next_action['display_bank_transfer_instructions']
                
                response.update({
                    'bank_transfer_details': {
                        'reference': bank_instructions.get('reference'),
                        'amount_remaining': bank_instructions.get('amount_remaining'),
                        'hosted_instructions_url': bank_instructions.get('hosted_instructions_url'),
                        'financial_addresses': bank_instructions.get('financial_addresses', [])
                    },
                    'next_action_type': payment_intent.next_action.get('type')
                })
                
                # Información específica de SPEI si está disponible
                financial_addresses = bank_instructions.get('financial_addresses', [])
                if financial_addresses:
                    spei_info = financial_addresses[0].get('spei', {})
                    if spei_info:
                        response['spei_details'] = {
                            'clabe': spei_info.get('clabe'),
                            'bank_name': spei_info.get('bank_name'),
                            'account_holder_name': spei_info.get('account_holder_name'),
                            'reference': bank_instructions.get('reference')
                        }

            return response
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error in transfer payment: {e}")
            raise HTTPException(status_code=400, detail=f"Error de Stripe: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating transfer payment intent: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    def create_payment_intent(self, db: Session, user: User, amount: float,
                              currency: str = "mxn", description: str = None,
                              payment_method_types: str = "card") -> Dict[str, Any]:
        try:
            # Convertir amount a centavos (Stripe usa centavos)
            amount_cents = int(amount * 100)
            # Crear o obtener customer
            customer_id = self.create_or_get_customer(db, user)
            # Determinar el tipo de método de pago
            method_type = payment_method_types[0].lower()
            
            # Crear Payment Intent con el método de pago específico
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                customer=customer_id,
                description=description,
                payment_method_types=[method_type],
                metadata={
                    "user_id": user.id,
                    "user_email": user.email
                }
            )
            # print(f"Payment_intent {payment_intent}")
            # Guardar en la base de datos
            db_payment = Payment(
                user_id=user.id,
                stripe_payment_intent_id=payment_intent.id,
                stripe_customer_id=customer_id,
                amount=amount,
                currency=currency,
                status="pending",
                description=description,
                payment_method_types=method_type
            )
            db.add(db_payment)
            db.commit()
            db.refresh(db_payment)
            # Preparar respuesta dinámica
            response = {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount,
                "currency": currency,
                "payment_method_types": method_type
            }
            # Metodos de pago oxxo y bank_transfer
            if method_type in ["oxxo", "bank_transfer"]:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent.id)
                if method_type == "oxxo" and payment_intent.next_action:
                    oxxo_details = payment_intent.next_action.get("oxxo_display_details")
                    if oxxo_details:
                        response["oxxo_voucher_url"] = oxxo_details.get("hosted_voucher_url")
                        response["oxxo_barcode"] = oxxo_details.get("number")
                        response["oxxo_expires_at"] = oxxo_details.get("expires_at")
                if method_type == "bank_transfer" and payment_intent.next_action:
                    # print("Entro a bank transfer")
                    bank_details = payment_intent.next_action.get("display_bank_transfer_instructions")
                    if bank_details:
                        response["bank_transfer_details"] = bank_details.get("financial_addresses")
            return response
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
