# File: backend/data/patch_tracker.py
# Purpose: Track and manage patch data and meta changes

"""
Patch Tracker
Monitors League of Legends patches and tracks meta changes
Stores patch notes and change history
"""

import boto3
import json
from typing import Dict, List, Any
from datetime import datetime

from backend.utils.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class PatchTracker:
    """
    Tracks patch versions and associated meta changes
    """
    
    def __init__(self):
        """Initialize S3 client for patch data storage"""
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket = settings.S3_BUCKET
        logger.info("Patch Tracker initialized")
    
    async def store_patch_data(
        self,
        patch_version: str,
        patch_notes: Dict[str, Any]
    ) -> bool:
        """
        Store patch notes and metadata
        
        Args:
            patch_version: Patch version (e.g., "14.21")
            patch_notes: Patch notes and change data
            
        Returns:
            Success status
        """
        try:
            key = f"patches/{patch_version}/metadata.json"
            
            data = {
                "patch_version": patch_version,
                "release_date": datetime.utcnow().isoformat(),
                "patch_notes": patch_notes,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            
            logger.info(f"Stored patch data for {patch_version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store patch data: {e}")
            return False
    
    async def get_patch_metadata(self, patch_version: str) -> Dict[str, Any]:
        """
        Retrieve patch metadata
        
        Args:
            patch_version: Patch version
            
        Returns:
            Patch metadata dictionary
        """
        try:
            key = f"patches/{patch_version}/metadata.json"
            
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = json.loads(response['Body'].read())
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve patch metadata: {e}")
            return {}
    
    async def get_patch_timeline(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get patch timeline within date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of patches in chronological order
        """
        try:
            # List all patch files
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix="patches/"
            )
            
            patches = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('metadata.json'):
                    patch_data = await self.get_patch_metadata(
                        obj['Key'].split('/')[1]
                    )
                    
                    release_date = datetime.fromisoformat(patch_data.get('release_date', ''))
                    if start_date <= release_date <= end_date:
                        patches.append(patch_data)
            
            # Sort by release date
            patches.sort(key=lambda x: x['release_date'])
            
            return patches
            
        except Exception as e:
            logger.error(f"Failed to get patch timeline: {e}")
            return []
