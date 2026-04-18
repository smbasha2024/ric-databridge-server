from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.routers import customer_router, user_router, email_router, databridge_router, auth_router

#from app.auth.auth import auth_middleware_call
from app.configs.settings import settings

app = FastAPI(
    title = settings.server.api_name,
    description = "This AI agent automates regulator-authorized portals to extract compliance evidence and integrates with the CMS to enable automatic closure.",
    version = settings.server.version
)

@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "error_code": exc.status_code,
            "error_desc": exc.detail
        }
    )

app.include_router(user_router.userRoutes)
app.include_router(customer_router.customerRoutes)
app.include_router(email_router.emailRoutes)
app.include_router(databridge_router.databridge_router)
app.include_router(auth_router.auth_router)

origins = settings.server.cors_urls
from app.auth.auth import AuthMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Middleware to check API key for all requests
app.add_middleware(AuthMiddleware)

@app.get("/")
def root():
    return {"message": f"Welcome to {app.title} {app.version}! {app.description}"}

@app.get("/health")
def health_check():
    return {"status": "Healthy", "service": "Data Bridge"}