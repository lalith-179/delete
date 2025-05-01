from multiprocessing import context
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.http import HttpResponse, JsonResponse
from django.forms import formset_factory,modelformset_factory
from staff.models import *
from datetime import datetime, date,time,timezone
from django.views.generic.list import ListView
from accounts.views import is_user, user_login_required
from django.contrib.auth.decorators import (user_passes_test)
from .models import *

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

import razorpay
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import requests
from django.views.decorators.http import require_http_methods
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = None

def get_razorpay_client():
    global client
    if client is None:
        try:
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                raise ValueError("Razorpay credentials not found in settings")
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            logger.info("Razorpay client initialized successfully with key_id: %s", settings.RAZORPAY_KEY_ID)
        except Exception as e:
            logger.error(f"Failed to initialize Razorpay client: {str(e)}")
            raise
    return client

def home(request):
    movies = film.objects.filter().values_list('id','movie_name','url', named=True)
    banners = banner.objects.filter().select_related().values_list('movie__id','movie__movie_name','url', named=True)
    return render(request,"index.html", context={'films': movies,'banners':banners})

def movie_detail(request,id):
    context = {}
    context['film'] = film.objects.get(id = id) 
    context ['showtimes'] = show.objects.filter(movie=id,end_date__gte=date.today()).all().values_list('id','showtime',named=True)
    return render(request,"movie_detail.html",context)

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def show_select(request):
    if(request.method == "GET" and len(request.GET)!=0):
        
        date = request.GET['date']
        films = ""
        # add showitme >= current time + 5 min
        shows = show.objects.filter(end_date__gte=date, start_date__lte=date).select_related('movie_id','movie__url','movie__movie_name').order_by('movie_id','showtime').values_list('id','price','showtime','movie','movie__url','movie__movie_name',named=True)
        res_dict = {}
        
        # Grouping shows rows by movie and appending showitmes in a list
        for s in shows:
            # legend of fields: showid 0, price 1, showtime 2, movieid 3, movieurl 4, moviename 5,
            if(s[5] not in res_dict.keys()): 
                #movie doesn't exit in dict
                res_dict[s[5]]={'url':s[4],'price':s[1], 'showtimes':{s[0]:s[2]}, 'movieid':s[3]}
            else: 
                #movie already exists
                res_dict[s[5]]['showtimes'][s[0]]=s[2]            
        
    return render(request,"show_selection.html",context = {'films':res_dict,'date':date,'shows':shows})


def bookedseats(request):
    """
    AJAX seat booking info retrival view funciton
    """
    if request.method == 'GET':
           show_id = request.GET['show_id']
           show_date = request.GET['show_date']
           seats = booking.objects.filter(show=show_id,show_date=show_date).values('seat_num')
           booked = ""
           for s in seats:
            booked+=s['seat_num']+","
           return HttpResponse(booked[:-1])
    else:
           return HttpResponse("Request method is not a GET")


def sendEmail(request,message):
    """
    Function to send Email
    """
    template ="Hello "+request.user.username+'\n'+message

    user_email = request.user.email

    email = EmailMessage(
        'Tickets Confirmation Email',
        template,
        settings.EMAIL_HOST_USER,
        [user_email],
    )

    email.fail_silently = False
    email.send()
    return True


def checkout(request):
    context = {}
    if request.method == "POST":
        try:
            # Log the incoming request data
            logger.info(f"Checkout request data: {request.POST}")
            
            show_date = request.POST['showdate']
            seats = request.POST['seats']
            show_id = request.POST['showid']
            
            # Get Show info
            showinfo = show.objects.get(id=show_id)
            num_seats = len(seats.split(","))
            total = showinfo.price * num_seats
            
            # Store booking details in session for payment
            request.session['show_id'] = show_id
            request.session['show_date'] = show_date
            request.session['seats'] = seats
            request.session['total'] = total
            
            # Force session save
            request.session.modified = True
            
            # Prepare context for template
            context = {
                'show': showinfo,
                'sdate': show_date,
                'seats': seats,
                'num_seats': num_seats,
                'total': total,
                'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID
            }
            
            logger.info(f"Session data stored: show_id={show_id}, show_date={show_date}, seats={seats}, total={total}")
            
            return render(request, "checkout.html", context)
                
        except KeyError as e:
            logger.error(f"Missing required parameter: {str(e)}")
            return HttpResponse(f"Checkout failed: Missing required information. Please try again.")
        except Exception as e:
            logger.error(f"Checkout process failed: {str(e)}")
            return HttpResponse(f"Checkout process failed: {str(e)}")
    
    return render(request, "checkout.html", context)

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def userbookings(request):
    msg=""
    if(request.method == "GET" and len(request.GET)!=0):
        msg = request.GET['ack']

    booking_table = booking.objects.filter(user=request.user).select_related().order_by('-booked_date').values_list('id','show_date','booked_date','show__movie__movie_name','show__movie__url','show__showtime','total','seat_num',named=True)
    
    context = {
        'data':booking_table,
        'msg':msg
    }
    return render(request,"bookings.html",context)

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def cancelbooking(request,id):
    bobj =  booking.objects.get(id=id)
    message="\nYour tickets are succcessfully Cancelled. Here are the details.\nYour show info{}\nYour Show date {}\nYour seats\n\nThank you,\nBookMyTicket".format(bobj.show,bobj.show_date,bobj.seat_num)
    ack = "Your tickets {} for {} are cancelled successfully".format(bobj.seat_num,bobj.show)
    bobj.delete()
    sendEmail(request,message)
    
    return HttpResponseRedirect("/mybookings?ack="+ack)

