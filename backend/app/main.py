from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routes import example as example_route
from .routes import admin as admin_route
from .routes import candidate as candidate_route
from .routes import webhooks as webhooks_route
from .config import get_settings

app = FastAPI(title="Backend API")

# Configure CORS to explicitly allow the frontend origin, which is required when
# allow_credentials=True. Using "*" is not permitted with credentials per the spec.
settings = get_settings()

# Explicitly allow the frontend origin so CORS headers are emitted on all responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://afterqueryapp-production.vercel.app",
        "https://*.vercel.app",  # For preview deployments
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers to ensure CORS headers are always included
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Ensure CORS headers in HTTP exceptions."""
    # Don't interfere with OPTIONS requests - CORS middleware handles them
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "https://afterqueryapp-production.vercel.app",
                "Access-Control-Allow-Credentials": "false",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "https://afterqueryapp-production.vercel.app",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Ensure CORS headers in validation errors."""
    # Don't interfere with OPTIONS requests - CORS middleware handles them
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "false",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and ensure CORS headers are included.
    This ensures browser can see error messages even when backend fails.
    """
    # Don't interfere with OPTIONS requests - CORS middleware handles them
    if request.method == "OPTIONS":
        from starlette.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "false",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "type": type(exc).__name__},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

app.include_router(example_route.router)
app.include_router(admin_route.router)
app.include_router(candidate_route.router)
app.include_router(webhooks_route.router)
