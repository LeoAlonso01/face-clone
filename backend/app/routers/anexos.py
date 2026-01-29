from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Anexos
from ..schemas import AnexoCreate, AnexoResponse, AnexoUpdate
from ..auth import get_current_user, get_admin_user
from typing import List
from datetime import date

router = APIRouter(prefix="/anexos", tags=["Anexos de Entrega Recepción"])

@router.get("", response_model=List[AnexoResponse])
def read_anexos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        anexos = db.query(Anexos).filter(Anexos.is_deleted == False).offset(skip).limit(limit).all()
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")

@router.post("", response_model=AnexoResponse)
def create_anexo(anexo: AnexoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_anexo = Anexos(clave=anexo.clave, creador_id=current_user.id, datos=anexo.datos, estado=anexo.estado, unidad_responsable_id=anexo.unidad_responsable_id, fecha_creacion=anexo.fecha_creacion or date.today(), creado_en=date.today(), actualizado_en=date.today(), is_deleted=False)
    db.add(db_anexo)
    db.commit()
    db.refresh(db_anexo)
    return db_anexo

@router.get("/{anexo_id}", response_model=AnexoResponse)
def read_anexo(anexo_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    return db_anexo

@router.put("/{anexo_id}", response_model=AnexoResponse)
def update_anexo(anexo_id: int, anexo: AnexoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    for key, value in anexo.model_dump(exclude_unset=True).items():
        setattr(db_anexo, key, value)
    db_anexo.actualizado_en = date.today()
    db.commit()
    db.refresh(db_anexo)
    return db_anexo

@router.delete("/{anexo_id}")
def delete_anexo(anexo_id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    db_anexo.is_deleted = True
    db_anexo.actualizado_en = date.today()
    db.commit()
    return {"message": "Anexo eliminado correctamente"}

@router.get("/clave/{clave}", response_model=List[AnexoResponse])
def read_anexos_by_clave(clave: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        anexos = db.query(Anexos).filter(Anexos.clave == clave, Anexos.is_deleted == False).all()
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar anexos por clave: {str(e)}")

@router.get("/estado/{estado}", response_model=List[AnexoResponse])
def read_anexos_by_estado(estado: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        anexos = db.query(Anexos).filter(Anexos.estado == estado, Anexos.is_deleted == False).all()
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar anexos por estado: {str(e)}")