@require_http_methods(["POST"])
@csrf_exempt
def create_order(request):
    try:
        # Parse request data
        data = json.loads(request.body)
        amount = data.get('amount')
        currency = data.get('currency', 'INR')
        receipt = data.get('receipt')
        
        if not all([amount, currency, receipt]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Get Razorpay client
        razorpay_client = get_razorpay_client()
        
        # Create order
        order = razorpay_client.order.create({
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'payment_capture': '1'
        })
        
        logger.info(f"Order created successfully: {order['id']}")
        
        return JsonResponse({
            'id': order['id'],
            'amount': order['amount'],
            'currency': order['currency']
        })
        
    except razorpay.errors.BadRequestError as e:
        logger.error(f"Razorpay BadRequestError: {str(e)}")
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)
    except razorpay.errors.ServerError as e:
        logger.error(f"Razorpay ServerError: {str(e)}")
        return JsonResponse({'error': 'Razorpay server error'}, status=500)
    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def generate_booking_qr(booking):
    """
    Generate QR code for booking details
    """
    # Create booking details string
    booking_details = f"""
    Movie: {booking.show.movie.movie_name}
    Date: {booking.show_date}
    Time: {booking.show.showtime}
    Seats: {booking.seat_num}
    Booking ID: {booking.booking_code}
    """
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(booking_details)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

@csrf_exempt
def payment_success(request):
    """
    Handles Razorpay payment success callback
    Flow:
    1. Payment Completion - Receives payment details from Razorpay
    2. Payment Verification - Verifies payment signature
    3. Booking Creation - Creates booking if verification succeeds
    4. Session Cleanup - Clears temporary session data
    5. Success Page Display - Shows booking confirmation
    """
    if request.method != 'POST':
        logger.warning("Invalid request method for payment success")
        return redirect('mainpage')
    
    try:
        # 1. Payment Completion - Get payment details
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Log payment details (excluding sensitive data)
        logger.info(f"Payment received - Order ID: {order_id}")
        
        # Validate required payment parameters
        if not all([payment_id, order_id, signature]):
            logger.error("Missing payment parameters")
            return HttpResponse("Payment verification failed: Missing payment parameters")
        
        # 2. Payment Verification
        try:
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            razorpay_client = get_razorpay_client()
            razorpay_client.utility.verify_payment_signature(params_dict)
            logger.info(f"Payment signature verified for order {order_id}")
        except Exception as e:
            logger.error(f"Payment signature verification failed: {str(e)}")
            return HttpResponse("Payment verification failed: Invalid payment signature")
        
        # 3. Booking Creation
        try:
            # Get booking details from session
            show_id = request.session.get('show_id')
            seats = request.session.get('seats')
            total = request.session.get('total')
            show_date = request.session.get('show_date')
            
            # Validate session data
            if not all([show_id, seats, total, show_date]):
                missing_data = []
                if not show_id: missing_data.append('show_id')
                if not seats: missing_data.append('seats')
                if not total: missing_data.append('total')
                if not show_date: missing_data.append('show_date')
                logger.error(f"Missing session data: {', '.join(missing_data)}")
                return HttpResponse(f"Booking failed: Missing session data ({', '.join(missing_data)})")
            
            # Get show information
            showinfo = show.objects.get(id=show_id)
            num_seats = len(seats.split(","))
            
            # Convert show_date string to date object if needed
            if isinstance(show_date, str):
                show_date = datetime.strptime(show_date, '%Y-%m-%d').date()
            
            # Create booking record
            new_booking = booking.objects.create(
                booking_code=order_id,
                user=request.user,
                show=showinfo,
                show_date=show_date,
                booked_date=datetime.now(timezone.utc),
                seat_num=seats,
                num_seats=num_seats,
                total=total
            )
            logger.info(f"Booking created successfully: {new_booking.id}")
            
            # 4. Session Cleanup
            for key in ['order_id', 'show_id', 'seats', 'total', 'show_date']:
                if key in request.session:
                    del request.session[key]
            
            # 5. Success Page Display
            context = {
                'booking': new_booking,
                'payment_id': payment_id
            }
            
            # Send confirmation email
            try:
                message = f"""
                Your tickets are successfully booked. Here are the details.
                Movie: {showinfo.movie.movie_name}
                Show Date: {show_date}
                Show Time: {showinfo.showtime.strftime('%I:%M %p')}
                Seat Numbers: {seats}
                Number of Seats: {num_seats}
                Total Amount: ₹{total}
                Booking ID: {order_id}
                
                Thank you,
                BookMyTicket
                """
                sendEmail(request, message)
                logger.info("Confirmation email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {str(e)}")
                # Continue even if email fails
            
            return render(request, 'booking/success.html', context)
            
        except Exception as e:
            logger.error(f"Booking creation failed: {str(e)}")
            return HttpResponse(f"Booking failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Payment success process failed: {str(e)}")
        return HttpResponse(f"Payment process failed: {str(e)}")

