from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Home & Product Detail
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase-quantity/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.order_success, name='order_success'),

    # Orders
    path('your-orders/', views.your_orders, name='your_orders'),

    # Address Book
    path('address-book/', views.address_book, name='address_book'),
    path('add-address/', views.add_address, name='add_address'),
    path('edit-address/<int:pk>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:pk>/', views.delete_address, name='delete_address'),

    # Payment
    path('payment/',views.payment,name='payment'),
    # store/urls.py

    path('payment-success/<int:selected_address_id>/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # Static Pages
    path('about/', TemplateView.as_view(template_name='store/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='store/contact.html'), name='contact'),
    path('services/', views.services_view, name='services'),

    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buynow'),
]