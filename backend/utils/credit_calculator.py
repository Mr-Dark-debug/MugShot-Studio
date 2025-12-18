from typing import Dict, Any


class InsufficientCreditsException(Exception):
    """Raised when a user doesn't have enough credits to perform an action."""
    """ implement later"""
    pass


# Credit costs based on the documentation
CREDIT_COSTS = {
    "draft": 1,        # Draft 512-768px: 1 credit
    "std": 2,          # Standard 1080p: 2 credits
    "4k": 4,           # 4K: 4 credits
    "copy_mode": 1,    # Add 1 credit if Copy mode with InstantID
    "provider_surcharge": {  # Provider surcharges
        "gemini_pro": 0,   # No surcharge for Gemini Pro (default)
        "gemini_flash": 0, # No surcharge for Gemini Flash
        "seedream": 1,     # Add 1 credit for Seedream
        "gpt_image": 2,    # Add 2 credits for GPT-Image
        "nano_banana": 0,  # No surcharge (default)
        "nano_banana_pro": 1  # Add 1 credit for Pro variant
    }
}

def calculate_job_credits(job_data: Dict[str, Any]) -> int:
    """
    Calculate the total credits required for a job based on quality, mode, and model.
    
    Args:
        job_data: Dictionary containing job information including:
            - quality: 'draft', 'std', or '4k'
            - mode: 'design' or 'copy'
            - model: model being used
    
    Returns:
        int: Total credits required for the job
    """
    base_credits = CREDIT_COSTS.get(job_data.get("quality", "std"), 2)
    
    # Add copy mode surcharge
    if job_data.get("mode") == "copy":
        base_credits += CREDIT_COSTS["copy_mode"]
    
    # Add provider surcharge
    model = job_data.get("model", "nano_banana")
    if model in CREDIT_COSTS["provider_surcharge"]:
        base_credits += CREDIT_COSTS["provider_surcharge"][model]
    
    return base_credits

def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model including capabilities and costs.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dict containing model information
    """
    model_info = {
        "nano_banana": {
            "name": "Nano Banana",
            "description": "Default Gemini model for fast image generation",
            "capabilities": ["text-to-image", "basic editing", "fast generation"],
            "default": True,
            "cost_surcharge": 0,
            "variants": ["nano_banana", "nano_banana_pro"]
        },
        "nano_banana_pro": {
            "name": "Nano Banana Pro",
            "description": "Advanced Gemini model with enhanced capabilities",
            "capabilities": ["text-to-image", "advanced editing", "higher resolution", "better quality"],
            "default": False,
            "cost_surcharge": 1,
            "variants": ["nano_banana", "nano_banana_pro"]
        },
        "seedream": {
            "name": "Seedream 4.0",
            "description": "ByteDance model for consistent image generation",
            "capabilities": ["identity preservation", "style consistency", "multi-image composition"],
            "default": False,
            "cost_surcharge": 1,
            "variants": ["seedream_4.0"]
        },
        "gemini_flash": {
            "name": "Gemini Flash",
            "description": "Fast Gemini model for quick iterations",
            "capabilities": ["text-to-image", "basic editing", "fast generation"],
            "default": False,
            "cost_surcharge": 0,
            "variants": ["gemini_flash"]
        },
        "gemini_pro": {
            "name": "Gemini Pro",
            "description": "Advanced Gemini model for high-quality outputs",
            "capabilities": ["text-to-image", "advanced editing", "high resolution", "complex compositions"],
            "default": False,
            "cost_surcharge": 0,
            "variants": ["gemini_pro"]
        }
    }
    
    return model_info.get(model_name, model_info["nano_banana"])