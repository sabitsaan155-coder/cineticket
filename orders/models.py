from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum


class TicketPurchase(models.Model):
    TICKET_ADULT = 'adult'
    TICKET_STUDENT = 'student'
    TICKET_CHILD = 'child'

    TICKET_TYPE_CHOICES = [
        (TICKET_ADULT, 'Взрослый'),
        (TICKET_STUDENT, 'Студент'),
        (TICKET_CHILD, 'Детский'),
    ]

    TICKET_PRICES = {
        TICKET_ADULT: 2000,
        TICKET_STUDENT: 1500,
        TICKET_CHILD: 1000,
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_purchases')
    movie_title = models.CharField(max_length=255)
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    price_per_ticket = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def get_ticket_tariffs(cls):
        return [
            {
                'code': code,
                'label': label,
                'price': cls.TICKET_PRICES[code],
            }
            for code, label in cls.TICKET_TYPE_CHOICES
        ]

    def recalculate_from_items(self, *, save=True):
        aggregates = self.items.aggregate(
            total=Sum('line_total'),
            qty=Sum('quantity'),
        )
        self.total_price = aggregates['total'] or 0
        self.price_per_ticket = 0
        self.quantity = aggregates['qty'] or 0
        if self.quantity < 1:
            self.quantity = 1
        if save:
            self.save(update_fields=['total_price', 'price_per_ticket', 'quantity'])
        return self.total_price

    def save(self, *args, **kwargs):
        if self.pk and self.items.exists():
            aggregates = self.items.aggregate(
                total=Sum('line_total'),
                qty=Sum('quantity'),
            )
            self.total_price = aggregates['total'] or 0
            self.price_per_ticket = 0
            self.quantity = aggregates['qty'] or 1
        else:
            self.price_per_ticket = self.TICKET_PRICES.get(self.ticket_type, 0)
            self.total_price = self.price_per_ticket * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movie_title} ({self.get_ticket_type_display()}) x {self.quantity}"


class TicketPurchaseItem(models.Model):
    purchase = models.ForeignKey(
        TicketPurchase,
        on_delete=models.CASCADE,
        related_name='items',
    )
    ticket_type = models.CharField(max_length=20, choices=TicketPurchase.TICKET_TYPE_CHOICES)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    price_per_ticket = models.PositiveIntegerField()
    line_total = models.PositiveIntegerField()

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['purchase', 'ticket_type'], name='unique_ticket_type_per_purchase'),
        ]

    def save(self, *args, **kwargs):
        self.price_per_ticket = TicketPurchase.TICKET_PRICES[self.ticket_type]
        self.line_total = self.price_per_ticket * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.purchase.movie_title}: {self.get_ticket_type_display()} x {self.quantity}"
