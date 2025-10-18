from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.support import HelpRequest
from services.support_service import send_help_request_email, send_confirmation_to_user

router = APIRouter(prefix="/support", tags=["support"])


@router.post("/request-help", status_code=status.HTTP_200_OK)
def request_help(help_request: HelpRequest):
    """
    Endpoint público para enviar solicitudes de ayuda por correo electrónico.
    No requiere autenticación para permitir que usuarios no registrados puedan solicitar ayuda.
    
    Envía dos emails:
    1. Al equipo de soporte con los detalles de la solicitud
    2. Al usuario con confirmación de que su solicitud fue recibida
    """
    try:
        print(f"📨 Nueva solicitud de ayuda recibida de: {help_request.email}")
        print(f"   Nombre: {help_request.fullName}")
        print(f"   Tipo: {help_request.helpType}")
        print(f"   Teléfono: {help_request.phone}")
        print(f"   Mensaje: {help_request.message[:50]}..." if len(help_request.message) > 50 else f"   Mensaje: {help_request.message}")
        
        # Enviar email al equipo de soporte
        print("🔄 Intentando enviar email al equipo de soporte...")
        email_sent = send_help_request_email(help_request)
        print(f"📬 Resultado del envío: {email_sent}")
        
        if not email_sent:
            print("❌ El envío de email falló")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al enviar el email de solicitud de ayuda. Revisa los logs del servidor para más detalles."
            )
        
        # Enviar confirmación al usuario (no detiene el proceso si falla)
        try:
            send_confirmation_to_user(help_request)
        except Exception as e:
            print(f"⚠️ No se pudo enviar confirmación al usuario, pero la solicitud fue procesada: {e}")
        
        return {
            "success": True,
            "message": "Solicitud de ayuda enviada exitosamente. Te responderemos pronto.",
            "email": help_request.email,
            "helpType": help_request.helpType
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en request_help: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando la solicitud: {str(e)}"
        )

