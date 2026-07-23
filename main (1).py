"""
main.py
-------
Mini-script de prueba: corre el pipeline con un par de textos de ejemplo,
incluyendo uno ambiguo para observar cómo se comporta el validador y la
lógica de reintento.
"""

import asyncio

from chain import process_text

TEXTO_CLARO = (
    "Nuestra API en FastAPI está sufriendo timeouts intermitentes bajo carga. "
    "Usamos Redis como caché de sesión y PostgreSQL como base de datos "
    "principal. El monitoreo muestra que el pool de conexiones a PostgreSQL "
    "se agota en los picos de tráfico, generando errores 504 para los usuarios."
)

TEXTO_AMBIGUO = (
    "El sistema anduvo raro ayer a la tarde, algunos usuarios reportaron que "
    "tardaba en cargar. No estamos seguros todavía de la causa."
)


async def main():
    print("=== Prueba 1: texto claro con tecnologías explícitas ===")
    resultado_1 = await process_text(TEXTO_CLARO)
    print(resultado_1.model_dump_json(indent=2))

    print("\n=== Prueba 2: texto ambiguo (prueba de estrés) ===")
    resultado_2 = await process_text(TEXTO_AMBIGUO)
    print(resultado_2.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
