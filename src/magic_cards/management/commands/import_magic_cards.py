from django.core.management import BaseCommand
import inflect

from magic_cards.models import (
    Card,
    SetType,
    Set,
    FrameEffect,
    PromoType,
    Printing,
    Artist,
)
from magic_cards.utils.import_cards import import_cards, Everything


class Command(BaseCommand):
    help = 'Imports data from MTGJSON into your local database.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            help="flush all tables before importing",
            action="store_true",
        )
        parser.add_argument('set_code', nargs='*', type=str)

    def handle(self, *args, **options):
        if options["flush"]:
            for klass in (
                Card,
                SetType,
                Set,
                FrameEffect,
                PromoType,
                Printing,
                Artist,
            ):
                print(f"Deleting all objects of class {klass}")
                klass.objects.all().delete()

        models_to_track = [Set, Card, Printing]
        initial = {model: model.objects.count() for model in models_to_track}

        p = inflect.engine()
        set_codes = options['set_code']
        if set_codes:
            count = len(set_codes)
            set_string = 'num({count}) plural_noun(set) ({codes})'.format(count=count, codes=', '.join(set_codes))
        else:
            set_string = 'all sets'

        self.stdout.write(p.inflect("Beginning import of {}.".format(set_string)))
        import_cards(set_codes or Everything)
        self.stdout.write("Import complete.")

        final = {model: model.objects.count() for model in models_to_track}
        status_strings = [
            p.inflect(
                "{0} new num({0},)plural_noun({1})".format(final[model] - initial[model], model._meta.object_name))
            for model in models_to_track
        ]
        self.stdout.write("Added {}.".format(p.join(status_strings)))
