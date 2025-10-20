from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        bucket_name = 'images'
        
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        client.put_object(bucket_name, image_name, file_object, file_object.size)
        
        return f"http://localhost:9000/{bucket_name}/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(drug, pic):
    endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
    client = Minio(
        endpoint=endpoint,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    
    img_obj_name = pic.name
    
    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})
    
    result = process_file_upload(pic, client, img_obj_name)
    
    if isinstance(result, dict) and 'error' in result:
        return Response(result)
    
    drug.image_url = result
    drug.save()
    
    return Response({"message": "success"})


def delete_pic(drug):
    if not drug.image_url:
        return
    
    try:
        endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
        client = Minio(
            endpoint=endpoint,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
        )
        
        img_obj_name = drug.image_url.split('/')[-1]
        client.remove_object('images', img_obj_name)
    except Exception as e:
        print(f"Error deleting image: {e}")
