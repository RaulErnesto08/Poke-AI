# Febara PokeAPI – Fullstack Demo (FastAPI + Streamlit + OpenAI)

Un proyecto completo y compacto para gestionar Pokémon con:

- **Autenticación (JWT)**
- **Mi Colección** (agregar/eliminar Pokémon)
- **Teams** (N equipos, 1–6 Pokémon cada uno; solo de tu colección)
- **Funciones IA**:
  - **Identify** (imagen → Pokémon → detalles)
  - **Comparar** dos Pokémon (análisis asistido por IA)
  - **Recomendaciones** según tu colección
  - **Auto Team Builder** (crea un equipo de 6)
  - **Fun Facts** (curiosidades generadas por IA)

Backend en **FastAPI** con **SQLite**. Frontend en **Streamlit**. Dependencias usando **uv**.

---

## 🧱 Arquitectura

```
/backend
  app/
    api/routers/
    core/
    domain/
    infra/
    main.py
  .env.example
  uv.lock

/frontend-streamlit
  pages/
  utils/
  .env.example
  uv.lock
README.md
```

---

# Quickstart Detallado (uv + FastAPI + Streamlit)

## ✅ 0) Instalar uv (si aún no lo tienes)

uv es un reemplazo moderno para pip/venv.  
Instálalo así:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verifica que está instalado:

```bash
uv --version
```

---

## ✅ 1) Crear entorno virtual con uv

En cada carpeta (backend y frontend) debes crear un entorno virtual:

```bash
uv venv
```

Esto crea un `.venv/` automático.  
uv detecta y activa ese entorno al usar `uv run`.

---

## ✅ 2) Instalar dependencias (uv sync)

Cada proyecto tiene su `uv.lock`, así que solo debes correr:

### Backend:
```bash
cd backend
uv sync
```

### Frontend:
```bash
cd ../frontend-streamlit
uv sync
```

Esto instala todo exactamente como se definió en `uv.lock`.

---

## ✅ 3) Copiar archivos .env.example

### Backend
```bash
cp backend/.env.example backend/.env
```

El archivo contiene:

```env
DATABASE_URL=sqlite:///./test.db
JWT_SECRET=supersecret
JWT_ALGORITHM=HS256
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
POKEAPI_TIMEOUT_SECONDS=5.0
POKEAPI_RETRIES=2
CACHE_TTL_SECONDS=43200
```

### Frontend
```bash
cp frontend-streamlit/.env.example frontend-streamlit/.env
```

Contenido:

```env
API_URL=http://127.0.0.1:8000
```

---

## ✅ 4) Ejecutar Backend

Dentro de `/backend`:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Se iniciará en:

- API → http://127.0.0.1:8000
- Swagger → http://127.0.0.1:8000/docs
- ReDoc → http://127.0.0.1:8000/redoc
- Postman → Importar archivo `PokeAPI.postman_collection.json` en Postman

---

## ✅ 5) Ejecutar Frontend

Dentro de `/frontend-streamlit`:

```bash
uv run streamlit run main.py
```

O puedes especificar puerto:

```bash
uv run streamlit run main.py --server.port=8501
```

Frontend disponible en:

👉 http://127.0.0.1:8501

---

## ✅ 6) Flujo completo

1. Corre backend (FastAPI)
2. Corre frontend (Streamlit)
3. Login → token guardado en session_state
4. Acceso a todas las páginas:
   - Pokédex
   - Mi Colección
   - Teams
   - IA (Identify, Compare, Recommend, Auto Team Builder, Fun Facts)

---

## ✅ 7) Notas importantes

### Sobre uv:
- No se usa `pip install`
- No se usa `requirements.txt`
- No hace falta `python -m venv`
- uv maneja todo con `uv.lock` + `uv sync`

### Sobre SQLite:
- archivo local, muy simple para desarrollo
- no requiere instalación externa
- se crea automáticamente

### Sobre variables de entorno:
- si cambias puertos, asegúrate de también cambiar `API_URL` en frontend
- backend → siempre debe correr antes que el frontend

---

## ✅ 8) Problemas comunes

### ❌ Streamlit no mantiene sesión
Solución: revisar el manejo de `session_state` y tokens.

