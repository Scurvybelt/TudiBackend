
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import auth, payments

app = FastAPI(title="Tudi Backend API", version="1.0.0")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # Puedes restringir a tu dominio frontend
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
models.Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(auth.router)
app.include_router(payments.router)



