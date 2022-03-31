
import uuid


def get_image_path(instance, filename, **kwargs):
    name, ext = filename.rsplit('.', 1)
    file = f"{name.replace(' ', '_')}_{uuid.uuid4()}.{ext}"
    file_path = f'static/{instance.post.title}/{file}'
    return file_path
