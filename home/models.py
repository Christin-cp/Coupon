from django.db import models
import uuid
from django.contrib.auth.models import User
from django.urls import reverse 


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    header_image = models.ImageField(upload_to='client_headers/', null=True, blank=True)  
    google_maps_link = models.URLField(max_length=500, null=True, blank=True)  
    contact_number = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.shop_name


class Coupon(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    discount = models.FloatField(help_text="Discount in percentage")
    product_image = models.ImageField(upload_to='coupon_image/', null=True, blank=True)
    submittd_by_user = models.BooleanField(default=False)
    valid_until = models.DateTimeField(null=True, blank=True)
    shareable_link = models.URLField(max_length=500, null=True, blank=True, editable=False)
    redeemed = models.BooleanField(default=False)
    message = models.CharField(max_length=500, null=False, blank=True)
    max_users = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4().hex[:10].upper())
        if not self.shareable_link:
            path = reverse('apply_coupon', args=[self.code])
            self.shareable_link = f"https://127.0.0.1:8000{path}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.discount}%"

    def is_available_for_redeem(self):
        """Check if the coupon can be redeemed by more users based on the max_users limit."""
        return self.used_count < self.max_users


class UserDetail(models.Model):
    customer_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255)
    whatsapp_number = models.CharField(max_length=15)
    email = models.EmailField()
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True)
    redeemed = models.BooleanField(default=False)

    def update_customer_ids(apps, schema_editor):
     UserDetail = apps.get_model('home', 'UserDetail')
     for user in UserDetail.objects.all():
        if not user.customer_id:
            user.customer_id = f'CUSS{str(uuid.uuid4().int)[:5]}'  # Customize as needed
            user.save()

    def __str__(self):
        return f"{self.name} - {self.customer_id}"


    def __str__(self):
        return f"{self.name} ({self.email})"


