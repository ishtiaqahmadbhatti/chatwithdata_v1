import boto3
from botocore.config import Config
from app.app_core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.s3_region,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.s3_bucket

    def generate_presigned_upload_url(self, file_name: str, content_type: str = None):
        """Generate a presigned URL to upload a file directly to S3."""
        if not self.bucket_name:
            logger.error("S3_BUCKET not configured")
            return None

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': f"uploads/{file_name}"
            }
            if content_type:
                params['ContentType'] = content_type

            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=settings.s3_presigned_expiry
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    def get_file_from_s3(self, file_key: str, local_path: str):
        """Download a file from S3 to a local path."""
        try:
            self.s3_client.download_file(self.bucket_name, file_key, local_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading from S3: {e}")
            return False

    def upload_file_to_s3(self, local_path: str, file_name: str, folder: str = "outputs"):
        """Upload a local file to S3."""
        if not self.bucket_name:
            return False
        
        file_key = f"{folder}/{file_name}"
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, file_key)
            return file_key
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            return None

    def generate_presigned_download_url(self, file_key: str, expiration: int = 3600):
        """Generate a presigned URL to download a file from S3."""
        if not self.bucket_name:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Error generating download presigned URL: {e}")
            return None

    def delete_file(self, file_key: str):
        """Delete a single file from S3."""
        if not self.bucket_name or not file_key:
            return False
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Deleted from S3: {file_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from S3: {e}")
            return False

    def delete_files(self, file_keys: list):
        """Delete multiple files from S3."""
        if not self.bucket_name or not file_keys:
            return False
            
        try:
            # S3 delete_objects can handle up to 1000 keys
            objects = [{'Key': k} for k in file_keys if k]
            if not objects:
                return True
                
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects, 'Quiet': True}
            )
            logger.info(f"Deleted {len(objects)} files from S3")
            return True
        except Exception as e:
            logger.error(f"Error deleting multiple from S3: {e}")
            return False

    def list_objects_older_than(self, prefix: str, cutoff_time):
        """List objects in a folder older than a specific timestamp."""
        if not self.bucket_name:
            return []
            
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            old_keys = []
            
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['LastModified'] < cutoff_time:
                            old_keys.append(obj['Key'])
            
            return old_keys
        except Exception as e:
            logger.error(f"Error listing old objects in S3: {e}")
            return []

s3_service = S3Service()
