from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    """Загружает файл в MinIO и возвращает URL"""
    try:
        client.put_object('drug-logos', image_name, file_object, file_object.size)
        return f"http://{settings.AWS_S3_ENDPOINT_URL}/drug-logos/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(drug, pic):
    """Добавляет изображение для препарата в MinIO"""
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    
    # Создаем имя файла на основе ID препарата
    img_obj_name = f"{drug.id}.png"
    
    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})
    
    result = process_file_upload(pic, client, img_obj_name)
    
    if isinstance(result, dict) and 'error' in result:
        return Response(result)
    
    # Сохраняем URL изображения в модели
    drug.image_url = result
    drug.save()
    
    return Response({"message": "success"})


def delete_pic(drug):
    """Удаляет изображение препарата из MinIO"""
    if not drug.image_url:
        return
    
    try:
        client = Minio(
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
        )
        
        img_obj_name = f"{drug.id}.png"
        client.remove_object('drug-logos', img_obj_name)
    except Exception as e:
        print(f"Error deleting image: {e}")
