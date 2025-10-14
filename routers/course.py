from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from utils.dependencies import get_current_user
from services import course_service
from models import User

router = APIRouter(prefix="/course", tags=["course"])

@router.get("/progress")
def get_my_course_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el progreso del curso del usuario actual"""
    try:
        progress = course_service.get_user_course_progress(db, current_user.id)
        if not progress:
            # Si no hay progreso, inicializar
            course_service.initialize_user_course_progress(db, current_user.id)
            progress = course_service.get_user_course_progress(db, current_user.id)
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/phase/{phase_number}/complete")
def complete_course_phase(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una fase como completada (cuando se presiona el checkbox)
    phase_number: Número de orden de la fase (1, 2, 3, etc.)
    """
    try:
        print(f"🎯 Completando fase {phase_number} para usuario {current_user.id}")
        
        # Verificar si el usuario tiene progreso inicializado
        user_progress = course_service.get_user_course_progress(db, current_user.id)
        if not user_progress:
            print(f"⚠️  Usuario {current_user.id} no tiene progreso. Inicializando...")
            course_service.initialize_user_course_progress(db, current_user.id)
        
        progress = course_service.complete_phase(db, current_user.id, phase_number)
        print(f"✅ Fase {phase_number} completada. Nuevo status: {progress.status.value}")
        return {
            "message": "Fase completada exitosamente",
            "phase_number": phase_number,
            "status": progress.status.value,
            "completed_at": progress.completed_at
        }
    except Exception as e:
        print(f"❌ Error completando fase {phase_number}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/phase/{phase_number}/start")
def start_course_phase(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una fase como iniciada
    phase_number: Número de orden de la fase (1, 2, 3, etc.)
    """
    try:
        progress = course_service.start_phase(db, current_user.id, phase_number)
        return {
            "message": "Fase iniciada exitosamente",
            "phase_number": phase_number,
            "status": progress.status.value,
            "started_at": progress.started_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/phase/{phase_number}/access")
def check_phase_access(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica si el usuario puede acceder a una fase específica
    phase_number: Número de orden de la fase (1, 2, 3, etc.)
    """
    try:
        can_access = course_service.can_access_phase(db, current_user.id, phase_number)
        return {"can_access": can_access, "phase_number": phase_number}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/phase/{phase_number}/status")
def get_phase_status(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el status completo de una fase específica
    phase_number: Número de orden de la fase (1, 2, 3, etc.)
    """
    try:
        # Verificar si el usuario tiene progreso inicializado
        progress = course_service.get_user_course_progress(db, current_user.id)
        if not progress:
            print(f"⚠️  Usuario {current_user.id} no tiene progreso. Inicializando...")
            course_service.initialize_user_course_progress(db, current_user.id)
        
        phase_status = course_service.get_phase_status(db, current_user.id, phase_number)
        return phase_status
    except Exception as e:
        print(f"❌ Error en get_phase_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )