from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.datos import RUTAS
from app.esquemas import (
    CoberturaConductorSalida,
    ProyeccionIngresosSalida,
    RutaActualizar,
    RutaCrear,
    RutaSalida,
)

router = APIRouter(prefix="/transporte/rutas", tags=["rutas"])


def obtener_ruta(codigo: str) -> dict:
    """Devuelve el diccionario de la ruta o lanza 404 (comparando en mayúsculas)."""
    codigo_upper = codigo.upper()
    for ruta in RUTAS:
        if ruta["codigo"].upper() == codigo_upper:
            return ruta
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la ruta '{codigo_upper}'",
    )


RutaEncontrada = Annotated[dict, Depends(obtener_ruta)]

# PREGUNTA 1: CRUD de rutas

@router.get("", response_model=list[RutaSalida], status_code=status.HTTP_200_OK)
def listar_rutas(
    zona: Annotated[int | None, Query(ge=1, le=8)] = None,
    nocturna: Annotated[bool | None, Query()] = None,
) -> list[dict]:
    resultado = []
    for ruta in RUTAS:
        if zona is not None and ruta["zona"] != zona:
            continue
        if nocturna is not None and ruta["nocturna"] is not nocturna:
            continue
        resultado.append(ruta)
    return resultado


@router.post("", response_model=RutaSalida, status_code=status.HTTP_201_CREATED)
def crear_ruta(nueva: RutaCrear) -> dict:
    for ruta in RUTAS:
        if ruta["codigo"].upper() == nueva.codigo.upper():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una ruta con el código '{nueva.codigo}'",
            )
    registro = nueva.model_dump()
    RUTAS.append(registro)
    return registro


# PREGUNTA 2 y 3

@router.get(
    "/proyeccion-ingresos",
    response_model=ProyeccionIngresosSalida,
    status_code=status.HTTP_200_OK,
)
def proyeccion_ingresos(
    frecuencias: Annotated[int, Query(ge=1, le=20)],
    zona: Annotated[int | None, Query(ge=1, le=8)] = None,
) -> ProyeccionIngresosSalida:
    seleccion = [ruta for ruta in RUTAS if zona is None or ruta["zona"] == zona]
    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay rutas para la zona '{zona}'",
        )

    cantidad = len(seleccion)
    suma_tarifas_base = 0
    suma_tarifas_recargo = 0.0
    rutas_con_recargo = 0

    for ruta in seleccion:
        tarifa_base = ruta["tarifa"]
        suma_tarifas_base += tarifa_base
        if ruta["nocturna"]:
            rutas_con_recargo += 1
            suma_tarifas_recargo += tarifa_base * 1.20
        else:
            suma_tarifas_recargo += float(tarifa_base)

    return ProyeccionIngresosSalida(
        rutas=cantidad,
        frecuencias=frecuencias,
        tarifa_promedio=round(suma_tarifas_base / cantidad, 2),
        ingreso_diario=round(suma_tarifas_recargo * frecuencias, 2),
        rutas_con_recargo=rutas_con_recargo,
        porcentaje_nocturnas=round((rutas_con_recargo / cantidad) * 100, 1),
    )


@router.get(
    "/cobertura-conductor",
    response_model=CoberturaConductorSalida,
    status_code=status.HTTP_200_OK,
)
def cobertura_conductor(
    asignadas: Annotated[list[str] | None, Query()] = None,
) -> CoberturaConductorSalida:
    if not RUTAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay rutas registradas en el sistema",
        )

    set_asignadas = {codigo.upper() for codigo in asignadas} if asignadas else set()

    total = 0
    cant_asignadas = 0
    cant_pendientes = 0
    tarifa_pendiente_total = 0
    mayor_tarifa = -1
    pendiente_mas_cara: str | None = None

    for ruta in RUTAS:
        total += 1
        if ruta["codigo"].upper() in set_asignadas:
            cant_asignadas += 1
        else:
            cant_pendientes += 1
            tarifa_pendiente_total += ruta["tarifa"]
            if ruta["tarifa"] > mayor_tarifa:
                mayor_tarifa = ruta["tarifa"]
                pendiente_mas_cara = ruta["codigo"]

    return CoberturaConductorSalida(
        total=total,
        asignadas=cant_asignadas,
        pendientes=cant_pendientes,
        porcentaje_cobertura=round((cant_asignadas / total) * 100, 1),
        tarifa_pendiente_total=tarifa_pendiente_total,
        pendiente_mas_cara=pendiente_mas_cara,
    )


@router.get("/{codigo}", response_model=RutaSalida, status_code=status.HTTP_200_OK)
def ver_ruta(ruta: RutaEncontrada) -> dict:
    return ruta


@router.patch("/{codigo}", response_model=RutaSalida, status_code=status.HTTP_200_OK)
def actualizar_ruta(ruta: RutaEncontrada, cambios: RutaActualizar) -> dict:
    datos_actualizados = cambios.model_dump(exclude_unset=True)
    ruta.update(datos_actualizados)
    return ruta


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ruta(ruta: RutaEncontrada) -> Response:
    RUTAS.remove(ruta)
    return Response(status_code=status.HTTP_204_NO_CONTENT)