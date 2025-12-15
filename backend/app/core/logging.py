"""
Logging configuration for the application.

Sets up structured logging and optional Sentry integration
for production error tracking.
"""

import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    Configure application logging.
    
    Sets up standard logging to stdout and optionally
    initializes Sentry for production error tracking.
    """
    # Configure structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Initialize Sentry if configured
    if hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    FastApiIntegration(),
                ],
                traces_sample_rate=0.5,
                profiles_sample_rate=0.5,
            )
            logging.info("Sentry initialized successfully")
        except Exception as e:
            logging.warning(f"Failed to initialize Sentry: {e}")
