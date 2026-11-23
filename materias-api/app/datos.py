# app/datos.py
# Nuestra "base de datos": una lista de diccionarios a nivel de módulo.
# Vive en memoria: se reinicia cada vez que el servidor recarga.
MATERIAS: list[dict] = [
    {"codigo": "MAT101", "nombre": "Cálculo I",            "creditos": 4, "semestre": 1, "obligatoria": True},
    {"codigo": "PRG101", "nombre": "Programación I",       "creditos": 5, "semestre": 1, "obligatoria": True},
    {"codigo": "FIS201", "nombre": "Física General",       "creditos": 4, "semestre": 2, "obligatoria": True},
    {"codigo": "PRG201", "nombre": "Estructuras de Datos", "creditos": 5, "semestre": 2, "obligatoria": True},
    {"codigo": "BDD301", "nombre": "Bases de Datos",       "creditos": 4, "semestre": 3, "obligatoria": True},
    {"codigo": "WEB301", "nombre": "Desarrollo Web",       "creditos": 3, "semestre": 3, "obligatoria": False},
    {"codigo": "ETI401", "nombre": "Ética Profesional",    "creditos": 2, "semestre": 4, "obligatoria": False},
]