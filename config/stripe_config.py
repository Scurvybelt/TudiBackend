import os
from dotenv import load_dotenv

load_dotenv()

#No me esta funcionanod sacarlos datos secretos desde env.example

class StripeConfig:
    """Configuración de Stripe"""
    STRIPE_PUBLISHABLE_KEY = 'pk_test_51RmmOGI2kaQuXy0UkoZbpvXBVlxrWI0cUVmQM6jmO9WYEx5QM57jdwzDGwlvN8JGLfz0Yb6p2TZgrIQhZOppuBby00Enwema0u'
    STRIPE_SECRET_KEY = 'sk_test_51RmmOGI2kaQuXy0UEkisepr7h7aatQf8aNtECiy2wPmsdCkxJ27G2e6lmeoV4361RMiI3IEXKT5QausEwyPnHq1j000xD0Hygt'
    # STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # URLs del frontend (ajusta según tu aplicación)
    SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/success")
    CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/cancel")
    
    @classmethod
    def validate_config(cls):
        """Valida que todas las variables de entorno necesarias estén configuradas"""
        if not cls.STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SECRET_KEY no está configurada en las variables de entorno")
        if not cls.STRIPE_PUBLISHABLE_KEY:
            raise ValueError("STRIPE_PUBLISHABLE_KEY no está configurada en las variables de entorno")
        return True
