from django.shortcuts import render, redirect, get_object_or_404
from .models import Coupon, UserDetail,Client
from .forms import UserForm
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import F, Count
from django.http import HttpResponse
import uuid

from django.template.loader import render_to_string

from django.template.loader import get_template
from weasyprint import HTML
from reportlab.pdfgen import canvas




from io import BytesIO
from .models import Coupon, Client










def apply_coupon(request, coupon_code):
    # Get the coupon object using the provided code
    coupon = get_object_or_404(Coupon, code=coupon_code)
    
    # Get the client object associated with this coupon
    client = coupon.client  # This ensures you get the client linked to the coupon

    # Check if coupon can still be redeemed
    if not coupon.is_available_for_redeem():
        return render(request, 'coupon_expired.html')  # Show coupon expired page if limit exceeded

    if request.method == "POST":
        # Process the form data
        form = UserForm(request.POST)

        if form.is_valid():
            # Save the user details
            user_detail = form.save(commit=False)
            user_detail.user = request.user  # Link to the current logged-in user
            user_detail.coupon = coupon  # Link the coupon to this user
            user_detail.save()

            # Increment the used_count of the coupon
            coupon.used_count += 1
            coupon.save()

            return render(request, 'coupon.html', {'coupon': coupon, 'user_detail': user_detail})  # Coupon successfully redeemed page
    else:
        # Display an empty form if it's a GET request
        form = UserForm()

    # Pass the client object and coupon code to the template for background image
    return render(request, 'apply_coupon.html', {'form': form, 'coupon': coupon, 'client': client, 'coupon_code': coupon_code})

def forms(request):
    # Get the coupon object using the provided code
    
    client = None
    coupon = None
    message = ""
    customer_id = ""
    header_image =  ("/media/client_headers/{{client.header_image}}") 
    try:
        # Get client associated with the user
        client = Client.objects.get(user=request.user)
        header_image =Client.objects.all()

        
       
        
        # Fetch all coupons related to the client
        coupons = Coupon.objects.filter(client=client)
        coupon_id = request.GET.get('coupon_id')  # Example of retrieving the coupon_id from request
        coupon = Coupon.objects.filter(id=coupon_id).first() 
        
        if coupons.exists():  # Check if any coupon exists
            coupon = coupons.first()  # Select the first coupon

            if coupon.is_available_for_redeem():
                message = "Coupon is available for redeem."
            else:
                message = "Coupon is not available for redeem."
        else:
            message = "No coupon found for this client."

       

    except Client.DoesNotExist:
        message = "Client does not exist."
    
    except Exception as e:
        message = f"An error occurred: {str(e)}"

    

    context = {
        'customer_id':customer_id,
        'client': client,
        'coupon': coupon,
        'message': message,
    }
    

    # Check if coupon can still be redeemed
    if not coupon.is_available_for_redeem():
        return render(request, 'coupon_expired.html')  # Show coupon expired page if limit exceeded

    if request.method == "POST":
        # Process the form data
        form = UserForm(request.POST )

        if form.is_valid():
            # Save the user details
            user_detail = form.save(commit=False)
            user_detail.user = request.user  # Link to the current logged-in user
            user_detail.coupon = coupon  # Link the coupon to this user
            user_detail.save()

            # Increment the used_count of the coupon
            coupon.used_count += 1
            coupon.save()

            return render(request, 'coupon.html', {'coupon': coupon,'user_detail': user_detail})  # Coupon successfully redeemed page
    else:
        # Display an empty form if it's a GET request
        form = UserForm()

    return render(request, 'apply_coupon.html', {'form': form, 'coupon': coupon,'header_image': header_image,'client': client})
    

    

def your_view(request):
    try:
        # Attempt to fetch a single coupon, handle multiple matches
        coupon = Coupon.objects.get(client=request.user)
    except Coupon.MultipleObjectsReturned:
        # If multiple are found, select the first
        coupon = Coupon.objects.filter(client=request.user).first()
    except Coupon.DoesNotExist:
        coupon = None  # If no coupon is found

    return render(request, 'your_template.html', {'coupon': coupon})


def generate_coupon_pdf(request, coupon_code):
    # Retrieve the coupon and client based on the coupon_code
    coupon = Coupon.objects.get(code=coupon_code)
    client = coupon.client  # Assuming coupon is linked to a client

    # Create a PDF response
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Set title
    pdf.setTitle(f"Coupon_{coupon.code}")

    # Header
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, 800, "Your Coupon Details")

    # Draw coupon details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Coupon Code: {coupon.code}")
    pdf.drawString(50, 740, f"Discount: {coupon.discount}%")
    pdf.drawString(50, 720, f"Expiry Date: {coupon.valid_until}")
    pdf.drawString(50, 700, f"Message: {coupon.message}")

    # Add client details
    pdf.drawString(50, 680, f"Client Name: {client.shop_name}")
    pdf.drawString(50, 660, f"Contact: {client.contact_number}")

    # Draw footer
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, 600, "Thank you for shopping with us!")
    pdf.drawString(50, 580, "Redeem this coupon in-store only.")

    # Close the PDF
    pdf.save()
    buffer.seek(0)

    # Create HTTP response for PDF
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="coupon_{coupon.code}.pdf"'

    return response