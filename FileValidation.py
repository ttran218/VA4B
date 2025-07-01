# Function to check if the file extension is valid
import Constants

def is_valid_extension(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in Constants.VALID_EXTENSIONS)

def is_docs_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in Constants.DOCS_EXTENSIONS)

def is_pdf_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in Constants.PDF_EXTENSIONS)

def is_video_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in Constants.VIDEO_EXTENSIONS)