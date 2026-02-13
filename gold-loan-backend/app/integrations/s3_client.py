class S3Client:
    def presigned_upload_url(self, image_id: str) -> str:
        return f'https://s3-presigned/{image_id}'
