from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_app.accounts'
    
    def ready(self):
        import api_app.accounts.signals  # Import the signals
