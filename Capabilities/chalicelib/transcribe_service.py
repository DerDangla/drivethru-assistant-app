import boto3
import time
import requests
from botocore.exceptions import ClientError

class TranscribeService:
    def __init__(self):
        self.client = boto3.client('transcribe', region_name = 'us-east-1')

    def transcribe_sounds(self, job_name, file_uri):
        try:
            self.client.start_transcription_job(
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
                job = self.client.get_transcription_job(TranscriptionJobName=job_name)
                job_status = job['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    if job_status == 'COMPLETED':
                        transcript_file_uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                        # Fetch and return the transcribed text
                        transcript_response = requests.get(transcript_file_uri)
                        transcript_data = transcript_response.json()
                        return {'transcribedText': transcript_data['results']['transcripts'][0]['transcript'],
                                'transcribedTextScore': job['TranscriptionJob']['IdentifiedLanguageScore']} # Add the confidence score
                    else:
                        return {'error': 'Transcription failed'}
            return {'error': 'Transcription timed out'}
        except ClientError as e:
            return {'error': str(e)}