### ❌ No conecta con backend
Solución:
- backend debe estar en `:8000`
- frontend debe tener `API_URL=http://127.0.0.1:8000`

### ❌ Swagger no muestra nada
Solución:
- confirmar `uvicorn` levantó sin errores
- revisar `.env`

---

# 🔌 MCP Server – Integración opcional

Este proyecto incluye un **MCP Server** compatible con el estándar **Model Context Protocol (MCP)**, permitiendo exponer herramientas del backend como "tools" accesibles por clientes LLM compatibles (Claude Desktop, MCP Inspector, etc.).

---

## ✅ Estructura del MCP Server
```
MCP Client → SSE → MCP Server → FastAPI → PokeAPI
```

--- 

## ✅ Requisitos

Antes de ejecutar el MCP Server:

- Backend FastAPI en **http://127.0.0.1:8000**
- Access Token válido (JWT)
- `.env` configurado correctamente en `/mcp-server`

---

## ✅ Instalación

```bash
cd mcp-server
uv venv # activar .venv
uv sync
cp .env.example .env
```

Editar `.env`:

```env
API_URL=http://127.0.0.1:8000
AUTH_TOKEN=TU_ACCESS_TOKEN_AQUI
```

---

## ✅ Ejecución

Iniciar el MCP Server:

```bash
uv run uvicorn main:app --reload --port 5000
```

El MCP server estará activo en:

```
http://127.0.0.1:5000/sse
```

---

## ✅ Probar en MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://127.0.0.1:5000/sse
```

Esto mostrará:

✅ Tools registradas  
✅ Schemas detectados  
✅ Ejecución en vivo  

---


## ✅ Probar en Cursor o VS Code (MCP Client)

Para usar tu MCP Server dentro de un MCP-enabled editor como Cursor o VS Code (con MCP extension), agrega la configuración en tu mcp.json:

{
  "Poke-MCP": {
    "type": "sse",
    "url": "http://0.0.0.0:5000/sse"
  }
}

✅ Detectará automáticamente
✅ Listará las tools del servidor
✅ Podrás preguntarle al LLM cualquier cosa relacionada con la API

---

## ✅ Tools disponibles

El servidor MCP expone wrappers de endpoints del backend:

- pokedex_lookup
- pokedex_search
- pokedex_random
- collection_add
- collection_remove
- collection_list
- teams_list
- teams_create
- teams_add
- teams_remove
- ai_identify
- ai_compare
- ai_recommendations
- ai_auto_team
- ai_fun_facts

---

## ✅ Flujo MCP + PokeAPI

1. Cliente MCP detecta las tools
2. Envía instrucciones naturales
3. MCP server las traduce a llamadas HTTP reales
4. Backend responde datos normalizados
5. Cliente LLM presenta resultados inteligentemente

---

## ✅ Errores comunes en el MCP Server

### 1) Token inválido
Solución: renovar desde el login en el backend.

---


## ✅ Resumen

| Componente | Comando |
|-----------|---------|
| Instalar deps | `uv sync` |
| Backend | `uv run uvicorn app.main:app --reload` |
| Frontend | `uv run streamlit run main.py` |
| MCP-Server | `uv run uvicorn main:app --reload --port 5000` |
| Variables | copiar `.env.example` → `.env` |
| Docs API | `/docs` , `/redoc` y `Postman` |

---

## 📚 Funcionalidad

### Pokédex
- Buscar
- Sugerencias
- Random
- Explorar por ID

### Colección (Auth)
- Agregar/Eliminar Pokémon

### Teams (Auth)
- Crear, renombrar, agregar, eliminar
- Auto Team Builder (IA)

### IA
- Identify (imagen)
- Compare
- Recommendations
- Fun Facts

---

## ✅ Mejoras y pendientes

### Issues actuales
- No hay cache persistente real por limitaciones de Streamlit
- Streamlit a veces requiere doble rerender
- No hay paginación en endpoints
- No hay validaciones estrictas en frontend

### Mejoras futuras
- Tests unitarios y de integración
- UI más pulida (React)
- Manejo de errores centralizado
- Añadir throttling / rate‑limit

---
