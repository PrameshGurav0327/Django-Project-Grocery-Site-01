from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order, OrderItem, Address
from .forms import AddressForm, SignupForm, EditProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from .forms import DirectMessageForm


# Home & Product Pages
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


# Cart Functions
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.title} added to cart.")
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')


# Checkout & Orders
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == 'POST' and cart_items.exists():
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart_items.delete()
        messages.success(request, "Order placed successfully.")
        return redirect('order_success')

    total = sum(item.total_price() for item in cart_items)
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})


@login_required
def order_success(request):
    return render(request, 'store/order_success.html')


@login_required
def your_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/your_orders.html', {'orders': orders})


# 🏠 Address Book
@login_required
def address_book(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/address_book.html', {'addresses': addresses})


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect('address_book')
    else:
        form = AddressForm()
    return render(request, 'store/add_address.html', {'form': form})


@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('address_book')
    else:
        form = AddressForm(instance=address)
    return render(request, 'store/edit_address.html', {'form': form})


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('address_book')
    return render(request, 'store/delete_address.html', {'address': address})


# Authentication
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'store/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'store/edit_profile.html', {'form': form})

# ================= Direct Message feature ===================

from django.core.mail import send_mail
from django.conf import settings
from .forms import DirectMessageForm  # Make sure to import your form

def services_view(request):
    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            # Save the form data into the message object
            message = form.save()
            
            # 📧 Send email to admin
            subject = f"New Message from {message.name}"
            body = f"""
You have received a new message from your grocery site:

Name: {message.name}
Email: {message.email}
Message:
{message.message}
"""
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                ['prameshgurav79286.learning@gmail.com'],  # 🔁 Replace with your admin email
                fail_silently=False,
            )

            # Send confirmation email to user
            user_subject = "Thanks for contacting Grocery Site"
            user_body = f"""
Hi {message.name},

Thank you for reaching out to us! We have received your message:

"{message.message}"

Our team will get back to you shortly.

Regards,
Grocery Site Team
"""

            send_mail(
                user_subject,
                user_body,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],  # ✅ Sending email to the user's email
                fail_silently=False,
            )

            # Show success message
            messages.success(request, "✅ Your message has been sent successfully!")
            return redirect('services')
    else:
        form = DirectMessageForm()

    return render(request, 'store/services.html', {'form': form})

# ============== Paypal payment ===============

@login_required
def paypal_checkout_view(request):
    host = request.get_host()
    final_price = 0
    address = None

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': final_price,
        'item_name': 'Pet',
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('paymentsuccess')}",
        'cancel_url': f"http://{host}{reverse('paymentfailed')}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    # ================= Paypal Code End =====================

    return render(request, 'store/checkout.html', {'cart_items': [], 'total': 0, 'final_price': final_price, 'address': address, 'paypal': paypal_payment})

def payment_success(request):
    return render(request,'core/payment_success.html')


def payment_failed(request):
    return render(request,'core/payment_failed.html')
