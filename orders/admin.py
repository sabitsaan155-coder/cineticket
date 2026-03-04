from django.contrib import admin

from .models import TicketPurchase, TicketPurchaseItem


class TicketPurchaseItemInline(admin.TabularInline):
    model = TicketPurchaseItem
    extra = 0


@admin.register(TicketPurchase)
class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('movie_title', 'user', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('movie_title', 'user__username')
    inlines = (TicketPurchaseItemInline,)


@admin.register(TicketPurchaseItem)
class TicketPurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'ticket_type', 'quantity', 'price_per_ticket', 'line_total')
    list_filter = ('ticket_type',)
    search_fields = ('purchase__movie_title', 'purchase__user__username')
