from azure.storage.blob import BlobServiceClient
from io import BytesIO
from docx import Document

# Function to extract text from a Word file stored in Azure Blob Storage
def extract_text_from_word_in_blob(storage_account_connection_string, storage_account_container_name, blob_name):
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(storage_account_connection_string)
    container_client = blob_service_client.get_container_client(storage_account_container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Download the blob (Word file) as bytes
    blob_data = blob_client.download_blob().readall()
    word_file = BytesIO(blob_data)

    # Read the Word file and extract text
    doc = Document(word_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text