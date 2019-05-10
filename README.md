# Django Magic Cards

![License](https://badgen.net/github/license/dcollinsn/django-magic-cards)
![Last Commit](https://badgen.net/github/last-commit/dcollinsn/django-magic-cards)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=dcollinsn/django-magic-cards)](https://dependabot.com)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/dcollinsn/django-magic-cards.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/dcollinsn/django-magic-cards/alerts/)
[![Patreon](https://badgen.net/badge//Support%20me%20on%20Patreon/cyan?icon=patreon)](https://patreon.com/dcollins_judge)
[![Buy me a Coffee?](https://badgen.net/badge/Ko-fi/Buy%20me%20a%20Coffee/cyan)](https://ko-fi.com/dcollins/)

Django Magic Cards is a pluggable Django app for the Oracle text of all Magic: the Gathering cards.

## Documentation

The full documentation is at https://django-magic-cards.readthedocs.io. However, it may be outdated, as I don't have comaint.

## Quickstart

Install the package::

    pip install -e git+git://github.com/dcollinsn/django-magic-cards.git@master#egg=django_magic-cards

Add the app to your `INSTALLED_APPS`:

```python
    INSTALLED_APPS = (
        ...
        'magic_cards.apps.MagicCardsConfig',
        ...
    )
```

Add Django Magic Cards' tables to your the database::

    ./manage.py migrate magic_cards

Populate the card database::

    ./manage.py import_magic_cards

## Acknowledgments

* MTGJSON for providing up-to-date card data.
* Cookiecutter and `cookiecutter-djangopackage` for providing the structure for this project.

## Disclaimer

The literal and graphical information presented in this software about Magic: the Gathering, including Oracle text and card images, is copyright Wizards of the Coast, LLC, a subsidiary of Hasbro, Inc. This project is not produced by, endorsed by, supported by, or affiliated with Wizards of the Coast.
