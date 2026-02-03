from sqlalchemy.orm import Session
from .models import AuditLog
from datetime import datetime
from typing import Optional, Any

SENSITIVE_KEYS = {"password", "new_password", "current_password"}


def sanitize_metadata(metadata: Optional[dict]) -> Optional[dict]:
    if not metadata:
        return None
    sanitized = {}
    for k, v in metadata.items():
        if k.lower() in SENSITIVE_KEYS:
            sanitized[k] = "[REDACTED]"
        else:
            try:
                # try to keep JSON serializable types
                sanitized[k] = v
            except Exception:
                sanitized[k] = str(v)
    return sanitized


def create_audit_log(
    db: Session,
    actor_id: Optional[int],
    action: str,
    object_type: Optional[str] = None,
    object_id: Optional[int] = None,
    success: bool = True,
    metadata: Optional[dict] = None,
    ip: Optional[str] = None,
):
    """Crea un registro de auditoría en la BD.

    metadata se sanitiza para evitar almacenar contraseñas en texto plano.
    """
    try:
        sanitized = sanitize_metadata(metadata)
        # map sanitized metadata to the model attribute `metadata_json`
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            success=success,
            ip_address=ip,
            metadata_json=sanitized,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        # Log the error so it can be debugged but don't interrupt the main flow
        import logging
        logger = logging.getLogger('audit')
        logger.exception(f"Failed to write audit log: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None
