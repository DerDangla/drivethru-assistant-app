from chalice import Chalice, BadRequestError, Response
import boto3
from datetime import datetime
import uuid
import json
import base64
import time
import requests
from botocore.exceptions import ClientError

app = Chalice(app_name='Capabilities')
app.debug = True
app.api.binary_types.append('multipart/form-data')

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe', region_name = 'us-east-1')
translate_client = boto3.client('translate')
BUCKET_NAME = 'contentcen301245113.aws.ai'

@app.route('/upload', methods=['POST'], cors = True)
def upload_to_s3():
    request_data = json.loads(app.current_request.raw_body)
    file_name = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.mp3'
    directory = f'uploads/{file_name}'
    file_bytes = base64.b64decode(request_data['filebytes'])
    
    s3_client.put_object(Bucket=BUCKET_NAME, Key=directory, Body=file_bytes, ContentType='audio/mp3', ACL = 'public-read')
    return {'filename': file_name}

@app.route('/transcribe', methods=['POST'], cors=True)
def transcribe_audio():
    try:
        request_data = json.loads(app.current_request.raw_body)
        file_key = request_data['fileKey']
        job_name = f"TranscriptionJob-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        file_uri = f'https://s3.amazonaws.com/{BUCKET_NAME}/uploads/{file_key}'
        
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='mp3',
            # LanguageCode='en-US'
            IdentifyLanguage=True
        )
        
        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            time.sleep(10)  # Wait before checking the job status
            job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = job['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                if job_status == 'COMPLETED':
                    transcript_file_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    # Fetch and return the transcribed text
                    transcript_response = requests.get(transcript_file_uri)
                    transcript_data = transcript_response.json()
                    return {'transcribedText': transcript_data['results']['transcripts'][0]['transcript']}
                else:
                    return {'error': 'Transcription failed'}
        return {'error': 'Transcription timed out'}
    except ClientError as e:
        return {'error': str(e)}
    
@app.route('/translate', methods=['POST'], cors=True)
def translate_text():
    try:
        request_data = json.loads(app.current_request.raw_body)
        text = request_data['text']
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode='en'
        )
        return {'translatedText': response.get('TranslatedText', '')}
    except ClientError as e:
        return {'error': str(e)}



