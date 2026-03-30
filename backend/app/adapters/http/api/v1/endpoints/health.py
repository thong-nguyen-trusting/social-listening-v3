from fastapi import APIRouter, Depends

from app.adapters.http.dependencies import get_health_status_use_case
from app.adapters.http.schemas.health import HealthResponse
from app.application.use_cases.get_health_status import GetHealthStatusUseCase

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(
    use_case: GetHealthStatusUseCase = Depends(get_health_status_use_case),
) -> HealthResponse:
    return HealthResponse.from_entity(await use_case.execute())

