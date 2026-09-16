from django.conf import settings
from django.db.models import Avg, Count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.bookings.models import Booking
from apps.reviews.models import Review
from .models import ListingStatistic, UserStatistic



# Создание UserStatistic при регистрации

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_statistic(sender, instance, created, **kwargs):
    if created:
        UserStatistic.objects.get_or_create(user=instance)



# Booking → обновление статистики листинга и юзеров

@receiver(post_save, sender=Booking)
def on_booking_created(sender, instance, created, **kwargs):
    if not created:
        return

    listing_stat, _ = ListingStatistic.objects.get_or_create(listing=instance.listing)
    listing_stat.booking_count = instance.listing.bookings.count()
    listing_stat.total_revenue = sum(b.price for b in instance.listing.bookings.all())
    listing_stat.save()

    guest_stat, _ = UserStatistic.objects.get_or_create(user=instance.guest)
    guest_stat.booking_count = instance.guest.bookings.count()
    guest_stat.total_spent = sum(b.price for b in instance.guest.bookings.all())
    guest_stat.save()

    owner_stat, _ = UserStatistic.objects.get_or_create(user=instance.listing.owner)
    owner_stat.total_earned = sum(
        b.price for listing in instance.listing.owner.listings.all() for b in listing.bookings.all()
    )
    owner_stat.save()



# Review → обновление рейтинга листинга и хозяина

@receiver(post_save, sender=Review)
def on_review_saved(sender, instance, **kwargs):
    listing = instance.booking.listing
    listing_stat, _ = ListingStatistic.objects.get_or_create(listing=listing)
    agg = Review.objects.filter(booking__listing=listing).aggregate(avg=Avg('stars'), count=Count('id'))
    listing_stat.average_rating = agg['avg']
    listing_stat.reviews_count = agg['count']
    listing_stat.save()

    owner = listing.owner
    owner_stat, _ = UserStatistic.objects.get_or_create(user=owner)
    owner_reviews = Review.objects.filter(booking__listing__owner=owner)
    owner_agg = owner_reviews.aggregate(avg=Avg('stars'))
    owner_stat.stars_count = owner_agg['avg']
    owner_stat.save()


@receiver(post_delete, sender=Review)
def on_review_deleted(sender, instance, **kwargs):
    on_review_saved(sender=Review, instance=instance)



# Listing → обновление listing_count у владельца

from apps.listings.models import Listing

@receiver(post_save, sender=Listing)
def on_listing_created(sender, instance, created, **kwargs):
    if not created:
        return
    owner_stat, _ = UserStatistic.objects.get_or_create(user=instance.owner)
    owner_stat.listing_count = instance.owner.listings.count()
    owner_stat.save()