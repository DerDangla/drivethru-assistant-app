import boto3
from botocore.exceptions import ClientError

class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location

    def get_storage_location(self):
        return self.bucket_name

    def upload_file(self, file_bytes, file_name):
        try:
            directory = f'uploads/{file_name}'
            self.client.put_object(Bucket = self.bucket_name,
                                Body = file_bytes,
                                Key = directory,
                                ContentType='audio/mp3',
                                ACL = 'public-read')

            return {'filename': file_name}
        except ClientError as e:
            return {'error': str(e)}