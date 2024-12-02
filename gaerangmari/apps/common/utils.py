import uuid

from django.core.files.storage import default_storage
from django.utils import timezone


def generate_unique_filename(filename):
    """고유한 파일명 생성"""
    ext = filename.split(".")[-1]
    return f"{uuid.uuid4()}.{ext}"


def upload_image(image, directory="images"):
    """이미지 업로드 유틸리티"""
    if not image:
        return None

    filename = generate_unique_filename(image.name)
    path = f"{directory}/{filename}"
    default_storage.save(path, image)
    return path


def get_client_ip(request):
    """클라이언트 IP 주소 획득"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
