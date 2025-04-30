from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class ServiceRequest(BaseModel):
    title: str
    icon: str
    description: str

