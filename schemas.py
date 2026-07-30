"""
schemas.py
----------
Define el "contrato" de salida validada para el pipeline de extracción
de entidades técnicas: qué tecnologías se mencionan, qué tan crítico es
el problema descrito, y un resumen técnico breve.
"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class NivelCriticidad(str, Enum):
    baja = "baja"
    media = "media"
    alta = "alta"


class EntidadesTecnicas(BaseModel):
    tecnologias: list[str] = Field(
        description="Lista de tecnologías, frameworks o herramientas mencionadas en el texto (ej. FastAPI, Redis, PostgreSQL)."
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Nivel de criticidad del problema o arquitectura descrita: baja, media o alta."
    )
    resumen_tecnico: str = Field(
        description="Resumen técnico breve (1-2 oraciones) de lo que describe el texto."
    )

    @field_validator("tecnologias")
    @classmethod
    def tecnologias_no_vacia(cls, valor: list[str]) -> list[str]:
        if not valor:
            raise ValueError("La lista de tecnologías no puede estar vacía.")
        return valor

    @field_validator("resumen_tecnico")
    @classmethod
    def resumen_no_vacio(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("El resumen técnico no puede estar vacío.")
        return valor
