import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from api.constants import MIN_YEAR


def validate_year(year):
    now = timezone.now().year
    if year > now or year <= MIN_YEAR:
        raise ValidationError(
            f'{year} не может быть больше {now} или меньше {MIN_YEAR}'
        )


def validate_slug(value):
    slug_regex = r'^[-a-zA-Z0-9_]+$'
    if not re.match(slug_regex, value):
        raise ValidationError('Слаг содержит недопустимый символ.')
