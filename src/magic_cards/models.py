from __future__ import unicode_literals

import random

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django_light_enums import enum


@python_2_unicode_compatible
class NameMixin(object):
    def __str__(self):
        return self.name


class Card(NameMixin, models.Model):
    scryfall_id = models.CharField(max_length=63, null=True, blank=True)

    name = models.CharField(max_length=255, unique=True)
    mana_cost = models.CharField(max_length=63, blank=True)

    text = models.TextField(blank=True)
    power = models.CharField(max_length=7, blank=True)
    toughness = models.CharField(max_length=7, blank=True)
    loyalty = models.CharField(max_length=8, null=True, blank=True)

    type_line = models.CharField(max_length=255, null=True, blank=True)
    layout = models.CharField(max_length=255, null=True, blank=True)


class SetType(NameMixin, models.Model):
    name = models.CharField(max_length=63)


class Set(NameMixin, models.Model):
    scryfall_id = models.CharField(max_length=63, null=True, blank=True)

    name = models.CharField(max_length=63)
    code = models.CharField(max_length=8, unique=True)

    set_type = models.ForeignKey(
        SetType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    release_date = models.DateField(null=True, blank=True)
    digital = models.BooleanField(default=False)
    foil_only = models.BooleanField(default=False)
    nonfoil_only = models.BooleanField(default=False)
    icon_uri = models.CharField(max_length=255, null=True, blank=True)


class FrameEffect(NameMixin, models.Model):
    name = models.CharField(max_length=63)


class PromoType(NameMixin, models.Model):
    name = models.CharField(max_length=63)


class PrintingQuerySet(models.QuerySet):
    def random(self, num):
        num = int(num)
        printing_ids = set(self.values_list('id', flat=True))
        random_ids = random.sample(printing_ids, num)
        return self.filter(id__in=random_ids)


@python_2_unicode_compatible
class Printing(models.Model):
    class Rarity(enum.Enum):
        MYTHIC = 10
        RARE = 20
        UNCOMMON = 30
        COMMON = 40
        SPECIAL = 50
        BASIC_LAND = 60

    objects = PrintingQuerySet.as_manager()

    scryfall_id = models.CharField(max_length=63, null=True, blank=True)

    card = models.ForeignKey('Card',
                             on_delete=models.CASCADE,
                             related_name='printings')
    set = models.ForeignKey('Set',
                            on_delete=models.CASCADE,
                            related_name='printings')
    rarity = enum.EnumField(Rarity)
    flavor_text = models.TextField(blank=True)
    artist = models.ForeignKey('Artist',
                               on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='printings')
    number = models.CharField(max_length=64, blank=True)
    multiverse_id = models.PositiveIntegerField(blank=True, null=True)
    scryfall_image_url = models.CharField(max_length=1024, blank=True, null=True)

    frame_effects = models.ManyToManyField(FrameEffect)
    promo_types = models.ManyToManyField(PromoType)

    @property
    def gatherer_image_url(self):
        if self.multiverse_id:
            return 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card'.format(
                self.multiverse_id)

    @property
    def image_url(self):
        if self.scryfall_image_url:
            return self.scryfall_image_url
        if self.gatherer_image_url:
            return self.gatherer_image_url


    def __str__(self):
        return '{} ({})'.format(self.card, self.set.code)


@python_2_unicode_compatible
class Artist(models.Model):
    full_name = models.CharField(max_length=127, unique=True)

    def __str__(self):
        return self.full_name
