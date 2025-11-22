import os
from celery import Celery

# Utilise DJANGO_SETTINGS_MODULE depuis l'environnement
# En production: exporter DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    os.getenv('DJANGO_SETTINGS_MODULE', 'niasotac_backend.config.prod')
)

app = Celery('niasotac_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from installed apps (e.g., `showcase.tasks`)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
