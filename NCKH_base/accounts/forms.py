from django.contrib.auth.forms import UserCreationForm
from trainingprogram.models import User  # Lấy model user từ app training_program

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)  # Điều chỉnh theo các trường của custom user model