def ticket_details(request, booking_code):
    """
    View to display ticket details when QR code is scanned
    """
    try:
        booking_obj = booking.objects.get(booking_code=booking_code)
        context = {
            'booking': booking_obj,
            'is_ticket_view': True  # Flag to indicate this is a ticket view
        }
        return render(request, 'booking/ticket_details.html', context)
    except booking.DoesNotExist:
        return HttpResponse("Invalid ticket code", status=404)

def generate_ticket_pdf(request, booking_code):
    try:
        booking_obj = booking.objects.get(booking_code=booking_code)
        
        # Create a BytesIO buffer for the PDF
        buffer = BytesIO()
        
        # Create the PDF object with custom page size and margins
        page_width = 8.5 * inch
        page_height = 11 * inch
        margin = 0.5 * inch
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(page_width, page_height),
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin
        )
        
        # Container for the PDF elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#1a237e')  # Dark blue color
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#303f9f')  # Slightly lighter blue
        )
        
        # Add decorative border
        border_style = [
            ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#1a237e')),  # Outer border
            ('BOX', (0, 0), (-1, -1), 3, colors.HexColor('#1a237e')),   # Inner border
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')), # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')), # Content background
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')), # Content text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#9fa8da'))  # Cell borders
        ]
        
        # Add title with movie name
        elements.append(Paragraph("Movie Ticket", title_style))
        elements.append(Paragraph(booking_obj.show.movie.movie_name, subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
            box_size=10,
            border=4,
        )
        ticket_url = f"{request.scheme}://{request.get_host()}/ticket/{booking_code}/"
        qr.add_data(ticket_url)
        qr.make(fit=True)
        
        # Create QR code image with custom colors
        qr_img = qr.make_image(fill_color="#1a237e", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Add QR code to PDF with custom size and alignment
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        qr_image.hAlign = 'CENTER'
        elements.append(qr_image)
        elements.append(Spacer(1, 20))
        
        # Create ticket details with improved formatting
        ticket_data = [
            ['Ticket Information', ''],  # Header row
            ['Show Date:', booking_obj.show_date.strftime("%B %d, %Y")],
            ['Show Time:', booking_obj.show.showtime.strftime("%I:%M %p")],
            ['Seat Numbers:', booking_obj.seat_num],
            ['Number of Seats:', str(booking_obj.num_seats)],
            ['Total Amount:', f"₹{booking_obj.total}"],
            ['Booking ID:', booking_obj.booking_code],
        ]
        
        # Create table with custom styling
        table = Table(ticket_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle(border_style))
        elements.append(table)
        
        # Add footer with terms and conditions
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=1,
            spaceBefore=30
        )
        footer_text = """
        This ticket is valid only for the show date and time mentioned above.
        Please arrive at least 15 minutes before the show time.
        No refunds or exchanges are allowed.
        """
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="movie-ticket-{booking_code}.pdf"'
        response.write(pdf)
        
        return response
        
    except booking.DoesNotExist:
        return HttpResponse("Invalid ticket code", status=404)
    except Exception as e:
        logger.error(f"Error generating PDF ticket: {str(e)}")
        return HttpResponse("Error generating ticket", status=500)

