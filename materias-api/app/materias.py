# app/materias.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import MATERIAS
from app.esquemas import Materia, MateriaActualizar, MateriaCrear

router = APIRouter(prefix="/materias", tags=["materias"])


def obtener_materia(codigo: str) -> dict:
    """Devuelve el diccionario de la materia o lanza 404."""
    for materia in MATERIAS:
        if materia["codigo"] == codigo.upper():
            return materia
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la materia '{codigo}'",
    )


MateriaEncontrada = Annotated[dict, Depends(obtener_materia)]

# app/materias.py — segunda parte: el CRUD


@router.get("", response_model=list[Materia])
def listar_materias(
    semestre: Annotated[int | None, Query(ge=1, le=10)] = None,
    solo_obligatorias: bool = False,
) -> list[dict]:
    resultado = MATERIAS
    if semestre is not None:
        resultado = [m for m in resultado if m["semestre"] == semestre]
    if solo_obligatorias:
        resultado = [m for m in resultado if m["obligatoria"]]
    return resultado


@router.post("", response_model=Materia, status_code=status.HTTP_201_CREATED)
def crear_materia(nueva: MateriaCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in MATERIAS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La materia '{nueva.codigo}' ya existe",
        )
    MATERIAS.append(nueva.model_dump())
    return MATERIAS[-1]

# app/materias.py — ¡ANTES de la ruta /{codigo}!


@router.get("/estadisticas")
def estadisticas(semestre: Annotated[int | None, Query(ge=1, le=10)] = None) -> dict:
    seleccion = [m for m in MATERIAS if semestre is None or m["semestre"] == semestre]
    if not seleccion:
        raise HTTPException(404, f"No hay materias en el semestre {semestre}")
    creditos = sum(m["creditos"] for m in seleccion)
    obligatorias = sum(1 for m in seleccion if m["obligatoria"])
    return {
        "materias": len(seleccion),
        "creditos_totales": creditos,
        "promedio_creditos": round(creditos / len(seleccion), 2),
        "porcentaje_obligatorias": round(obligatorias * 100 / len(seleccion), 1),
    }

# app/materias.py — también ANTES de la ruta /{codigo}


@router.get("/avance")
def avance(aprobadas: Annotated[list[str] | None, Query()] = None) -> dict:
    codigos = {c.upper() for c in (aprobadas or [])}
    total = aprobados = 0
    pendientes = []
    for materia in MATERIAS:
        total += materia["creditos"]
        if materia["codigo"] in codigos:
            aprobados += materia["creditos"]
        elif materia["obligatoria"]:
            pendientes.append(materia["codigo"])
    return {"porcentaje_avance": round(aprobados * 100 / total, 1),
            "creditos_aprobados": aprobados, "obligatorias_pendientes": pendientes}

@router.get("/{codigo}", response_model=Materia)
def ver_materia(materia: MateriaEncontrada) -> dict:
    return materia


@router.put("/{codigo}", response_model=Materia)
def actualizar_materia(cambios: MateriaActualizar, materia: MateriaEncontrada) -> dict:
    materia.update(cambios.model_dump(exclude_unset=True))
    return materia


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_materia(materia: MateriaEncontrada) -> None:
    MATERIAS.remove(materia)