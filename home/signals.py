from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Coupon

@receiver(post_save, sender=Coupon)
def create_dynamic_link(sender, instance, created, **kwargs):
    if created:  # Only create the link if the coupon is being created, not updated
        # Generate and save the dynamic link
        instance.dynamic_link = instance.generate_dynamic_link()
        instance.save()  # Save the coupon again with the dynamic link
