# config.py
"""Configuration management for the Weather App."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Configuration
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL", 
        "https://api.openweathermap.org/data/2.5/weather"
    )
    
    # App Configuration
    APP_TITLE = "Weather App"
    APP_WIDTH = 400
    APP_HEIGHT = 600
    
    # API Settings
    UNITS = "metric"  # metric, imperial, or standard
    TIMEOUT = 10  # seconds
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY:
            raise ValueError(
                "OPENWEATHER_API_KEY not found. "
                "Please create a .env file with your API key."
            )
        return True

# config.py

CUSTOM_ICONS = {
    "01d": "01d.png",
    "01n": "01n.png",
    "02d": "02d.png",
    "02n": "02n.png",
    "03d": "03d.png",
    "03n": "03n.png",
    "04d": "04d.png",
    "04n": "04n.png",
    "09d": "09d.png",
    "09n": "09n.png",
    "10d": "10d.png",
    "10n": "10n.png",
    "11d": "11d.png",
    "11n": "11n.png",
    "13d": "13d.png",
    "13n": "13n.png",
    "50d": "50d.png",
    "50n": "50n.png",
}


# Validate configuration on import
Config.validate()