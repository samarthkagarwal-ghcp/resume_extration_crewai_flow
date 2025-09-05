from typing import Type
import os
import PyPDF2
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PDFReaderToolInput(BaseModel):
    """Input schema for PDFReaderTool."""
    file_path: str = Field(..., description="Path to the PDF file to be read. Can be absolute or relative path.")
    page_range: str = Field(
        "all",
        description="Range of pages to read. Format: 'all' for entire document, '1-5' for pages 1 to 5, '3' for just page 3."
    )


class PDFReaderTool(BaseTool):
    name: str = "PDF Reader"
    description: str = (
        "A tool that extracts text from PDF files. "
        "Provide the path to the PDF file and optionally specify which pages to read. "
        "Returns the extracted text content."
    )
    args_schema: Type[BaseModel] = PDFReaderToolInput

    def _run(self, file_path: str, page_range: str = "all") -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file
            page_range: Range of pages to read ('all', '1-5', '3', etc.)

        Returns:
            str: Extracted text from the PDF
        """
        # Ensure the file exists
        if not os.path.isfile(file_path):
            # Try to find the file in the attachments directory
            attachment_path = os.path.join("src", "emails", "attachments", file_path)
            if os.path.isfile(attachment_path):
                file_path = attachment_path
            else:
                return f"Error: File not found at {file_path}"

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                # Gather metadata
                metadata = f"PDF: {os.path.basename(file_path)}\n"
                metadata += f"Total Pages: {total_pages}\n"

                # Parse page range
                pages_to_read = []
                if page_range == "all":
                    pages_to_read = range(total_pages)
                    metadata += f"Pages Read: all (1-{total_pages})\n"
                else:
                    # Handle page ranges like "1-5" or single pages like "3"
                    if "-" in page_range:
                        start, end = map(int, page_range.split("-"))
                        # Convert to 0-based indexing and ensure within bounds
                        start = max(0, start - 1)
                        end = min(total_pages, end)
                        pages_to_read = range(start, end)
                        metadata += f"Pages Read: {page_range} (0-indexed: {start}-{end-1})\n"
                    else:
                        # Single page
                        page = int(page_range) - 1  # Convert to 0-based indexing
                        if 0 <= page < total_pages:
                            pages_to_read = [page]
                            metadata += f"Pages Read: {page_range} (0-indexed: {page})\n"

                # Add PDF document information if available
                if pdf_reader.metadata:
                    metadata += "\nDocument Information:\n"
                    for key, value in pdf_reader.metadata.items():
                        if value and str(value).strip():
                            metadata += f"- {key}: {value}\n"

                metadata += "\n--- Content Start ---\n\n"

                # Extract text
                all_text = ""
                for i in pages_to_read:
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text()

                    # Debug info for text extraction
                    page_info = f"--- Page {i+1} ---\n"
                    if not page_text or page_text.strip() == "":
                        page_info += f"[WARNING] No text extracted from page {i+1}. This could be an image-based page or content protection.\n"

                        # Add information about page objects
                        page_info += f"Page objects: {len(page.get_contents() or [])} content streams\n"
                        resources = page.get_resources()
                        if resources:
                            page_info += f"Resources: {', '.join(resources.keys())}\n"

                        # Report if page has XObjects (often images)
                        if resources and "/XObject" in resources:
                            page_info += f"Contains XObjects (possibly images): {len(resources['/XObject'])}\n"
                    else:
                        text_preview = page_text[:100].replace('\n', ' ').strip()
                        if len(page_text) > 100:
                            text_preview += "..."
                        page_info += f"Text preview: {text_preview}\n"
                        page_info += f"Text length: {len(page_text)} characters\n"

                    all_text += page_info + "\n"
                    if page_text:
                        all_text += page_text + "\n"
                    all_text += "\n--- Page Break ---\n\n"

                return metadata + all_text

        except Exception as e:
            return f"Error reading PDF: {str(e)}"
