import boto3
from botocore.exceptions import NoCredentialsError

class S3Client:
    def __init__(self):
        ACCESS_KEY = '07dddace-e138-487f-8fcc-d6086f10c791'
        SECRET_KEY = 'ede31f964320795c073ca11cb01ebc95655e9087fd629808233b8cf1923148aa'
        self.s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY, endpoint_url='https://s3.ir-thr-at1.arvanstorage.com')

    def upload_to_aws(self,local_file, bucket, s3_file):
        try:
            self.s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def download_from_aws(self,local_file, bucket, s3_file):
        with open(local_file, 'wb') as f:
            self.s3.download_fileobj(bucket, s3_file, f)
