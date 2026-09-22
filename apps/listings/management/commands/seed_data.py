import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from apps.listings.models import Listing, InputTypeChoices, PropertyTypeChoices, CountryChoices

User = get_user_model()
fake = Faker('de_DE')

GERMAN_CITIES = [
    ('Berlin', 52.5200, 13.4050),
    ('Munich', 48.1351, 11.5820),
    ('Hamburg', 53.5511, 9.9937),
    ('Cologne', 50.9375, 6.9603),
    ('Frankfurt', 50.1109, 8.6821),
    ('Stuttgart', 48.7758, 9.1829),
    ('Dresden', 51.0504, 13.7373),
    ('Leipzig', 51.3397, 12.3731),
]


class Command(BaseCommand):
    help = 'Populate the database with fake listings for testing.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Number of listings to create')

    def handle(self, *args, **options):
        count = options['count']

        owner, created = User.objects.get_or_create(
            username='test_owner',
            defaults={
                'email': 'test_owner@example.com',
                'address': fake.address(),
                'is_active': True,
            }
        )
        if created:
            owner.set_password('testpass123')
            owner.save()
            self.stdout.write(self.style.SUCCESS(f'Created test owner: {owner.username}'))

        property_types = [PropertyTypeChoices.apartment, PropertyTypeChoices.house, PropertyTypeChoices.studio]

        for i in range(count):
            city, base_lat, base_lon = random.choice(GERMAN_CITIES)
            property_type = random.choice(property_types)

            listing_data = {
                'apartment_name': f'{fake.word().capitalize()} {random.choice(["Loft", "Studio", "Apartment", "House"])}',
                'description': fake.paragraph(nb_sentences=4),
                'address': fake.street_address(),
                'country': CountryChoices.germany,
                'max_guests': random.randint(1, 8),
                'shower_count': random.randint(1, 2),
                'toilets_count': random.randint(1, 2),
                'input_type': random.choice(list(InputTypeChoices.values)),
                'property_type': property_type,
                'parking': random.choice([True, False]),
                'wifi': random.choice([True, False]),
                'can_smoke': random.choice([True, False]),
                'can_pets': random.choice([True, False]),
                'indoor_fireplace': random.choice([True, False]),
                'air_conditioner': random.choice([True, False]),
                'elevator': random.choice([True, False]),
                'facilities_for_guests_with_disabilities': random.choice([True, False]),
                'price_per_night': round(random.uniform(30, 300), 2),
                'owner': owner,
                'latitude': round(base_lat + random.uniform(-0.05, 0.05), 6),
                'longitude': round(base_lon + random.uniform(-0.05, 0.05), 6),
            }

            if property_type == PropertyTypeChoices.house:
                listing_data['floors_count'] = random.randint(1, 3)
                listing_data['floor'] = None
                listing_data['room_count'] = random.randint(2, 6)
            elif property_type == PropertyTypeChoices.studio:
                listing_data['floor'] = random.randint(1, 10)
                listing_data['floors_count'] = None
                listing_data['room_count'] = 1
            else:
                listing_data['floor'] = random.randint(1, 10)
                listing_data['floors_count'] = None
                listing_data['room_count'] = random.randint(1, 5)

            listing = Listing.objects.create(**listing_data)
            self.stdout.write(f'Created listing: {listing.apartment_name} in {city} ({property_type})')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} fake listings.'))