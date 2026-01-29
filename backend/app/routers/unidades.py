from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import UnidadResponsable, User
from ..schemas import UnidadResponsableCreate, UnidadResponsableResponse, UnidadResponsableUpdate, UnidadJerarquicaResponse
from ..auth import get_current_user, get_admin_user
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql import text

router = APIRouter(prefix="/unidades_responsables", tags=["Unidades Responsables"])

@router.post("", response_model=UnidadResponsableResponse, status_code=status.HTTP_201_CREATED)
def create_unidades_responsables(unidad: UnidadResponsableCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if user_role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear unidades responsables")
    if unidad.responsable is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede asignar un responsable al crear una unidad, asigna el responsable despues")
    if unidad.unidad_padre_id:
        parent_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad.unidad_padre_id).first()
        if not parent_unidad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad padre no encontrada")
    if not unidad.nombre:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la unidad es obligatorio")
    try:
        new_unidad = UnidadResponsable(
            nombre=unidad.nombre,
            telefono=unidad.telefono,
            domicilio=unidad.domicilio,
            municipio=unidad.municipio,
            localidad=unidad.localidad,
            codigo_postal=unidad.codigo_postal,
            rfc=unidad.rfc,
            correo_electronico=unidad.correo_electronico,
            responsable=unidad.responsable,
            tipo_unidad=unidad.tipo_unidad,
            unidad_padre_id=unidad.unidad_padre_id
        )
        db.add(new_unidad)
        db.commit()
        db.refresh(new_unidad)
        return jsonable_encoder(new_unidad)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear la unidad responsable: {str(e)}")

@router.get("", response_model=list[UnidadResponsableResponse])
def read_unidades(db: Session = Depends(get_db)):
    try:
        query = db.query(UnidadResponsable).options(joinedload(UnidadResponsable.usuario_responsable))
        unidades = query.all()
        for unidad in unidades:
            if unidad.usuario_responsable:
                unidad.responsable = {
                    "id": unidad.usuario_responsable.id,
                    "username": unidad.usuario_responsable.username,
                    "email": unidad.usuario_responsable.email
                }
            else:
                unidad.responsable = None
        return unidades
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener unidades: {str(e)}")

@router.get("/{unidad_id}", response_model=UnidadResponsableResponse)
def get_unidad(unidad_id: int, db: Session = Depends(get_db)):
    db_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad_id).first()
    if not db_unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return db_unidad

@router.put("/{unidad_id}", response_model=UnidadResponsableResponse)
def actualizar_unidad(unidad_id: int, unidad_actualizacion: UnidadResponsableUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_unidad = db.query(UnidadResponsable).get(unidad_id)
    if not db_unidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró una unidad con ID {unidad_id}")
    if unidad_actualizacion.responsable_id is not None:
        responsable = db.query(User).get(unidad_actualizacion.responsable_id)
        if not responsable:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró un usuario con ID {unidad_actualizacion.responsable_id}")
    data = unidad_actualizacion.model_dump(exclude_unset=True)
    if "responsable_id" in data:
        db_unidad.responsable = data.pop("responsable_id")
    if "responsable" in data:
        resp = data.pop("responsable")
        if resp is None:
            db_unidad.responsable = None
        else:
            resp_id = getattr(resp, "id", None) if hasattr(resp, 'id') else (resp.get('id') if isinstance(resp, dict) else None)
            if resp_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El objeto 'responsable' debe incluir el campo 'id'")
            responsable = db.query(User).get(resp_id)
            if not responsable:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró un usuario con ID {resp_id}")
            db_unidad.responsable = resp_id
    for key, value in data.items():
        setattr(db_unidad, key, value)
    db.commit()
    db.refresh(db_unidad)
    if db_unidad.usuario_responsable:
        db_unidad.responsable = {
            "id": db_unidad.usuario_responsable.id,
            "username": db_unidad.usuario_responsable.username,
            "email": db_unidad.usuario_responsable.email
        }
    else:
        db_unidad.responsable = None
    return db_unidad

@router.put("/{unidad_id}/asignar-responsable")
def asignar_responsable(unidad_id: int, usuario_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    db_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad_id).first()
    if not db_unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    db_usuario = db.query(User).filter(User.id == usuario_id, User.is_deleted == False).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db_unidad.responsable = db_usuario.id
    db.commit()
    db.refresh(db_unidad)
    return {"message": "Responsable asignado correctamente", "unidad": jsonable_encoder(db_unidad)}

@router.get("/jerarquia", response_model=list[UnidadJerarquicaResponse])
def unidades_jerarquicas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role,'value') else str(current_user.role)
    if user_role != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para acceder a esta información")
    sql = text("""
        WITH RECURSIVE jerarquia AS (
            SELECT 
                u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, 0 as nivel,
                u.responsable as responsable_id
            FROM unidades_responsables u
            WHERE unidad_padre_id IS NULL
            UNION ALL
            SELECT 
                u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, j.nivel + 1,
                u.responsable as responsable_id
            FROM unidades_responsables u
            JOIN jerarquia j ON u.unidad_padre_id = j.id_unidad
        )
        SELECT 
            j.id_unidad, j.nombre, j.tipo_unidad, j.nivel, 
            us.id as responsable_id, us.username, us.email
        FROM jerarquia j
        LEFT JOIN users us ON j.responsable_id = us.id
        ORDER BY j.nivel, j.nombre;
    """)
    result = db.execute(sql).fetchall()
    unidades = []
    for row in result:
        responsable = None
        if row.responsable_id:
            responsable = {"id": row.responsable_id, "username": row.username, "email": row.email}
        unidades.append({"id_unidad": row.id_unidad, "nombre": row.nombre, "tipo_unidad": row.tipo_unidad, "nivel": row.nivel, "responsable": responsable})
    return unidades

@router.get("/por_usuario/{user_id}")
def obtener_unidad_por_usuario(user_id:int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not usuario.unidad:
        raise HTTPException(status_code=404, detail="El usuario no tiene una unidad responsable asignada")
    unidad = usuario.unidad
    return {"id_unidad": unidad.id_unidad, "nombre": unidad.nombre, "responsable": {"id": unidad.usuario_responsable.id, "nombre": unidad.usuario_responsable.username}}