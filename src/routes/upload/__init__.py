# This file is auto-generated by bearpath.py. Do not edit directly.

from typing import Any, Dict

from fastapi import APIRouter

from .base import router as base_router

router = APIRouter()
router.include_router(base_router, prefix='')

