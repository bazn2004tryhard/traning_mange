from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, User

@receiver(post_save, sender=User)
def create_or_update_student(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance, Fullname = instance.username)
    else:
        instance.student.save()
