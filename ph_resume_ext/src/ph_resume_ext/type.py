from pydantic import BaseModel, Field
from typing import Union, List, Dict, Optional, Any, Tuple

class Output_format(BaseModel):
    """Represents the factual data extracted from an document."""
    
    status: str = Field(
        None,
        description="Document content parsing status",
        enum=["Success", "Fail"]
    )
    First_Name: Optional[str] = None
    Last_Name: Optional[str] = None
    email_address: Optional[str] = None
    skills: List[str] = []
    phone_number: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    work_experience: Dict[str, Any] = {}
    education: Dict[str, Any] = {}
    certifications: Dict[str, Any] = {}