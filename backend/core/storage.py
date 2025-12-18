from core.config import settings

class StorageConfig:
    """Centralized storage configuration for Supabase buckets."""
    
    PROFILE_PHOTOS_BUCKET = settings.PROFILE_PHOTOS_BUCKET
    USER_ASSETS_BUCKET = settings.USER_ASSETS_BUCKET
    RENDERS_BUCKET = settings.RENDERS_BUCKET
    
    @classmethod
    def get_bucket_name(cls, asset_type: str) -> str:
        """
        Get the appropriate bucket name for an asset type.
        
        Args:
            asset_type: The type of asset ('profile_photo', 'render', or other)
            
        Returns:
            The bucket name for the asset type
        """
        if asset_type == "profile_photo":
            return cls.PROFILE_PHOTOS_BUCKET
        elif asset_type == "render":
            return cls.RENDERS_BUCKET
        else:
            return cls.USER_ASSETS_BUCKET