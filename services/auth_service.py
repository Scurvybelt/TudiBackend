from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from schemas.user import UserCreate
from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720
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
    
    # Inicializar progreso del curso para el nuevo usuario
    from services.course_service import initialize_user_course_progress
    try:
        initialize_user_course_progress(db, db_user.id)
    except Exception as e:
        print(f"Error inicializando progreso del curso: {e}")
    
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user

def verify_access_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except JWTError:
        return None

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
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
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
    Diseño actualizado para coincidir con la interfaz de Tudi
    """
    try:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Restaurar contraseña - Tudi"
        
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Restaurar contraseña - Tudi</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #592DAC 0%, #7C4DDB 100%); min-height: 100vh;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="min-height: 100vh;">
                <tr>
                    <td style="padding: 40px 20px;" align="center">
                        <!-- Contenedor principal -->
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #FFFFFF; border-radius: 24px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);">
                            <tr>
                                <td style="padding: 60px 40px; text-align: center;">
                                    <!-- Logo -->
                                    <div style="margin-bottom: 40px;">
                                        <h1 style="font-size: 64px; font-weight: 900; color: #000000; margin: 0; letter-spacing: -2px;">tudi.</h1>
                                    </div>
                                    
                                    <!-- Título -->
                                    <h2 style="font-size: 28px; font-weight: 700; color: #592DAC; margin: 0 0 30px 0; letter-spacing: -0.5px;">
                                        Restaurar contraseña
                                    </h2>
                                    
                                    <!-- Contenido -->
                                    <div style="text-align: left; margin-bottom: 40px;">
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Hola,
                                        </p>
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Has solicitado restaurar tu contraseña. Haz clic en el botón para continuar con el proceso:
                                        </p>
                                    </div>
                                    
                                    <!-- Botón principal -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{reset_url}" style="display: inline-block; background-color: #592DAC; color: #FFFFFF; font-size: 16px; font-weight: 600; text-decoration: none; padding: 16px 48px; border-radius: 50px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(89, 45, 172, 0.3);">
                                                    RESTAURAR CONTRASEÑA
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Información adicional -->
                                    <div style="background-color: #F8F7FF; border-radius: 12px; padding: 20px; margin-bottom: 30px;">
                                        <p style="font-size: 14px; color: #592DAC; line-height: 1.6; margin: 0 0 10px 0; font-weight: 600;">
                                            ⏱️ Este enlace expirará en 1 hora
                                        </p>
                                        <p style="font-size: 13px; color: #666666; line-height: 1.5; margin: 0;">
                                            Si el botón no funciona, copia y pega este enlace en tu navegador:
                                        </p>
                                        <p style="font-size: 12px; color: #592DAC; word-break: break-all; margin: 10px 0 0 0; padding: 10px; background-color: #FFFFFF; border-radius: 6px; border: 1px solid #E0E0E0;">
                                            {reset_url}
                                        </p>
                                    </div>
                                    
                                    <!-- Nota de seguridad -->
                                    <div style="text-align: left; padding-top: 20px; border-top: 1px solid #E0E0E0;">
                                        <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 0 0 20px 0;">
                                            Si no solicitaste este cambio, puedes ignorar este correo. Tu contraseña permanecerá sin cambios.
                                        </p>
                                        <p style="font-size: 14px; color: #333333; line-height: 1.6; margin: 0;">
                                            Saludos,<br>
                                            <strong style="color: #592DAC;">El equipo de Tudi</strong>
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #F8F7FF; padding: 30px 40px; text-align: center; border-bottom-left-radius: 24px; border-bottom-right-radius: 24px;">
                                    <p style="font-size: 12px; color: #999999; margin: 0; line-height: 1.5;">
                                        Este es un correo automático, por favor no respondas a este mensaje.
                                    </p>
                                    <p style="font-size: 12px; color: #999999; margin: 10px 0 0 0;">
                                        © 2025 Tudi. Todos los derechos reservados.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        text_body = f"""
        TUDI - RESTAURAR CONTRASEÑA
        
        Hola,
        
        Has solicitado restaurar tu contraseña. Copia y pega el siguiente enlace en tu navegador:
        
        {reset_url}
        
        ⏱️ Este enlace expirará en 1 hora.
        
        Si no solicitaste este cambio, puedes ignorar este correo. Tu contraseña permanecerá sin cambios.
        
        Saludos,
        El equipo de Tudi
        
        ---
        Este es un correo automático, por favor no respondas a este mensaje.
        © 2025 Tudi. Todos los derechos reservados.
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
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            print("Conexión SSL establecida")
        else:
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