# MyEvents Backend

API REST para gestión de eventos, construida con FastAPI. Prueba técnica para Tusdatos.

## Stack

- **FastAPI** + **Uvicorn**
- **SQLModel** sobre **PostgreSQL** (driver `psycopg2`)
- **Alembic** para migraciones
- **JWT** (python-jose) con hashing de contraseñas vía **Passlib (Argon2)**
- **Poetry** para gestión de dependencias
- **Docker / docker-compose**

## Requisitos

- Python 3.12+
- Poetry
- Docker y docker-compose (opcional, para levantar el stack completo)

## Configuración

Copia el archivo de ejemplo y ajusta los valores:

```bash
cp .env.example .env
```

Variables principales:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL |
| `JWT_SECRET_KEY` | Secreto para firmar los tokens JWT |
| `JWT_ALGORITHM` | Algoritmo de firma (default `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiración del refresh token |

## Uso con Docker

```bash
docker-compose up --build
```

La API queda disponible en `http://localhost:8000` y Postgres en el puerto `5432`.

## Uso local (sin Docker)

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

Asegúrate de tener una instancia de PostgreSQL accesible y `DATABASE_URL` apuntando a ella (usa `localhost` en vez de `db` como host).

## Migraciones

```bash
poetry run alembic upgrade head
```

Para generar una nueva migración:

```bash
poetry run alembic revision --autogenerate -m "descripcion"
```

## Tests

```bash
poetry run pytest
```

Con cobertura:

```bash
poetry run pytest --cov
```

## Documentación de la API

Con el servidor corriendo, la documentación interactiva está disponible en:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estructura del proyecto

```
app/
├── api/v1/        # Routers y endpoints
├── core/          # Configuración, seguridad
├── db/            # Sesión y engine de base de datos
├── models/        # Modelos SQLModel
├── repositories/  # Acceso a datos
├── schemas/       # Esquemas Pydantic
└── services/      # Lógica de negocio
alembic/           # Migraciones
tests/             # Pruebas
```
