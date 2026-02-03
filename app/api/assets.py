from fastapi import APIRouter, Depends, HTTPException
from app.services.asset_service import AssetService
from typing import Dict, List

router = APIRouter()

@router.get("/{project_id}/tree")
def get_asset_tree(project_id: int):
    try:
        return AssetService.list_assets(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/{asset_type}")
def list_specific_assets(project_id: int, asset_type: str):
    try:
        return AssetService.list_assets(project_id, asset_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
