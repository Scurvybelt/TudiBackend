
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routers import auth, payments, course, support
from models import CoursePhase

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

# # Inicializar fases del curso si no existen
# def init_course_phases():
#     db = SessionLocal()
#     try:
#         # Verificar si ya existen fases
#         existing_phases = db.query(CoursePhase).count()
        
#         if existing_phases == 0:
#             print("🔧 Inicializando fases del curso...")
#             phases_data = [
#                 {'name': 'Fase 1', 'description': 'Primer Contacto', 'phase_order': 1},
#                 {'name': 'Fase 2', 'description': 'La estrategia', 'phase_order': 2},
#                 {'name': 'Fase 3', 'description': 'La conceptualización', 'phase_order': 3},
#                 {'name': 'Fase 4', 'description': 'Desarrollo de proyecto', 'phase_order': 4},
#                 {'name': 'Fase 5', 'description': 'Testeo de la propuesta', 'phase_order': 5},
#                 {'name': 'Fase 6', 'description': 'Presenta la propuesta', 'phase_order': 6},
#                 {'name': 'Fase 7', 'description': 'Cierre del proyecto', 'phase_order': 7},
#             ]
            
#             for phase_data in phases_data:
#                 phase = CoursePhase(**phase_data)
#                 db.add(phase)
            
#             db.commit()
#             print(f"✅ {len(phases_data)} fases del curso creadas correctamente")
#         else:
#             print(f"ℹ️  Ya existen {existing_phases} fases en la base de datos")
#     except Exception as e:
#         print(f"❌ Error inicializando fases: {e}")
#         db.rollback()
#     finally:
#         db.close()

# # Ejecutar inicialización al arrancar
# init_course_phases()

# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(course.router, prefix="/api")
app.include_router(support.router, prefix="/api")



