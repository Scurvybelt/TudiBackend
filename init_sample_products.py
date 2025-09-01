"""
Script para inicializar productos de ejemplo en la base de datos
Solo productos de pago único (sin suscripciones)
Ejecutar después de configurar las variables de entorno de Stripe
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product
from services.stripe_service import stripe_service

def create_sample_products():
    """Crear productos de ejemplo"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen productos
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print("Ya existen productos en la base de datos.")
            return
        
        # Productos de ejemplo (solo pagos únicos)
        sample_products = [
            {
                "name": "Curso Básico",
                "description": "Curso introductorio completo",
                "price": 29.99,
                "currency": "usd"
            },
            {
                "name": "Curso Intermedio",
                "description": "Curso de nivel intermedio con proyectos prácticos",
                "price": 59.99,
                "currency": "usd"
            },
            {
                "name": "Curso Premium",
                "description": "Curso avanzado con certificación y mentoría",
                "price": 99.99,
                "currency": "usd"
            },
            {
                "name": "Pack Completo",
                "description": "Todos los cursos incluidos con material extra",
                "price": 149.99,
                "currency": "usd"
            }
        ]
        
        for product_data in sample_products:
            try:
                # Crear producto en Stripe
                stripe_data = stripe_service.create_product_in_stripe(db, product_data)
                
                # Crear producto en la base de datos
                db_product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    currency=product_data["currency"],
                    stripe_product_id=stripe_data["stripe_product_id"],
                    stripe_price_id=stripe_data["stripe_price_id"]
                )
                
                db.add(db_product)
                print(f"✓ Producto creado: {product_data['name']} - ${product_data['price']}")
                
            except Exception as e:
                print(f"✗ Error creando producto {product_data['name']}: {e}")
        
        db.commit()
        print("\n¡Productos de ejemplo creados exitosamente!")
        print("Ahora puedes usar estos productos en tu aplicación para crear Payment Intents.")
        
    except Exception as e:
        print(f"Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creando productos de ejemplo para pagos únicos...")
    create_sample_products()
