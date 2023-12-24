import io
import itertools
import json
import zipfile
from contextlib import closing

import requests
from django.db import transaction

from magic_cards.models import (
    Card,
    SetType,
    Set,
    FrameEffect,
    PromoType,
    Printing,
    Artist,
)

SCRYFALL_BULK_DATA = "https://api.scryfall.com/bulk-data"


class Everything:
    """
    Sentinel value for downloading all sets (i.e. skipping nothing).
    """
    pass


def fetch_data():
    r = requests.get(SCRYFALL_BULK_DATA)
    r.raise_for_status()
    files_data = r.json()
    default_cards_data = [x for x in files_data["data"] if x["type"] == "default_cards"]
    if len(default_cards_data) != 1:
        raise Exception("Too many or not enough URIs for Default Cards JSON")

    default_cards_url = default_cards_data[0]["download_uri"]
    r = requests.get(default_cards_url)
    r.raise_for_status()
    cards = r.json()
    return cards


def parse_rarity(string):
    if string == 'mythic':
        return Printing.Rarity.MYTHIC
    elif string == 'rare':
        return Printing.Rarity.RARE
    elif string == 'uncommon':
        return Printing.Rarity.UNCOMMON
    elif string == 'common':
        return Printing.Rarity.COMMON
    elif string == 'basic land':
        return Printing.Rarity.BASIC_LAND
    else:
        return Printing.Rarity.SPECIAL


class ModelCache(dict):
    def get_or_create(self, model, field, value, **kwargs):
        """
        Retrieves object of class `model` with lookup key `value` from the cache. If not found,
        creates the object based on `field=value` and any other `kwargs`.

        Returns a tuple of `(object, created)`, where `created` is a boolean specifying whether an
        `object` was created.
        """
        result = self[model].get(value.lower())
        created = False
        if not result:
            kwargs[field] = value
            result = model.objects.create(**kwargs)
            self[model][value.lower()] = result
            created = True
        return result, created

def get_from_face_or_card(face, card, field, default=None):
    return face.get(field, card.get(field, default))

def parse_data(cards_data, set_codes):
    CACHED_MODELS = [
        FrameEffect,
        PromoType,
        SetType,
    ]
    # Load supertypes, types, and subtypes into memory
    cache = ModelCache()
    for model in CACHED_MODELS:
        cache[model] = {obj.name.lower(): obj for obj in model.objects.all()}
    # Load relevant sets into memory
    if set_codes is Everything:
        cache[Set] = {obj.code.lower(): obj for obj in Set.objects.all()}
    else:
        cache[Set] = {obj.code.lower(): obj for obj in Set.objects.filter(code__in=set_codes)}

    printings_to_create = []

    for card in cards_data:
        faces = card.get("card_faces", [{}])
        for face in faces:

            # Skip sets that have not been chosen
            if set_codes is not Everything and card['set'] not in set_codes:
                continue

            # Create the set
            set_kwargs = {
                'name': card['set_name'],
                'code': card['set'],
            }
            if 'set_type' in card:
                set_type, st_created = cache.get_or_create(
                    SetType,
                    'name',
                    card['set_type'],
                )
                set_kwargs['set_type'] = set_type
            magic_set, set_created = cache.get_or_create(
                Set,
                'scryfall_id',
                card['set_id'],
                **set_kwargs,
            )

            # Skip tokens
            layout = card['layout']
            if layout == 'token':
                continue

            # Card info
            name = get_from_face_or_card(face, card, 'name')
            mana_cost = get_from_face_or_card(face, card, 'mana_cost', '')
            type_line = get_from_face_or_card(face, card, 'type_line', '')
            text = get_from_face_or_card(face, card, 'oracle_text', '')
            power = get_from_face_or_card(face, card, 'power', '')
            toughness = get_from_face_or_card(face, card, 'toughness', '')
            loyalty = get_from_face_or_card(face, card, 'loyalty', None)

            card_obj, created = Card.objects.update_or_create(
                name=name, defaults={
                    'mana_cost': mana_cost,
                    'type_line': type_line,
                    'text': text,
                    'power': power,
                    'toughness': toughness,
                    'loyalty': loyalty,
                    'layout': layout,
                    'scryfall_id': card.get('oracle_id', ''),
                })
            type_line = get_from_face_or_card(face, card, 'type_line', '')

            # Printing info
            artist_name = get_from_face_or_card(face, card, 'artist') # Missing on certain cards
            if artist_name:
                artist, _ = Artist.objects.get_or_create(full_name=artist_name)
            else:
                artist = None
            multiverse_ids = card.get('multiverse_ids', None)  # Missing on certain sets
            if multiverse_ids:
                multiverse_id = multiverse_ids[0]
            else:
                multiverse_id = None
            flavor_text = get_from_face_or_card(face, card, 'flavor', '')
            rarity = card.get('rarity', '')  # Absent on tokens
            number = card.get('number', '')  # Absent on old sets
            # If the Set was just created, we don't need to check if the Printing already exists,
            # and we can leverage bulk_create.
            printing_kwargs = {
                'set': magic_set,
                'rarity': parse_rarity(rarity),
                'flavor_text': flavor_text,
                'artist': artist,
                'number': number,
                'multiverse_id': multiverse_id,
            }
            image_data = get_from_face_or_card(face, card, 'image_uris', {})
            if 'normal' in image_data:
                printing_kwargs['scryfall_image_url'] = image_data['normal']

            printing, printing_created = Printing.objects.update_or_create(
                scryfall_id=card['id'],
                card=card_obj,
                defaults=printing_kwargs,
            )
            if 'frame_effects' in card:
                frame_effects = [
                    cache.get_or_create(FrameEffect, 'name', fe)[0]
                    for fe in card['frame_effects']
                ]
                printing.frame_effects.set(frame_effects)
            if 'promo_types' in card:
                promo_types = [
                    cache.get_or_create(PromoType, 'name', pt)[0]
                    for pt in card['promo_types']
                ]
                printing.promo_types.set(promo_types)

    if printings_to_create:
        Printing.objects.bulk_create(printings_to_create)


@transaction.atomic
def import_cards(set_codes=Everything):
    cards_data = fetch_data()
    parse_data(cards_data, set_codes)


if __name__ == "__main__":
    import_cards()
