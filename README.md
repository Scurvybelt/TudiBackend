# Tudi Backend - API con Integración de Stripe

API backend desarrollada con FastAPI que incluye autenticación de usuarios y sistema completo de pagos con Stripe.

## Características

- ✅ Autenticación JWT
- ✅ Registro y login de usuarios
- ✅ Recuperación de contraseña por email
- ✅ Pagos únicos con Stripe
- ✅ Gestión de productos
- ✅ Webhooks de Stripe
- ✅ Componentes embebidos de Stripe

## Estructura del Proyecto

```
BackendTudi/
├── config/
│   └── stripe_config.py          # Configuración de Stripe
├── routers/
│   ├── auth.py                   # Endpoints de autenticación
│   └── payments.py               # Endpoints de pagos
├── services/
│   ├── auth_service.py           # Lógica de autenticación
│   └── stripe_service.py         # Lógica de Stripe
├── schemas/
│   ├── user.py                   # Schemas de usuarios
│   └── stripe_schemas.py         # Schemas de pagos
├── utils/
│   └── dependencies.py           # Dependencias comunes
├── models.py                     # Modelos de base de datos
├── database.py                   # Configuración de base de datos
├── main.py                       # Aplicación principal
└── requirements.txt              # Dependencias
```

## Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y configura:

```bash
# Stripe (obtener desde https://dashboard.stripe.com)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost/tudi_db

# JWT
SECRET_KEY=tu_secret_key_aqui
```

### 3. Configurar base de datos
```bash
# Crear la base de datos
psql -U postgres
CREATE DATABASE tudi_db;

# Ejecutar migraciones (las tablas se crean automáticamente)
# O ejecutar manualmente:
psql -U usuario -d tudi_db -f create_payment_tables.sql
```

### 4. Configurar Stripe Webhook
1. Ve a https://dashboard.stripe.com/webhooks
2. Crea endpoint: `https://tudominio.com/payments/stripe-webhook`
3. Selecciona eventos:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`

### 5. Inicializar productos de ejemplo (opcional)
```bash
python init_sample_products.py
```

## Ejecutar la aplicación

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000
Documentación: http://localhost:8000/docs

## Endpoints Principales

### Autenticación
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Login
- `POST /auth/request-password-reset` - Solicitar reset de contraseña
- `POST /auth/reset-password` - Resetear contraseña

### Pagos
- `GET /payments/config` - Obtener clave pública de Stripe
- `POST /payments/create-payment-intent` - Crear pago único
- `GET /payments/payment-history` - Historial de pagos
- `POST /payments/stripe-webhook` - Webhook de Stripe

### Productos
- `GET /payments/products` - Listar productos
- `POST /payments/products` - Crear producto
- `PUT /payments/products/{id}` - Actualizar producto

## Integración Frontend

### Instalación en el frontend
```bash
npm install @stripe/stripe-js
```

### Ejemplo básico (React)
```javascript
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

// Cargar Stripe
const stripePromise = loadStripe('pk_test_...');

// Componente de pago
const CheckoutForm = () => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Crear Payment Intent
    const response = await fetch('/payments/create-payment-intent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ amount: 29.99, currency: 'usd' })
    });
    
    const { client_secret } = await response.json();
    
    // Procesar pago
    const result = await stripe.confirmCardPayment(client_secret, {
      payment_method: {
        card: elements.getElement(CardElement),
      }
    });
    
    if (result.error) {
      console.error(result.error.message);
    } else {
      console.log('¡Pago exitoso!');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button type="submit">Pagar</button>
    </form>
  );
};
```

## Testing

### Tarjetas de prueba de Stripe
- **Éxito**: 4242424242424242
- **Error**: 4000000000000002
- **3D Secure**: 4000002500003155

### Ejecutar con datos de prueba
Asegúrate de usar las claves de prueba (`pk_test_` y `sk_test_`) durante el desarrollo.

## Documentación Completa

Ver `STRIPE_INTEGRATION.md` para documentación detallada de la integración con Stripe, incluyendo:
- Ejemplos completos de frontend
- Configuración de webhooks
- Mejores prácticas de seguridad
- Troubleshooting

## Tecnologías Utilizadas

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos
- **Stripe** - Procesamiento de pagos
- **JWT** - Autenticación
- **Pydantic** - Validación de datos

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.
