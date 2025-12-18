import os
import httpx
import base64
from core.config import get_settings
from utils.logger import logger
from utils.exceptions import ModelGenerationException

settings = get_settings()

class ByteDanceService:
    def __init__(self):
        self.api_key = settings.BYTEDANCE_API_KEY if hasattr(settings, 'BYTEDANCE_API_KEY') else os.getenv("BYTEDANCE_API_KEY")
        self.base_url = "https://ark-api.bytedance.com/api/v3/images/generations"  # Updated endpoint
        
    async def generate_image(self, prompt: str, model: str = "seedream-4.0", 
                           width: int = 1024, height: int = 1024, 
                           reference_images: list = None):
        """
        Generate image using ByteDance Seedream model.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use (default: seedream-4.0)
            width: Image width
            height: Image height
            reference_images: List of reference images as base64 strings
            
        Returns:
            List of base64 encoded images
        """
        if not self.api_key:
            raise ModelGenerationException("ByteDance API key not configured", "seedream-4.0")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload
        payload = {
            "model": model,
            "prompt": prompt,
            "width": width,
            "height": height,
            "response_format": "b64_json"
        }
        
        # Add reference images if provided
        if reference_images:
            payload["reference_images"] = reference_images
            
        logger.info(f"Generating image with Seedream model: {model}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url, 
                    json=payload, 
                    headers=headers, 
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract images
                images = []
                if "data" in data and len(data["data"]) > 0:
                    for item in data["data"]:
                        if "b64_json" in item:
                            images.append(item["b64_json"])
                
                logger.info(f"Successfully generated {len(images)} images with Seedream")
                return images
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error during Seedream generation: {str(e)}")
                raise ModelGenerationException(f"HTTP error during image generation: {str(e)}", model)
            except Exception as e:
                logger.error(f"Error generating image with Seedream: {str(e)}")
                raise ModelGenerationException(f"Failed to generate image: {str(e)}", model)