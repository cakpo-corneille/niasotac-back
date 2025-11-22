"""
Utilitaires pour les tests de showcase
"""
import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def generate_image_file(filename='test.jpg', size=(100, 100), format='JPEG'):
    """Génère un fichier image temporaire pour les tests."""
    image = Image.new('RGB', size)
    tmp_file = tempfile.NamedTemporaryFile(suffix=f'.{format.lower()}', delete=False)
    image.save(tmp_file, format=format)
    tmp_file.seek(0)
    return SimpleUploadedFile(
        filename,
        tmp_file.read(),
        content_type=f'image/{format.lower()}'
    )
