from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Table, Reservation
from django.core.exceptions import ValidationError

# Create your tests here.
class ReservationModelTest(TestCase):

    def setUp(self):
        self.table = Table.objects.create(capacity=4)

    def test_create_reservation(self):
        start = timezone.now()
        end = start + timedelta(hours=2)
        reservation = Reservation(
            table=self.table,
            name="Leo",
            start_time=start,
            end_time=end,
            status="confirmed"
        )
        reservation.full_clean()  # Should not raise
        reservation.save()
        self.assertEqual(Reservation.objects.count(), 1)

    def test_overlapping_reservations_raise_error(self):
        start = timezone.now()
        end = start + timedelta(hours=2)

        Reservation.objects.create(
            table=self.table,
            name="Leo",
            start_time=start,
            end_time=end,
            status="confirmed"
        )

        with self.assertRaises(ValidationError):
            new_reservation = Reservation(
                table=self.table,
                name="Juan",
                start_time=start + timedelta(minutes=30),
                end_time=end + timedelta(minutes=30)
            )
            new_reservation.full_clean()

    def test_auto_delete_if_expired(self):
        start = timezone.now() - timedelta(hours=3)
        end = start + timedelta(hours=1)

        reservation = Reservation.objects.create(
            table=self.table,
            name="Expired",
            start_time=start,
            end_time=end,
            status="confirmed"
        )
        reservation.auto_delete_if_expired()
        self.assertEqual(Reservation.objects.count(), 0)