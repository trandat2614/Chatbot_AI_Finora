"""Aggregate /api/v1 routers."""
from fastapi import APIRouter

from src.api.routes import business, chat, data, knowledge, market, planning, products

router = APIRouter()
router.include_router(data.router)
router.include_router(business.router)
router.include_router(products.router)
router.include_router(market.router)
router.include_router(chat.router)
router.include_router(planning.router)
router.include_router(knowledge.router)
