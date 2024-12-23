import csv
from django.core.management.base import BaseCommand
from .models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from CSV file'

    def handle(self, *args, **kwargs):
        with open('path/to/your/ingredients.csv', newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    continue
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Ingredient "{name}" added.'))
