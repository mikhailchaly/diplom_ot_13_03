from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal

from new_user.models import User

new_order = Signal()


@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """ отправяем письмо при изменении статуса заказа """
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        f"Обновление статуса заказа",
        'Заказ сформирован',
        settings.EMAIL_BACKEND,
        [user.email]
    )
    msg.send()