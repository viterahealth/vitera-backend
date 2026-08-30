from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings

# ============================
# EXCEPTION HANDLERS
# ============================


async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "data": exc.errors()},
    )


async def unhandled_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "data": None},
    )


# ============================
# APP
# ============================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ============================
# ROUTERS
# ============================
# Each module (auth, patients, registrations, vitals, medical_history,
# consultations, ...) gets its own {module}/  folder with
# {module}_routes.py / {module}_schema.py / {module}_services.py.
# Import and include its router here, one line per module, as each is built.

from auth.auth_routes import router as auth_router
from registrations.registrations_routes import router as registrations_router
from camps.camps_routes import router as camps_router
from vitals.vitals_routes import router as vitals_router
from medical_history.medical_history_routes import router as history_router
from consultations.consultations_routes import router as consultations_router

app.include_router(auth_router)
app.include_router(registrations_router)
app.include_router(camps_router)
app.include_router(vitals_router)
app.include_router(history_router)
app.include_router(consultations_router)

# ============================
# HEALTH CHECK
# ============================


@app.get("/")
def health_check():
    return {"success": True, "message": "VITERA Camp API is running.", "data": None}