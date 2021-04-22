from django.core.mail import send_mail


def send_activation_code(email, activation_code, is_password):
    activation_url = f'http://localhost:5000/api/v1/account/activate/{activation_code}'
    if not is_password:
         message = f'Thank you for registration! Please follow the link {activation_url}'
    else:
         message = activation_code
    send_mail(
        'Info Blog Activation',
        message,
        'admin@admin.com',
        [email, ],
        fail_silently=False
    )

