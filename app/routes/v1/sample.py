"""."""

from typing import Annotated

import fastapi
from auth.enums import ScopeEnum
from auth.schemas import TokenPayloadSchema
from auth.security import security
from dependency_injector.providers import Configuration
from dependency_injector.wiring import Provide, inject

router = fastapi.APIRouter(prefix="/sample", tags=["sample"])


@router.get("/")
@inject
async def sample(
    token_payload: Annotated[
        TokenPayloadSchema,
        fastapi.Security(security, scopes=[ScopeEnum.LOGS]),
    ],
    config: Configuration = fastapi.Depends(Provide["config"]),
) -> dict[str, str]:
    """Sample route."""
    return {"debug": config.debug}
