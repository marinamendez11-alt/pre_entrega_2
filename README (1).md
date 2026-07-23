# Pipeline de Extracción de Entidades Técnicas

Pipeline LCEL que recibe un párrafo de texto sin procesar (descripción de
arquitectura de software, log de error, etc.) y devuelve un objeto validado
con las tecnologías mencionadas, el nivel de criticidad y un resumen técnico.

## Estructura del proyecto

```
schemas.py       -> Modelo Pydantic EntidadesTecnicas (contrato de salida)
chain.py         -> Prompt + modelo con .with_structured_output() + .with_retry()
main.py          -> Script de prueba asíncrono (texto claro + texto ambiguo)
.env.example     -> Variables de entorno necesarias
requirements.txt
```

## Instalación

1. Creá y activá un entorno virtual con Python 3.12:

```bash
python -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
```

2. Instalá las dependencias:

```bash
pip install -r requirements.txt
```

3. Copiá `.env.example` a `.env` y completá tu API key:

```bash
cp .env.example .env
```

## Cómo correrlo

```bash
python main.py
```

Esto corre dos pruebas:
1. Un texto claro, con tecnologías explícitas (FastAPI, Redis, PostgreSQL).
2. Un texto ambiguo, sin tecnologías explícitas, para observar cómo el
   modelo y el validador se comportan ante un caso menos directo (prueba
   de estrés pedida en el ejercicio).

## Ejemplo de salida esperada

Dado un texto como:

> "Nuestra API en FastAPI está sufriendo timeouts intermitentes bajo carga.
> Usamos Redis como caché de sesión y PostgreSQL como base de datos
> principal..."

El pipeline devuelve:

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con caché en Redis y persistencia en PostgreSQL; cuello de botella en conexiones concurrentes."
}
```

## Cómo funciona la resiliencia

- `model.with_structured_output(EntidadesTecnicas)` fuerza al modelo a
  responder con un JSON que cumple el esquema Pydantic (tipos correctos,
  campos completos).
- `.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)` envuelve
  toda la cadena: si el LLM devuelve un JSON mal formado, incompleto (por
  ejemplo, cortado por límite de tokens) o que no pasa la validación de
  Pydantic (como la lista de tecnologías vacía), se reintenta automáticamente
  hasta 3 veces con backoff exponencial antes de fallar definitivamente.
- `process_text()` loguea cada intento y el resultado final (o el error, si
  se agotan los reintentos), para poder observar el comportamiento del
  pipeline en producción.

## Validaciones adicionales en el schema

Además de los tipos básicos, `schemas.py` incluye validadores personalizados
(`@field_validator`) que rechazan una lista de tecnologías vacía o un resumen
técnico vacío — si el modelo devolviera esos campos vacíos, la validación de
Pydantic falla y dispara el mecanismo de reintento de `.with_retry()`.
