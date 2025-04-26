from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem, Order, OrderItem, Address, Payment
from .forms import AddressForm, SignupForm, EditProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DirectMessageForm


# Paypal Payment 

from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse

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
    total = sum(item.total_price() for item in cart_items)
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_address_id = request.POST.get('address_id')
        if not selected_address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('checkout')

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total,
            'item_name': 'Order',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'USD',
            'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
            'return_url': request.build_absolute_uri(reverse('payment_success', args=[selected_address_id])),
            'cancel_return': request.build_absolute_uri(reverse('payment_failed')),
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'store/checkout.html', {'paypal': form, 'total': total, 'addresses': addresses})

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total, 'addresses': addresses})


@login_required
def payment_success(request, selected_address_id):
    # Cart items ko get karna
    cart_items = CartItem.objects.filter(user=request.user)

    # Agar cart mein items hain to order banayein
    if cart_items.exists():
        # Step 1: Naya Order create karna
        order = Order.objects.create(user=request.user)

        # Step 2: Cart items ko OrderItem mein convert karna
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Step 3: Cart ko empty kar dena
        cart_items.delete()

        # Order confirmation ka message
        messages.success(request, "Payment successful and your order is placed!")
    else:
        # Agar cart empty ho, to error message dena
        messages.error(request, "No items found in cart.")

    # Selected address ko pass karte hue success page dikhana
    return render(request, 'store/payment_success.html', {'address_id': selected_address_id})



@login_required
def payment_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return render(request, 'store/payment_failed.html')

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

def services_view(request):
    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            subject = f"New Message from {message.name}"
            body = f"""
You have received a new message from your Nexus:

Name: {message.name}
Email: {message.email}
Message:
{message.message}
"""
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                ['prameshgurav79286@gmail.com'],  # Admin email
                fail_silently=False,
            )

            user_subject = "Thanks for contacting Nexus"
            user_body = f"""
Hi {message.name},

Thank you for reaching out to us! We have received your message:

"{message.message}"

Our team will get back to you shortly.

Regards,
Nexus Team
"""
            send_mail(
                user_subject,
                user_body,
                settings.DEFAULT_FROM_EMAIL,
                [message.email],  # User's email
                fail_silently=False,
            )

            messages.success(request, "✅ Your message has been sent successfully!")
            return redirect('services')
    else:
        form = DirectMessageForm()

    return render(request, 'store/services.html', {'form': form})

# increase_quantity attribute

@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')  # Ensure this matches your cart page's URL name

# increase_quantity attribute

@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()  # Optional: remove item if quantity reaches 0
    return redirect('cart')  # Ensure this matches your cart page's URL name


# paypal payment functions

# def payment_success(request, selected_address_id):
#     return render(request, 'store/payment_success.html', {'address_id': selected_address_id})


# def payment_failed(request):
#     return render(request, 'store/payment_failed.html')

def payment(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        print(selected_address_id)

        cart_items = CartItem.objects.filter(user=request.user)
        total = 0
        for item in cart_items:
            item_total_price = item.product.price * item.quantity
            total += item_total_price
        final_price = total

        address = Address.objects.filter(user=request.user)

        # PayPal Code
        host = request.get_host()
        paypal_checkout = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': final_price,
            'item_name': 'Veggy',
            'invoice': uuid.uuid4(),
            'currency_code': 'USD',
            'notify_url': f"http://{host}{reverse('paypal-ipn')}",
            'return_url': f"http://{host}{reverse('payment_success', args=[selected_address_id])}",
            'cancel_url': f"http://{host}{reverse('payment_failed')}",
        }
        paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

        context = {
            'paypal_payment': paypal_payment,
            'final_price': final_price,
            'cart_items': cart_items,
            'address': address,
        }
        return render(request, 'store/payment.html', context)

    else:
        return redirect('checkout')


    return render(request, 'store/payment.html')

@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/manage_addresses.html', {'addresses': addresses})

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    total = product.price

    # PayPal payment setup
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total,
        'item_name': product.title,
        'invoice': str(uuid.uuid4()),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment_success', args=[1])}",  # Replace '1' with the address ID if needed
        'cancel_return': f"http://{host}{reverse('payment_failed')}",
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'store/buy_now.html', {'paypal': form, 'product': product})


