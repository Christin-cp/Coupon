

from django.contrib import admin
from django.core.mail import send_mail
from .models import Client, Coupon, UserDetail

admin.site.register(Client)

# Define action to assign coupon
def assign_coupon_to_multiple_users(modeladmin, request, queryset):
    for coupon in queryset:
        if coupon.used_count < coupon.max_users:  # Ensure the coupon isn't fully redeemed
            users = UserDetail.objects.filter(coupon__isnull=True)[:coupon.max_users - coupon.used_count]

            for user in users:
                user.coupon = coupon
                user.save()

                # Send email to user
                redemption_url = f"https://127.0.0.1:8000/{user}/"
                send_mail(
                    subject="Your Coupon Code",
                    message=f"Hi {user.name},\n\nYou've received a coupon from {coupon.client.shop_name}!\n\nCoupon Code: {coupon.code}\nDiscount: {coupon.discount}%\nValid Until: {coupon.valid_until.strftime('%Y-%m-%d %H:%M') if coupon.valid_until else 'No Expiry'}\n\nRedeem your coupon here: {redemption_url}",
                    from_email="no-reply@yourdomain.com",
                    recipient_list=[user.email],
                )

                coupon.used_count += 1  # Increment used_count
                coupon.save()

assign_coupon_to_multiple_users.short_description = "Assign coupon to multiple users"

class CouponAdmin(admin.ModelAdmin):
    list_display = ('client', 'code', 'discount', 'valid_until','shareable_link', 'used_count', 'max_users')
    actions = [assign_coupon_to_multiple_users]
    @admin.display(description="Shareable Link")
    def shareable_link_display(self, obj):
        return f'<a href="{obj.shareable_link}" target="_blank">Link</a>'

    # Show only coupons related to the logged-in client
   
    def get_queryset(self, request):
        """
        Filter the coupons shown in the admin panel.
        Admin users will see all coupons.
        Clients will only see their own coupons.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:  # Admins can see all coupons
            return queryset
        else:  # Clients can only see their own coupons
            return queryset.filter(client=request.user.client)

    def has_change_permission(self, request, obj=None):
        """
        Allow clients to change only their own coupons.
        Admins can change any coupon.
        """
        if request.user.is_superuser:
            return True
        if obj is not None and obj.client == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Allow clients to delete only their own coupons.
        Admins can delete any coupon.
        """
        if request.user.is_superuser:
            return True
        if obj is not None and obj.client == request.user:
            return True
        return False
admin.site.register(Coupon, CouponAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('name','customer_id', 'whatsapp_number', 'email', 'coupon','redeemed')
    search_fields = ['name','customer_id', 'whatsapp_number', 'email',]
    
    def get_queryset(self, request):
        """
        Filter the user details shown in the admin.
        Admin can see all, clients can see only their own.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(user=request.user)  # Only show the logged-in user's details

    def has_change_permission(self, request, obj=None):
        """
        Clients can only change their own user details.
        """
        if request.user.is_superuser:
            return True
        if obj is not None and obj.user == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Clients can only delete their own user details.
        """
        if request.user.is_superuser:
            return True
        if obj is not None and obj.user == request.user:
            return True
        return False

admin.site.register(UserDetail, UserAdmin)
