import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "image_generation")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "generated_images")
    
    # Hugging Face
    HF_API_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_API_URL: str = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0")
    
    # App
    IMAGES_DIR: str = "generated_images"
    
    # Style options
    STYLES = {
        "realistic": "photorealistic, high quality, detailed, 8k resolution",
        "cartoon": "cartoon style, animated, colorful, disney style",
        "cyberpunk": "cyberpunk style, neon lights, futuristic, sci-fi",
        "fantasy": "fantasy art, magical, ethereal, mystical",
        "abstract": "abstract art, artistic, creative, modern art"
    }

settings = Settings()