from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    """Загружает файл в MinIO и возвращает URL"""
    try:
        bucket_name = 'images'
        
        # Создаем bucket если его нет
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        client.put_object(bucket_name, image_name, file_object, file_object.size)
        
        # Используем localhost для доступа из браузера
        return f"http://localhost:9000/{bucket_name}/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(drug, pic):
    """Добавляет изображение для препарата в MinIO"""
    # Убираем протокол из URL для MinIO client
    endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
    client = Minio(
        endpoint=endpoint,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    
    # Используем оригинальное название файла
    img_obj_name = pic.name
    
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
        # Убираем протокол из URL для MinIO client
        endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
        client = Minio(
            endpoint=endpoint,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
        )
        
        # Извлекаем имя файла из URL
        img_obj_name = drug.image_url.split('/')[-1]
        client.remove_object('images', img_obj_name)
    except Exception as e:
        print(f"Error deleting image: {e}")
