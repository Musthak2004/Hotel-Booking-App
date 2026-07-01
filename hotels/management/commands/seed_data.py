"""
Management command to seed the database with demo data.

Usage:
    python manage.py seed_data

Creates:
    - 2 hotel owners
    - 1 customer
    - 3 hotels with 2-3 rooms each
    - Sample bookings, reviews, and payments
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from reviews.models import Review
from payments.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo data for testing"

    def handle(self, *args, **options):
        today = date.today()

        # -- Create users ----------------------------------------------------
        owner1, _ = User.objects.get_or_create(
            email="alice@example.com",
            defaults={
                "username": "alice",
                "role": "owner",
                "phone_number": "+1-555-0101",
            },
        )
        if not owner1.password or owner1.password.startswith("!"):
            owner1.set_password("password123")
            owner1.save()

        owner2, _ = User.objects.get_or_create(
            email="bob@example.com",
            defaults={
                "username": "bob",
                "role": "owner",
                "phone_number": "+1-555-0102",
            },
        )
        if not owner2.password or owner2.password.startswith("!"):
            owner2.set_password("password123")
            owner2.save()

        customer, _ = User.objects.get_or_create(
            email="charlie@example.com",
            defaults={
                "username": "charlie",
                "role": "customer",
                "phone_number": "+1-555-0103",
            },
        )
        if not customer.password or customer.password.startswith("!"):
            customer.set_password("password123")
            customer.save()

        self.stdout.write(self.style.SUCCESS(f"[OK] Users: {owner1.email}, {owner2.email}, {customer.email}"))

        # -- Create hotels ---------------------------------------------------
        hotel1, _ = Hotel.objects.get_or_create(
            name="Grand Plaza Hotel",
            defaults={
                "owner": owner1,
                "description": "A luxurious 5-star hotel in the heart of Paris, offering stunning views of the Eiffel Tower, world-class dining, and exceptional service.",
                "address": "15 Avenue des Champs-Elysees",
                "city": "Paris",
                "country": "France",
                "phone_number": "+33-1-2345-6789",
                "email": "info@grandplaza.fr",
                "is_active": True,
            },
        )

        hotel2, _ = Hotel.objects.get_or_create(
            name="Seaside Resort & Spa",
            defaults={
                "owner": owner1,
                "description": "Escape to our beachfront paradise with private sandy beaches, infinity pools, and award-winning spa treatments.",
                "address": "42 Coastal Highway",
                "city": "Nice",
                "country": "France",
                "phone_number": "+33-4-9876-5432",
                "email": "hello@seasideresort.fr",
                "is_active": True,
            },
        )

        hotel3, _ = Hotel.objects.get_or_create(
            name="Mountain Lodge",
            defaults={
                "owner": owner2,
                "description": "A cozy alpine retreat nestled in the Swiss Alps, perfect for skiing in winter and hiking in summer.",
                "address": "8 Bergweg",
                "city": "Zermatt",
                "country": "Switzerland",
                "phone_number": "+41-27-123-4567",
                "email": "stay@mountainlodge.ch",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"[OK] Hotels: {hotel1.name}, {hotel2.name}, {hotel3.name}"))

        # -- Create rooms ----------------------------------------------------
        rooms_data = [
            # (hotel, room_number, room_type, price, capacity, total, description)
            (hotel1, "101", "single", 180, 1, 5, "Cozy single room with city view"),
            (hotel1, "201", "double", 280, 2, 8, "Spacious double room with balcony"),
            (hotel1, "301", "suite", 450, 3, 3, "Executive suite with panoramic views"),
            (hotel2, "1A", "double", 220, 2, 10, "Ocean-view double room"),
            (hotel2, "2A", "deluxe", 350, 2, 5, "Deluxe room with private jacuzzi"),
            (hotel2, "3A", "family", 400, 4, 4, "Family suite with kitchenette"),
            (hotel3, "1", "single", 120, 1, 4, "Standard single with mountain view"),
            (hotel3, "2", "double", 200, 2, 6, "Double room with rustic furnishings"),
            (hotel3, "3", "suite", 320, 4, 3, "Chalet suite with fireplace"),
        ]

        created_rooms = []
        for hotel, rn, rtype, price, cap, total, desc in rooms_data:
            room, _ = Room.objects.get_or_create(
                hotel=hotel,
                room_number=rn,
                defaults={
                    "room_type": rtype,
                    "description": desc,
                    "price_per_night": price,
                    "capacity": cap,
                    "total_rooms": total,
                    "available_rooms": total,
                    "is_available": True,
                },
            )
            created_rooms.append(room)
            self.stdout.write(f"  -> Room {rn} ({rtype}) - ${price}/night")

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(created_rooms)} rooms created"))

        # -- Create bookings -------------------------------------------------
        booking1, _ = Booking.objects.get_or_create(
            user=customer,
            room=created_rooms[0],
            check_in=today + timedelta(days=7),
            check_out=today + timedelta(days=10),
            defaults={
                "guests": 1,
                "total_price": 180 * 3,
                "status": "confirmed",
            },
        )

        booking2, _ = Booking.objects.get_or_create(
            user=customer,
            room=created_rooms[3],
            check_in=today + timedelta(days=14),
            check_out=today + timedelta(days=18),
            defaults={
                "guests": 2,
                "total_price": 220 * 4,
                "status": "pending",
            },
        )

        booking3, _ = Booking.objects.get_or_create(
            user=customer,
            room=created_rooms[6],
            check_in=today + timedelta(days=30),
            check_out=today + timedelta(days=33),
            defaults={
                "guests": 1,
                "total_price": 120 * 3,
                "status": "pending",
            },
        )

        self.stdout.write(self.style.SUCCESS(f"[OK] {3} bookings created"))

        # -- Create reviews --------------------------------------------------
        review1, _ = Review.objects.get_or_create(
            user=customer,
            hotel=hotel1,
            defaults={
                "rating": 5,
                "comment": "Absolutely incredible stay! The staff were wonderful and the views of the Eiffel Tower from our room were breathtaking. The breakfast buffet was world-class.",
            },
        )

        review2, _ = Review.objects.get_or_create(
            user=customer,
            hotel=hotel2,
            defaults={
                "rating": 4,
                "comment": "Beautiful resort with excellent amenities. The spa treatments were fantastic. Only minor complaint is that the beach was a bit crowded during peak hours.",
            },
        )

        self.stdout.write(self.style.SUCCESS(f"[OK] {2} reviews created"))

        # -- Create payments -------------------------------------------------
        payment1, _ = Payment.objects.get_or_create(
            booking=booking1,
            defaults={
                "amount": booking1.total_price,
                "payment_method": "card",
                "transaction_id": "pi_demo_seed_" + str(booking1.id),
                "status": "completed",
                "paid_at": timezone.now(),
            },
        )

        self.stdout.write(self.style.SUCCESS(f"[OK] {1} payment created"))

        # -- Summary ---------------------------------------------------------
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("  Seed data complete!"))
        self.stdout.write(f"  Users:     {User.objects.count()}")
        self.stdout.write(f"  Hotels:    {Hotel.objects.count()}")
        self.stdout.write(f"  Rooms:     {Room.objects.count()}")
        self.stdout.write(f"  Bookings:  {Booking.objects.count()}")
        self.stdout.write(f"  Reviews:   {Review.objects.count()}")
        self.stdout.write(f"  Payments:  {Payment.objects.count()}")
        self.stdout.write("=" * 50)
        self.stdout.write("\nDemo logins (password: password123):")
        self.stdout.write("  Owner:    alice@example.com / password123")
        self.stdout.write("  Owner:    bob@example.com / password123")
        self.stdout.write("  Customer: charlie@example.com / password123")
