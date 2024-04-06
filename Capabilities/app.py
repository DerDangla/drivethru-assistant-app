from chalice import Chalice
from datetime import datetime
import json, base64
from chalicelib import storage_service, transcribe_service, translation_service

app = Chalice(app_name='Capabilities')
app.debug = True

bucket_name = 'xxxx.aws.ai'

storage_service = storage_service.StorageService(bucket_name)
transcribe_service = transcribe_service.TranscribeService()
translation_service = translation_service.TranslationService()

@app.route('/upload', methods=['POST'], cors = True)
def upload_to_s3():
    request_data = json.loads(app.current_request.raw_body)
    file_name = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.mp3'
    file_bytes = base64.b64decode(request_data['filebytes'])
        
    image_info = storage_service.upload_file(file_bytes, file_name)
        
    return image_info


@app.route('/transcribe', methods=['POST'], cors=True)
def transcribe_audio():
    request_data = json.loads(app.current_request.raw_body)
    file_key = request_data['fileKey']
    job_name = f"TranscriptionJob-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    file_uri = f'https://s3.amazonaws.com/{bucket_name}/uploads/{file_key}'
        
    transcribed_message = transcribe_service.transcribe_sounds(job_name, file_uri)
    
    return transcribed_message


@app.route('/translate', methods=['POST'], cors=True)
def translate_text():
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']
        
    translatedText = translation_service.translate_text(text, target_language = request_data['targetLanguage'])
        
    return translatedText
