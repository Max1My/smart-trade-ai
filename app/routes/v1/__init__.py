"""Include all v1 routes."""

import fastapi

from .sample import router as router_sample

router = fastapi.APIRouter(prefix="/v1")
router.include_router(router_sample)
