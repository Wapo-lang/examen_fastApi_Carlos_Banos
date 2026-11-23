# app/esquemas.py
from pydantic import BaseModel, Field


class MateriaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    creditos: int = Field(ge=1, le=10)
    semestre: int = Field(ge=1, le=10)
    obligatoria: bool = True


class MateriaCrear(MateriaBase):
    # Tres letras mayúsculas + tres dígitos: MAT101, PRG201...
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class MateriaActualizar(BaseModel):
    # Todos opcionales: en un PUT parcial, lo que no se envía no se toca.
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    creditos: int | None = Field(default=None, ge=1, le=10)
    semestre: int | None = Field(default=None, ge=1, le=10)
    obligatoria: bool | None = None


class Materia(MateriaCrear):
    """Lo que la API devuelve: los cinco campos completos."""