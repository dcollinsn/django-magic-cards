from django.contrib import admin

from .models import (
    Card,
    Set,
    Printing,
    Artist,
    SetType,
    FrameEffect,
    PromoType,
)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Printing)
class PrintingAdmin(admin.ModelAdmin):
    search_fields = ['card__name']
    list_filter = ['promo_types', 'frame_effects', 'set']
    raw_id_fields = ['card']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['full_name']


@admin.register(SetType)
class SetTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(FrameEffect)
class FrameEffectAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(PromoType)
class PromoTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
