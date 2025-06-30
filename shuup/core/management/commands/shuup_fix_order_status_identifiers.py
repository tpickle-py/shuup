
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from shuup.core.models import OrderStatus, OrderStatusRole


class Command(BaseCommand):
    @atomic
    def handle(self, *args, **options):
        data = [  # role, invalid_identifier, valid_identifier
            (OrderStatusRole.PROCESSING, "canceled", "processing"),
            (OrderStatusRole.COMPLETE, "processing", "complete"),
            (OrderStatusRole.CANCELED, "complete", "canceled"),
        ]

        to_post_process = []

        for role, invalid_identifier, valid_identifier in data:
            status = OrderStatus.objects.filter(
                identifier=invalid_identifier, role=role
            ).first()
            if not status:
                self.stdout.write(f"No changes to {role} statuses")
                continue
            tmp_identifier = valid_identifier + "_tmp"
            self.stdout.write(
                f"Updating identifier of {role} status: {status.identifier!r} -> {tmp_identifier!r}"
            )
            status.identifier = tmp_identifier
            status.save()
            to_post_process.append(status)

        for status in to_post_process:
            new_identifier = status.identifier.replace("_tmp", "")
            self.stdout.write(
                f"Updating identifier of {status.role} status: {status.identifier!r} -> {new_identifier!r}"
            )
            status.identifier = new_identifier
            status.save()
