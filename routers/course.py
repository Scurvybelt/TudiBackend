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

@router.post("/phase/{phase_id}/complete")
def complete_course_phase(
    phase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una fase como completada (cuando se presiona el checkbox)"""
    try:
        progress = course_service.complete_phase(db, current_user.id, phase_id)
        return {
            "message": "Fase completada exitosamente",
            "phase_id": phase_id,
            "status": progress.status.value,
            "completed_at": progress.completed_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/phase/{phase_id}/start")
def start_course_phase(
    phase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una fase como iniciada"""
    try:
        progress = course_service.start_phase(db, current_user.id, phase_id)
        return {
            "message": "Fase iniciada exitosamente",
            "phase_id": phase_id,
            "status": progress.status.value,
            "started_at": progress.started_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/phase/{phase_id}/access")
def check_phase_access(
    phase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica si el usuario puede acceder a una fase específica"""
    try:
        can_access = course_service.can_access_phase(db, current_user.id, phase_id)
        return {"can_access": can_access, "phase_id": phase_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )