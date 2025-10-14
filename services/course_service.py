from sqlalchemy.orm import Session
from models import User, CoursePhase, UserCourseProgress, CoursePhaseStatus
from datetime import datetime

def initialize_user_course_progress(db: Session, user_id: int):
    """Inicializa el progreso del curso para un nuevo usuario"""
    print(f"🔧 Inicializando progreso del curso para usuario {user_id}")
    
    # Verificar si ya existe progreso
    existing_progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id
    ).first()
    
    if existing_progress:
        print(f"ℹ️  Usuario {user_id} ya tiene progreso inicializado")
        return
    
    phases = db.query(CoursePhase).order_by(CoursePhase.phase_order).all()
    
    if not phases:
        print(f"❌ No hay fases en la base de datos. Ejecuta create_course_tables.sql")
        raise Exception("No hay fases configuradas en el sistema")
    
    print(f"📚 Creando progreso para {len(phases)} fases")
    
    for i, phase in enumerate(phases):
        # Solo la primera fase está disponible al inicio
        status = CoursePhaseStatus.AVAILABLE if i == 0 else CoursePhaseStatus.LOCKED
        
        progress = UserCourseProgress(
            user_id=user_id,
            phase_id=phase.id,
            status=status
        )
        db.add(progress)
        print(f"  ✓ Fase {phase.phase_order} ({phase.name}): {status.value}")
    
    db.commit()
    print(f"✅ Progreso inicializado correctamente para usuario {user_id}")

def complete_phase(db: Session, user_id: int, phase_number: int):
    """Marca una fase como completada y desbloquea la siguiente
    phase_number: El número de orden de la fase (1, 2, 3, etc.)
    """
    print(f"📚 complete_phase - Usuario: {user_id}, Número de Fase: {phase_number}")
    
    # Buscar la fase por su número de orden (phase_order)
    current_phase = db.query(CoursePhase).filter(
        CoursePhase.phase_order == phase_number
    ).first()
    
    if not current_phase:
        print(f"❌ No se encontró la fase con número de orden {phase_number}")
        raise Exception(f"No se encontró la fase {phase_number}")
    
    print(f"✅ Fase encontrada: ID={current_phase.id}, Nombre={current_phase.name}, Orden={current_phase.phase_order}")
    
    # Obtener el progreso actual de la fase
    current_progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == current_phase.id
    ).first()
    
    if not current_progress:
        print(f"❌ No se encontró el progreso para fase {phase_number} (ID: {current_phase.id})")
        raise Exception("No se encontró el progreso de esta fase")
    
    print(f"📊 Estado actual de la fase {phase_number}: {current_progress.status.value}")
    
    if current_progress.status == CoursePhaseStatus.LOCKED:
        print(f"🔒 Error: Intentando completar fase bloqueada {phase_number}")
        raise Exception("No puedes completar una fase bloqueada")
    
    # Marcar como completada
    current_progress.status = CoursePhaseStatus.COMPLETED
    current_progress.completed_at = datetime.utcnow()
    current_progress.progress_percentage = 100.0
    print(f"✅ Fase {phase_number} marcada como completada")
    
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
            print(f"🔓 Fase {next_phase.phase_order} desbloqueada (estaba LOCKED → AVAILABLE)")
        elif next_progress:
            print(f"ℹ️  Fase {next_phase.phase_order} ya estaba en estado: {next_progress.status.value}")
    else:
        print(f"ℹ️  No hay siguiente fase después de la fase {phase_number}")
    
    db.commit()
    print(f"💾 Cambios guardados en la base de datos")
    return current_progress

def get_user_course_progress(db: Session, user_id: int):
    """Obtiene todo el progreso del curso de un usuario"""
    print(f"📖 get_user_course_progress - Usuario: {user_id}")
    
    progress = db.query(UserCourseProgress, CoursePhase).join(
        CoursePhase, UserCourseProgress.phase_id == CoursePhase.id
    ).filter(
        UserCourseProgress.user_id == user_id
    ).order_by(CoursePhase.phase_order).all()
    
    result = [
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
    
    print(f"📊 Progreso del usuario {user_id}:")
    for phase in result:
        print(f"   - Fase {phase['phase_id']} ({phase['phase_name']}): {phase['status']} - can_access: {phase['can_access']}")
    
    return result

def can_access_phase(db: Session, user_id: int, phase_number: int) -> bool:
    """Verifica si un usuario puede acceder a una fase específica
    phase_number: El número de orden de la fase (1, 2, 3, etc.)
    """
    # Buscar la fase por su número de orden
    phase = db.query(CoursePhase).filter(
        CoursePhase.phase_order == phase_number
    ).first()
    
    if not phase:
        return False
    
    progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase.id
    ).first()
    
    if not progress:
        return False
    
    return progress.status in [CoursePhaseStatus.AVAILABLE, CoursePhaseStatus.IN_PROGRESS, CoursePhaseStatus.COMPLETED]

def get_phase_status(db: Session, user_id: int, phase_number: int):
    """Obtiene el status completo de una fase específica
    phase_number: El número de orden de la fase (1, 2, 3, etc.)
    """
    # Buscar la fase por su número de orden
    phase = db.query(CoursePhase).filter(
        CoursePhase.phase_order == phase_number
    ).first()
    
    if not phase:
        raise Exception(f"No se encontró la fase {phase_number}")
    
    progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase.id
    ).first()
    
    if not progress:
        raise Exception("No se encontró el progreso de esta fase")
    
    return {
        "phase_number": phase_number,
        "phase_id": phase.id,
        "status": progress.status.value,
        "progress_percentage": progress.progress_percentage,
        "started_at": progress.started_at,
        "completed_at": progress.completed_at,
        "can_access": progress.status in [CoursePhaseStatus.AVAILABLE, CoursePhaseStatus.IN_PROGRESS, CoursePhaseStatus.COMPLETED]
    }

def start_phase(db: Session, user_id: int, phase_number: int):
    """Marca una fase como iniciada
    phase_number: El número de orden de la fase (1, 2, 3, etc.)
    """
    # Buscar la fase por su número de orden
    phase = db.query(CoursePhase).filter(
        CoursePhase.phase_order == phase_number
    ).first()
    
    if not phase:
        raise Exception(f"No se encontró la fase {phase_number}")
    
    progress = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == user_id,
        UserCourseProgress.phase_id == phase.id
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