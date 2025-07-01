from azure.storage.blob import BlobServiceClient
from io import BytesIO
import PyPDF2

# Function to extract text from a PDF file stored in Azure Blob Storage
def extract_text_from_pdf_in_azure(storage_account_connection_string, storage_account_container_name, blob_name):
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(storage_account_connection_string)
    container_client = blob_service_client.get_container_client(storage_account_container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Download PDF blob as bytes
    pdf_bytes = blob_client.download_blob().readall()
    pdf_stream = BytesIO(pdf_bytes)

    # Extract text from PDF
    reader = PyPDF2.PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text