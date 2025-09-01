# Integración de Stripe - Pagos Únicos

## Configuración requerida

### Variables de entorno (.env)
```
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=http://localhost:3000/success
STRIPE_CANCEL_URL=http://localhost:3000/cancel
```

## Endpoints disponibles

### 1. Obtener configuración de Stripe
```
GET /payments/config
```
Respuesta:
```json
{
  "publishable_key": "pk_test_..."
}
```

### 2. Crear Payment Intent (pagos únicos)
```
POST /payments/create-payment-intent
Authorization: Bearer {token}
```
Body:
```json
{
  "amount": 29.99,
  "currency": "usd",
  "description": "Compra de curso premium"
}
```

### 3. Obtener historial de pagos
```
GET /payments/payment-history
Authorization: Bearer {token}
```

### 4. Gestionar productos
```
GET /payments/products              # Listar productos
POST /payments/products             # Crear producto
PUT /payments/products/{id}         # Actualizar producto
```

### 5. Webhook de Stripe
```
POST /payments/stripe-webhook
Stripe-Signature: {signature}
```

## Ejemplo de integración frontend (React/JavaScript)

### 1. Instalación
```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 2. Configuración inicial
```javascript
import { loadStripe } from '@stripe/stripe-js';

// Obtener la clave pública desde el backend
const getStripeConfig = async () => {
  const response = await fetch('/payments/config');
  const config = await response.json();
  return config.publishable_key;
};

const stripePromise = getStripeConfig().then(publishableKey => 
  loadStripe(publishableKey)
);
```

### 3. Componente de pago único
```javascript
import React, { useState, useEffect } from 'react';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const CheckoutForm = ({ amount, description }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState('');

  useEffect(() => {
    // Crear Payment Intent
    const createPaymentIntent = async () => {
      const response = await fetch('/payments/create-payment-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          amount: amount,
          currency: 'usd',
          description: description
        })
      });
      
      const { client_secret } = await response.json();
      setClientSecret(client_secret);
    };

    createPaymentIntent();
  }, [amount, description]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);

    const card = elements.getElement(CardElement);

    const { error, paymentIntent } = await stripe.confirmCardPayment(
      clientSecret,
      {
        payment_method: {
          card: card,
          billing_details: {
            name: 'Usuario',
          },
        }
      }
    );

    if (error) {
      console.error('Error:', error);
      setIsProcessing(false);
    } else if (paymentIntent.status === 'succeeded') {
      console.log('Pago exitoso!', paymentIntent);
      // Redirigir o mostrar mensaje de éxito
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement
        options={{
          style: {
            base: {
              fontSize: '16px',
              color: '#424770',
              '::placeholder': {
                color: '#aab7c4',
              },
            },
          },
        }}
      />
      <button type="submit" disabled={!stripe || isProcessing}>
        {isProcessing ? 'Procesando...' : `Pagar $${amount}`}
      </button>
    </form>
  );
};

const PaymentPage = () => {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm amount={29.99} description="Compra de curso premium" />
    </Elements>
  );
};

export default PaymentPage;
```

### 4. Listar productos disponibles
```javascript
const ProductList = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/payments/products')
      .then(response => response.json())
      .then(data => setProducts(data));
  }, []);

  return (
    <div>
      <h2>Productos Disponibles</h2>
      {products.map(product => (
        <div key={product.id} className="product-card">
          <h3>{product.name}</h3>
          <p>{product.description}</p>
          <p>${product.price} {product.currency.toUpperCase()}</p>
          <button onClick={() => handlePurchase(product)}>
            Comprar
          </button>
        </div>
      ))}
    </div>
  );
};
```

## Configuración de Webhook en Stripe Dashboard

1. Ve a https://dashboard.stripe.com/webhooks
2. Crea un nuevo endpoint: `https://tudominio.com/payments/stripe-webhook`
3. Selecciona estos eventos:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copia el webhook secret y agrégalo a las variables de entorno

## Comandos para migrar la base de datos

```bash
# Si usas Alembic
alembic revision --autogenerate -m "Add payment tables"
alembic upgrade head

# O ejecutar directamente el SQL
psql -U usuario -d tudi_db -f create_payment_tables.sql
```

## Estructura de carpetas creada

```
BackendTudi/
├── config/
│   └── stripe_config.py          # Configuración de Stripe
├── schemas/
│   └── stripe_schemas.py         # Schemas para pagos
├── services/
│   └── stripe_service.py         # Lógica de negocio de Stripe
├── routers/
│   └── payments.py               # Endpoints de pagos
└── models.py                     # Modelos con Payment y Product
```

## Testing

Para probar la integración, puedes usar las tarjetas de prueba de Stripe:

- **Éxito**: 4242424242424242
- **Error**: 4000000000000002
- **3D Secure**: 4000002500003155

## Flujo de trabajo típico

1. **Listar productos**: `GET /payments/products`
2. **Crear Payment Intent**: `POST /payments/create-payment-intent` 
3. **Procesar pago en frontend**: Usar Stripe Elements con el `client_secret`
4. **Webhook confirma pago**: Stripe envía webhook cuando el pago se completa
5. **Ver historial**: `GET /payments/payment-history`

## Notas importantes

1. **Seguridad**: Nunca expongas las claves secretas en el frontend
2. **Webhooks**: Son esenciales para mantener sincronizado el estado de los pagos
3. **Monedas**: El sistema soporta múltiples monedas, pero Stripe maneja centavos
4. **Testing**: Usa las claves de prueba de Stripe durante el desarrollo
5. **Logs**: Revisa los logs para debuggear problemas con pagos

## Próximos pasos

1. Configurar las variables de entorno
2. Migrar la base de datos con `create_payment_tables.sql`
3. Configurar webhooks en Stripe Dashboard
4. Implementar el frontend con los ejemplos proporcionados
5. Crear productos con `POST /payments/products` o usar `init_sample_products.py`
6. Testear pagos en modo de prueba
