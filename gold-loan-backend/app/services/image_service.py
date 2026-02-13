import uuid

class ImageService:
    def upload_url(self):
        image_id = str(uuid.uuid4())
        return {'image_id': image_id, 'upload_url': f'https://s3-presigned/{image_id}'}
