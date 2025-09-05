from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import re

class TextCleanerInput(BaseModel):
    """Input schema for TextCleaner Tool."""
    text: str = Field(..., description="The raw text content to be cleaned")

class TextCleanerTool(BaseTool):
    """Tool for cleaning and normalizing text content."""

    name: str = "TextCleanerTool"
    description: str = (
        "Cleans raw text by removing non-ASCII characters, normalizing whitespace, "
        "and removing control characters while preserving basic formatting and structure."
    )
    args_schema: Type[BaseModel] = TextCleanerInput

    def _run(self, text: str) -> str:
        try:
            # Handle empty or None input
            if not text or not isinstance(text, str):
                return ""
            
            # Remove control characters except for basic whitespace
            # Keep newlines, tabs, and spaces for structure
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
            
            # Remove non-ASCII characters but preserve basic punctuation and symbols
            # Allow ASCII printable characters (32-126) plus basic whitespace
            text = ''.join(char for char in text if ord(char) <= 127)
            
            # Normalize whitespace while preserving paragraph structure
            # Replace multiple spaces with single space
            text = re.sub(r' +', ' ', text)
            
            # Replace multiple tabs with single space
            text = re.sub(r'\t+', ' ', text)
            
            # Normalize line breaks - replace multiple newlines with double newline (paragraph break)
            text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
            
            # Remove trailing/leading whitespace from each line while preserving structure
            lines = text.split('\n')
            cleaned_lines = [line.strip() for line in lines]
            text = '\n'.join(cleaned_lines)
            
            # Remove leading and trailing whitespace from entire text
            text = text.strip()
            
            return text
            
        except Exception as e:
            # Return original text if cleaning fails
            return text if isinstance(text, str) else ""
