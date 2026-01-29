from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import ActaEntregaRecepcion, Anexos, UnidadResponsable
from ..schemas import ActaResponse, ActaCreate, ActaUpdate
from ..auth import get_current_user, get_admin_user
from typing import List

router = APIRouter(prefix="/actas", tags=["Actas de Entrega Recepción"])

@router.get("", response_model=List[ActaResponse])
def read_actas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        actas = (
            db.query(ActaEntregaRecepcion)
            .options(selectinload(ActaEntregaRecepcion.unidad), selectinload(ActaEntregaRecepcion.anexos))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return actas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/{acta_id}", response_model=ActaResponse)
def read_acta(acta_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_acta = (
        db.query(ActaEntregaRecepcion)
        .options(selectinload(ActaEntregaRecepcion.anexos))
        .filter(ActaEntregaRecepcion.id == acta_id)
        .first()
    )
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    return db_acta

@router.post("", response_model=ActaResponse, status_code=status.HTTP_201_CREATED)
def crear_acta(acta: ActaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == acta.unidad_responsable).first()
        if not unidad:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unidad responsable con ID {acta.unidad_responsable} no existe")
        existing_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.folio == acta.folio).first()
        if existing_acta:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un acta con el folio {acta.folio}")
        db_acta = ActaEntregaRecepcion(**acta.model_dump(exclude_unset=True))
        db.add(db_acta)
        db.commit()
        db.refresh(db_acta)
        anexos_a_asociar = db.query(Anexos).filter(Anexos.unidad_responsable_id == acta.unidad_responsable, Anexos.creador_id == current_user.id, ((Anexos.acta_id == None) | (Anexos.acta_id == 0))).all()
        for an in anexos_a_asociar:
            an.acta_id = db_acta.id
        db.commit()
        db.refresh(db_acta)
        return db_acta
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear acta: {str(e)}")

@router.put("/{acta_id}", response_model=ActaResponse)
def update_acta(acta_id: int, acta: ActaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta_id).first()
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    for key, value in acta.model_dump(exclude_unset=True).items():
        setattr(db_acta, key, value)
    db.commit()
    db.refresh(db_acta)
    return db_acta

@router.delete("/{acta_id}")
def delete_acta(acta_id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    db_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta_id).first()
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    db.delete(db_acta)
    db.commit()
    return {"message": "Acta eliminada correctamente"}
