from django.apps import AppConfig

class TrainingprogramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trainingprogram'
    
    def ready(self):
        import trainingprogram.signals  # Đảm bảo signals được load khi app khởi động
