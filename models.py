from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImageRecord(BaseModel):
    id: str
    prompt: str
    expected_style: str
    filename: str
    created_at: datetime
    generation_time: Optional[float] = None
    status: str = "completed"
    file_size: Optional[int] = None