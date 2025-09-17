from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserLogin, UserOut, PasswordResetRequest, PasswordReset
from services import auth_service
from database import get_db
from fastapi import Request

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

#Register
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth_service.create_user(db, user)

#Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth_service.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(db_user)
    return {"access_token": token, "token_type": "bearer", "user": db_user.email, "name": db_user.name + " " + db_user.last_name}

#Request Password Reset
@router.post("/request-password-reset")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Solicitar reset de contraseña por email
    """
    user = auth_service.get_user_by_email(db, request.email)
    if not user:
        # Por seguridad, no revelamos si el email existe o no
        return {"message": "Si el email existe, recibirás un enlace para restaurar tu contraseña"}
    
    reset_token = auth_service.create_password_reset_token(db, user.email)
    if reset_token:
        auth_service.send_password_reset_email(user.email, reset_token)
    
    return {"message": "Si el email existe, recibirás un enlace para restaurar tu contraseña"}

#Reset Password
@router.post("/reset-password")
def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """
    Resetear contraseña usando el token recibido por email
    """
    if not auth_service.verify_password_reset_token(db, reset_data.token):
        raise HTTPException(
            status_code=400, 
            detail="Token inválido o expirado"
        )
    
    if not auth_service.reset_user_password(db, reset_data.token, reset_data.new_password):
        raise HTTPException(
            status_code=400, 
            detail="Error al resetear la contraseña"
        )
    
    return {"message": "Contraseña restablecida exitosamente"}

@router.get("/verify-token")
def verify_token(request: Request, db: Session = Depends(get_db)):
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("bearer"):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = auth_header.split(" ")[1]
    user = auth_service.verify_access_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return {"valid": True, "user": user.email}