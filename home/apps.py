from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
  


from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'your_app'

      # Import the signals module to ensure they are connected
