from azure.storage.blob import BlobServiceClient
from ExtractActionItems import extract_action_items
from ExtractTextFromMp4InAzure import extract_text_from_mp4
from ExtractTextFromPDFInAzure import extract_text_from_pdf_in_azure
from ExtractTextFromWordInAzure import extract_text_from_word_in_blob
from FileValidation import is_docs_file, is_pdf_file, is_valid_extension, is_video_file
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import Constants
from SummarizeTextAzureOpenAI import summarize_text_azure_openai
import uvicorn

app = FastAPI()

# FastAPI endpoint to check if the file extension is valid and uploadable
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        blob_service_client = BlobServiceClient.from_connection_string(Constants.storage_account_connection_string)
        blob_client = blob_service_client.get_blob_client(container=Constants.storage_account_container_name, blob=file.filename)
        blob_client.upload_blob(contents, overwrite=True)
        return JSONResponse(content={"message": f"Uploaded {file.filename} successfully."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# FastAPI endpoint to handle file upload and summarization
@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    if not is_valid_extension(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    # Upload the file to blob storage
    await upload_file(file)

    text = ""

    try:
        if is_docs_file(file.filename):
            text = extract_text_from_word_in_blob(Constants.storage_account_connection_string, Constants.storage_account_container_name, file.filename)
        elif is_pdf_file(file.filename):
            text = extract_text_from_pdf_in_azure(Constants.storage_account_connection_string, Constants.storage_account_container_name, file.filename)
        elif is_video_file(file.filename):
            text = extract_text_from_mp4(
                Constants.storage_account_connection_string,
                Constants.storage_account_container_name,
                file.filename,
                Constants.open_ai_endpoint,
                Constants.open_ai_api_key
            )

        summarize_text = summarize_text_azure_openai(text, Constants.open_ai_deployment_name, Constants.open_ai_endpoint, Constants.open_ai_api_key, Constants.open_ai_api_version)
        print("================================ Summary: ================================")
        print(summarize_text)
        print("================================ End Summary: ================================")

        action_items = extract_action_items(text, Constants.open_ai_deployment_name, Constants.open_ai_endpoint, Constants.open_ai_api_key, Constants.open_ai_api_version)
        print("================================ Action Items: ================================")
        print(action_items)
        print("================================ End Action Items: ================================")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content={"filename": file.filename, "summarize_text": summarize_text, "action_items": action_items}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )