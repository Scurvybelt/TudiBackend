from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from schemas.user import UserCreate
from jose import jwt
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de email - Hostinger SMTP
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587  
SMTP_USER = "hello@ferandsean.com"
SMTP_PASSWORD = "F3R&S34N@wedding"
FRONTEND_URL = "http://localhost:4200"

# User helpers
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(name=user.name, last_name=user.last_name, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user

def create_access_token(user):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user.id), "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
    return pwd_context.hash(password)

def test_smtp_connection():
    """
    Función para probar la conexión SMTP
    """
    try:
        print(f"🔍 Probando conexión SMTP...")
        print(f"Servidor: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"Usuario: {SMTP_USER}")
        
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            print("✅ Conexión SSL establecida")
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            print("✅ Conexión STARTTLS establecida")
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✅ Autenticación exitosa")
        
        server.quit()
        print("✅ Conexión SMTP funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión SMTP: {str(e)}")
        return False

# Password Reset Functions
def create_password_reset_token(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token válido por 1 hora
    
    user.reset_token = token
    user.reset_token_expires = expires_at
    db.commit()
    
    return token

def verify_password_reset_token(db: Session, token: str):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or user.reset_token_expires < datetime.utcnow():
        return False
    return True

def reset_user_password(db: Session, token: str, new_password: str):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or user.reset_token_expires < datetime.utcnow():
        return False
    
    user.password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return True

def send_password_reset_email(email: str, token: str):
    """
    Envía un email con el enlace para resetear la contraseña
    """
    try:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Restaurar contraseña - Tudi"
        
        html_body = f"""
        <html>
        <body>
            <h2>Restaurar contraseña</h2>
            <p>Hola,</p>
            <p>Has solicitado restaurar tu contraseña. Haz clic en el siguiente enlace:</p>
            <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restaurar Contraseña</a></p>
            <p>O copia y pega este enlace en tu navegador:</p>
            <p>{reset_url}</p>
            <p><strong>Este enlace expirará en 1 hora.</strong></p>
            <p>Si no solicitaste esto, ignora este email.</p>
            <br>
            <p>Saludos,<br>El equipo de Tudi</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Restaurar contraseña
        
        Hola,
        
        Has solicitado restaurar tu contraseña. Copia y pega el siguiente enlace en tu navegador:
        {reset_url}
        
        Este enlace expirará en 1 hora.
        
        Si no solicitaste esto, ignora este email.
        
        Saludos,
        El equipo de Tudi
        """
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = email
        
        # Agregar partes del mensaje
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"Intentando conectar a SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        
        # Hostinger usa SSL (465) no STARTTLS
        if SMTP_PORT == 465:
            # Usar SMTP_SSL para conexiones SSL directas
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            print("Conexión SSL establecida")
        else:
            # Usar SMTP normal con STARTTLS
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            print("Conexión STARTTLS establecida")
        
        print(f"Intentando login con: {SMTP_USER}")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("Login exitoso")
        
        text = msg.as_string()
        server.sendmail(SMTP_USER, email, text)
        server.quit()
        
        print(f"✅ Email de reset enviado exitosamente a: {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {str(e)}")
        print("Verifica que las credenciales sean correctas")
        print(f"TESTING - Reset URL para {email}: {reset_url}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ Error de conexión SMTP: {str(e)}")
        print("Verifica el servidor y puerto SMTP")
        print(f"TESTING - Reset URL para {email}: {reset_url}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP genérico: {str(e)}")
        print(f"TESTING - Reset URL para {email}: {reset_url}")
        return False
    except Exception as e:
        print(f"❌ Error general enviando email: {str(e)}")
        print(f"TESTING - Reset URL para {email}: {reset_url}")
        return False
        