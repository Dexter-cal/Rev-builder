import os
import shutil
from typing import Optional

class AssetService:
    STORAGE_ROOT = "storage"

    @classmethod
    def get_project_dir(cls, project_id: int) -> str:
        path = os.path.join(cls.STORAGE_ROOT, f"project_{project_id}")
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def get_asset_path(cls, project_id: int, asset_type: str, filename: str) -> str:
        """
        asset_type can be 'binaries', 'reports', 'payloads', 'firmware_extracted', 'source'
        """
        base_dir = cls.get_project_dir(project_id)
        asset_dir = os.path.join(base_dir, asset_type)
        os.makedirs(asset_dir, exist_ok=True)
        return os.path.join(asset_dir, filename)

    @classmethod
    def save_asset(cls, project_id: int, asset_type: str, filename: str, content: bytes) -> str:
        path = cls.get_asset_path(project_id, asset_type, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path

    @classmethod
    def list_assets(cls, project_id: int, asset_type: Optional[str] = None):
        base_dir = cls.get_project_dir(project_id)
        if asset_type:
            target_dir = os.path.join(base_dir, asset_type)
            if not os.path.exists(target_dir):
                return []
            return os.listdir(target_dir)

        # If no asset_type, return a tree structure
        tree = {}
        for folder in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder)
            if os.path.isdir(folder_path):
                tree[folder] = os.listdir(folder_path)
        return tree
