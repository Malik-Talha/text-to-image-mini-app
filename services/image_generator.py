import os

import logging
from huggingface_hub import InferenceClient
from io import BytesIO

from config import settings

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.model = os.getenv("MODEL", "stabilityai/stable-diffusion-xl-base-1.0")

        self.client = InferenceClient(
            provider=os.getenv("PROVIDER", "nebius"),
            api_key=os.environ["HF_TOKEN"],
        )

    
    def enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt based on selected style"""
        enhancement = settings.STYLES.get(style, "")
        return f"{prompt}, {enhancement}" if enhancement else prompt
    
    def generate_image(self, prompt: str, style: str = "realistic") -> bytes:
        """Generate image using Hugging Face API"""
        if not settings.HF_API_TOKEN:
            raise ValueError("❌ Hugging Face API token not configured")
        
        enhanced_prompt = self.enhance_prompt(prompt, style)
        
        try:
            # output is a PIL.Image object
            image = self.client.text_to_image(
                enhanced_prompt,
                model=self.model,
            )

            buffer = BytesIO()
            image.save(buffer, format="PNG")  # Or JPEG, WEBP etc.
            image_bytes = buffer.getvalue()   # byte-like data 

            return image_bytes
    
        except Exception as e:
            print(f"Failed to Generate the image: {e}")
            return None