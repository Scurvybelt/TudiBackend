
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import auth, payments

app = FastAPI(title="Tudi Backend API", version="1.0.0")

# Configuración de CORS simplificada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=False,  # Cambiar a False para evitar problemas
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(payments.router, prefix="/api")



