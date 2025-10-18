import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from schemas.support import HelpRequest

# Configuración de email - misma que auth_service
SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 587  
SMTP_USER = "hello@ferandsean.com"
SMTP_PASSWORD = "F3R&S34N@wedding"
SUPPORT_EMAIL = "hello@ferandsean.com"  # Email donde se recibirán las solicitudes de ayuda

def send_help_request_email(help_request: HelpRequest):
    """
    Envía un email con la solicitud de ayuda del usuario
    """
    try:
        subject = f"Nueva solicitud de ayuda - {help_request.helpType}"
        
        # Email HTML con el diseño de Tudi
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Solicitud de Ayuda - Tudi</title>
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
                                        Nueva Solicitud de Ayuda
                                    </h2>
                                    
                                    <!-- Contenido -->
                                    <div style="text-align: left; margin-bottom: 30px;">
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Has recibido una nueva solicitud de ayuda a través del formulario de contacto:
                                        </p>
                                    </div>
                                    
                                    <!-- Información del usuario -->
                                    <div style="background-color: #F8F7FF; border-radius: 12px; padding: 25px; margin-bottom: 30px; text-align: left;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 5px 0;">
                                                        👤 Nombre completo:
                                                    </p>
                                                    <p style="font-size: 16px; color: #333333; margin: 0;">
                                                        {help_request.fullName}
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 5px 0;">
                                                        📧 Email:
                                                    </p>
                                                    <p style="font-size: 16px; color: #333333; margin: 0;">
                                                        <a href="mailto:{help_request.email}" style="color: #592DAC; text-decoration: none;">
                                                            {help_request.email}
                                                        </a>
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 5px 0;">
                                                        📱 Teléfono:
                                                    </p>
                                                    <p style="font-size: 16px; color: #333333; margin: 0;">
                                                        {help_request.phone}
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-bottom: 15px;">
                                                    <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 5px 0;">
                                                        🏷️ Tipo de ayuda:
                                                    </p>
                                                    <p style="font-size: 16px; color: #333333; margin: 0; background-color: #FFFFFF; padding: 8px 12px; border-radius: 6px; display: inline-block;">
                                                        {help_request.helpType}
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    
                                    <!-- Mensaje -->
                                    <div style="background-color: #FFFFFF; border: 2px solid #F8F7FF; border-radius: 12px; padding: 25px; margin-bottom: 30px; text-align: left;">
                                        <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 15px 0;">
                                            💬 Mensaje:
                                        </p>
                                        <p style="font-size: 15px; color: #333333; line-height: 1.6; margin: 0; white-space: pre-wrap;">
                                            {help_request.message}
                                        </p>
                                    </div>
                                    
                                    <!-- Botón de respuesta -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 20px;">
                                        <tr>
                                            <td align="center">
                                                <a href="mailto:{help_request.email}?subject=Re: {help_request.helpType}" style="display: inline-block; background-color: #592DAC; color: #FFFFFF; font-size: 16px; font-weight: 600; text-decoration: none; padding: 16px 48px; border-radius: 50px; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(89, 45, 172, 0.3);">
                                                    RESPONDER AL USUARIO
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Nota -->
                                    <div style="text-align: left; padding-top: 20px; border-top: 1px solid #E0E0E0;">
                                        <p style="font-size: 13px; color: #666666; line-height: 1.6; margin: 0;">
                                            Este mensaje fue enviado desde el formulario de ayuda de Tudi.
                                        </p>
                                    </div>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #F8F7FF; padding: 30px 40px; text-align: center; border-bottom-left-radius: 24px; border-bottom-right-radius: 24px;">
                                    <p style="font-size: 12px; color: #999999; margin: 0; line-height: 1.5;">
                                        Este es un correo automático del sistema de Tudi.
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
        
        # Versión de texto plano
        text_body = f"""
        TUDI - NUEVA SOLICITUD DE AYUDA
        
        Has recibido una nueva solicitud de ayuda:
        
        INFORMACIÓN DEL USUARIO:
        ------------------------
        Nombre: {help_request.fullName}
        Email: {help_request.email}
        Teléfono: {help_request.phone}
        Tipo de ayuda: {help_request.helpType}
        
        MENSAJE:
        --------
        {help_request.message}
        
        ---
        Para responder, envía un email a: {help_request.email}
        
        Este mensaje fue enviado desde el formulario de ayuda de Tudi.
        © 2025 Tudi. Todos los derechos reservados.
        """
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = SUPPORT_EMAIL
        msg['Reply-To'] = help_request.email  # Permite responder directamente al usuario
        
        # Agregar partes del mensaje
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"Intentando enviar solicitud de ayuda desde: {help_request.email}")
        print(f"Configuración SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"Usuario SMTP: {SMTP_USER}")
        print(f"Email de soporte destino: {SUPPORT_EMAIL}")
        
        # Conectar al servidor SMTP
        if SMTP_PORT == 465:
            print("Intentando conexión SSL...")
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            print("✅ Conexión SSL establecida")
        else:
            print("Intentando conexión STARTTLS...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            print("✅ Conexión STARTTLS establecida")
        
        print("Intentando login...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✅ Login exitoso")
        
        print("Preparando mensaje...")
        text = msg.as_string()
        print(f"Enviando desde {SMTP_USER} a {SUPPORT_EMAIL}")
        server.sendmail(SMTP_USER, SUPPORT_EMAIL, text)
        server.quit()
        
        print(f"✅ Solicitud de ayuda enviada exitosamente desde: {help_request.email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {str(e)}")
        print(f"   Verifica usuario: {SMTP_USER}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ Error de conexión SMTP: {str(e)}")
        print(f"   Verifica servidor: {SMTP_SERVER}:{SMTP_PORT}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP genérico: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Error general enviando email: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def send_confirmation_to_user(help_request: HelpRequest):
    """
    Envía un email de confirmación al usuario que solicitó ayuda
    """
    try:
        subject = "Hemos recibido tu solicitud de ayuda - Tudi"
        
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Solicitud - Tudi</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #592DAC 0%, #7C4DDB 100%); min-height: 100vh;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="min-height: 100vh;">
                <tr>
                    <td style="padding: 40px 20px;" align="center">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #FFFFFF; border-radius: 24px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);">
                            <tr>
                                <td style="padding: 60px 40px; text-align: center;">
                                    <!-- Logo -->
                                    <div style="margin-bottom: 40px;">
                                        <h1 style="font-size: 64px; font-weight: 900; color: #000000; margin: 0; letter-spacing: -2px;">tudi.</h1>
                                    </div>
                                    
                                    <!-- Título -->
                                    <h2 style="font-size: 28px; font-weight: 700; color: #592DAC; margin: 0 0 30px 0; letter-spacing: -0.5px;">
                                        ¡Solicitud Recibida!
                                    </h2>
                                    
                                    <!-- Contenido -->
                                    <div style="text-align: left; margin-bottom: 40px;">
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Hola <strong>{help_request.fullName}</strong>,
                                        </p>
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Hemos recibido tu solicitud de ayuda sobre <strong style="color: #592DAC;">{help_request.helpType}</strong>.
                                        </p>
                                        <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">
                                            Nuestro equipo revisará tu mensaje y te responderá lo antes posible al correo <strong style="color: #592DAC;">{help_request.email}</strong>.
                                        </p>
                                    </div>
                                    
                                    <!-- Información de la solicitud -->
                                    <div style="background-color: #F8F7FF; border-radius: 12px; padding: 25px; margin-bottom: 30px; text-align: left;">
                                        <p style="font-size: 14px; color: #592DAC; font-weight: 600; margin: 0 0 15px 0;">
                                            📋 Resumen de tu solicitud:
                                        </p>
                                        <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 0 0 10px 0;">
                                            <strong>Tipo:</strong> {help_request.helpType}
                                        </p>
                                        <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 0;">
                                            <strong>Mensaje:</strong><br>
                                            <span style="color: #333333;">{help_request.message}</span>
                                        </p>
                                    </div>
                                    
                                    <!-- Nota -->
                                    <div style="text-align: left; padding-top: 20px; border-top: 1px solid #E0E0E0;">
                                        <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 0 0 20px 0;">
                                            Tiempo estimado de respuesta: <strong>24-48 horas</strong>
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
        TUDI - CONFIRMACIÓN DE SOLICITUD
        
        Hola {help_request.fullName},
        
        Hemos recibido tu solicitud de ayuda sobre: {help_request.helpType}
        
        RESUMEN DE TU SOLICITUD:
        ------------------------
        Tipo: {help_request.helpType}
        Mensaje: {help_request.message}
        
        Nuestro equipo revisará tu mensaje y te responderá lo antes posible 
        al correo {help_request.email}.
        
        Tiempo estimado de respuesta: 24-48 horas
        
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
        msg['To'] = help_request.email
        
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Conectar al servidor SMTP
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(SMTP_USER, help_request.email, text)
        server.quit()
        
        print(f"✅ Confirmación enviada al usuario: {help_request.email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando confirmación al usuario: {str(e)}")
        return False