"""
chain.py
--------
Cadena LCEL que recibe un párrafo de texto sin procesar (descripción de
arquitectura, log de error, etc.) y devuelve un objeto EntidadesTecnicas
ya validado por Pydantic, usando .with_structured_output() del modelo
y .with_retry() para manejar salidas mal formadas o incompletas.

Soporta OpenAI, Anthropic o Google Gemini según la variable de entorno
LLM_PROVIDER en el .env (openai / anthropic / google).
"""

import logging
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from schemas import EntidadesTecnicas

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("pipeline_entidades")


def construir_modelo():
    """Instancia el modelo base según LLM_PROVIDER (openai / anthropic / google)."""
    proveedor = os.getenv("LLM_PROVIDER", "google").lower()

    if proveedor == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-flash-latest"),
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    elif proveedor == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif proveedor == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            temperature=0,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
    raise ValueError(f"LLM_PROVIDER desconocido: {proveedor}")


# --- 1. Prompt modular, sin f-strings hardcodeadas ---
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos un analista técnico. Tu tarea es leer un texto (puede ser una "
            "descripción de arquitectura de software o un log de error) y extraer "
            "de forma estructurada: las tecnologías mencionadas, el nivel de "
            "criticidad del problema (baja, media o alta) y un resumen técnico breve. "
            "Si el texto es ambiguo o no menciona tecnologías claras, igual completá "
            "los campos con tu mejor estimación fundamentada, nunca dejes la lista "
            "de tecnologías vacía sin intentar inferir al menos una.",
        ),
        ("human", "Texto a analizar:\n\n{texto}"),
    ]
)

# --- 2 y 3. Modelo + salida estructurada, encadenado con | ---
_modelo_base = construir_modelo()
_modelo_estructurado = _modelo_base.with_structured_output(EntidadesTecnicas)

# --- 4. Resiliencia: reintento automático ante fallos de validación/formato ---
chain = (prompt | _modelo_estructurado).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)


async def process_text(texto: str) -> EntidadesTecnicas:
    """Punto de entrada asíncrono del pipeline: recibe texto crudo y
    devuelve un EntidadesTecnicas validado, con logging del proceso."""
    logger.info("Procesando texto de entrada (%d caracteres)", len(texto))
    try:
        resultado = await chain.ainvoke({"texto": texto})
        logger.info(
            "Extracción exitosa: %d tecnologías, criticidad=%s",
            len(resultado.tecnologias),
            resultado.nivel_de_criticidad.value,
        )
        return resultado
    except Exception as e:
        logger.error("Fallo la extracción tras reintentos: %s", str(e))
        raise
