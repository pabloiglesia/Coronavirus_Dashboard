import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_aws(local_file, bucket, s3_file, access_key, secret_key):
    s3 = boto3.client('s3', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


AWS_ACCESS_KEY_ID = 'AKIAY3VGYQU2MOJPJIMN'
AWS_SECRET_ACCESS_KEY = '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'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'images.webbuildeer.com'
AWS_S3_REGION_NAME = 'eu-west-1'
AWS_DEFAULT_ACL = None

upload_to_aws("coronavirus.csv", AWS_STORAGE_BUCKET_NAME, "coronavirus.csv", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
upload_to_aws("coronavirus-total.csv", AWS_STORAGE_BUCKET_NAME, "coronavirus-total.csv", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

