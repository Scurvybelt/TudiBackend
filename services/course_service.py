from sqlalchemy.orm import Session
from models import User, CoursePhase, UserCourseProgress, CoursePhaseStatus
from datetime import datetime

def initialize_user_course_progress(db: Session, user_id: int):
    """Inicializa el progreso del curso para un nuevo usuario"""
    phases = db.query(CoursePhase).order_by(CoursePhase.phase_order).all()
    
    for i, phase in enumerate(phases):
        # Solo la primera fase está disponible al inicio
        status = CoursePhaseStatus.AVAILABLE if i == 0 else CoursePhaseStatus.LOCKED
        
        progress = UserCourseProgress(
            user_id=user_id,
            phase_id=phase.id,
            status=status
        )
        db.add(progress)
    
    db.commit()

def complete_phase(db: Session, user_id: int, phase_id: int):
    """Marca una fase como completada y desbloquea la siguiente"""
    # Obtener el progreso actual de la fase
    current_progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase_id
    ).first()
    
    if not current_progress:
        raise Exception("No se encontró el progreso de esta fase")
    
    if current_progress.status == CoursePhaseStatus.LOCKED:
        raise Exception("No puedes completar una fase bloqueada")
    
    # Marcar como completada
    current_progress.status = CoursePhaseStatus.COMPLETED
    current_progress.completed_at = datetime.utcnow()
    current_progress.progress_percentage = 100.0
    
    # Obtener la fase actual para saber su orden
    current_phase = db.query(CoursePhase).filter(CoursePhase.id == phase_id).first()
    
    # Desbloquear la siguiente fase
    next_phase = db.query(CoursePhase).filter(
        CoursePhase.phase_order == current_phase.phase_order + 1
    ).first()
    
    if next_phase:
        next_progress = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == user_id,
            UserCourseProgress.phase_id == next_phase.id
        ).first()
        
        if next_progress and next_progress.status == CoursePhaseStatus.LOCKED:
            next_progress.status = CoursePhaseStatus.AVAILABLE
    
    db.commit()
    return current_progress

def get_user_course_progress(db: Session, user_id: int):
    """Obtiene todo el progreso del curso de un usuario"""
    progress = db.query(UserCourseProgress, CoursePhase).join(
        CoursePhase, UserCourseProgress.phase_id == CoursePhase.id
    ).filter(
        UserCourseProgress.user_id == user_id
    ).order_by(CoursePhase.phase_order).all()
    
    return [
        {
            "phase_id": prog.UserCourseProgress.phase_id,
            "phase_name": prog.CoursePhase.name,
            "phase_order": prog.CoursePhase.phase_order,
            "status": prog.UserCourseProgress.status.value,
            "progress_percentage": prog.UserCourseProgress.progress_percentage,
            "started_at": prog.UserCourseProgress.started_at,
            "completed_at": prog.UserCourseProgress.completed_at,
            "can_access": prog.UserCourseProgress.status in [CoursePhaseStatus.AVAILABLE, CoursePhaseStatus.IN_PROGRESS, CoursePhaseStatus.COMPLETED]
        }
        for prog in progress
    ]

def can_access_phase(db: Session, user_id: int, phase_id: int) -> bool:
    """Verifica si un usuario puede acceder a una fase específica"""
    progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase_id
    ).first()
    
    if not progress:
        return False
    
    return progress.status in [CoursePhaseStatus.AVAILABLE, CoursePhaseStatus.IN_PROGRESS, CoursePhaseStatus.COMPLETED]

def start_phase(db: Session, user_id: int, phase_id: int):
    """Marca una fase como iniciada"""
    progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase_id
    ).first()
    
    if not progress:
        raise Exception("No se encontró el progreso de esta fase")
    
    if progress.status == CoursePhaseStatus.LOCKED:
        raise Exception("No puedes iniciar una fase bloqueada")
    
    if progress.status == CoursePhaseStatus.AVAILABLE:
        progress.status = CoursePhaseStatus.IN_PROGRESS
        progress.started_at = datetime.utcnow()
        db.commit()
    
    return progress