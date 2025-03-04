from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.conf import settings
import os
from django.core.files import File

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

        # Set default profile picture if it exists
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
        if os.path.exists(default_image_path):
            try:
                with open(default_image_path, 'rb') as f:
                    profile.profile_picture.save(os.path.basename(default_image_path), File(f), save=False)
            except Exception as e:
                print(f"Error setting default profile picture: {e}")

        profile.save()

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """ Save profile after user instance is saved. """
    instance.profile.save()  # Save existing profile, no need to create again