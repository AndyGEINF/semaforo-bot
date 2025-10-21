from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Welcome to the Semáforo Bot API"}

@router.get("/status")
async def get_status():
    return {"status": "running"}

@router.get("/health")
async def health_check():
    return {"health": "ok"}

# Aquí puedes agregar más rutas según sea necesario.