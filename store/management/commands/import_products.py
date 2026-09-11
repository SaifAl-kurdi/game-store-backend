import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import Product


class Command(BaseCommand):
    help = "Import products from a CSV file into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path of the CSV file to import.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])

        if not csv_path.exists():
            raise CommandError(f"CSV file does not exist: {csv_path}")

        if not csv_path.is_file():
            raise CommandError(f"The provided path is not a file: {csv_path}")

        required_columns = {
            "id",
            "title",
            "description",
            "price",
            "location",
        }

        created_count = 0
        updated_count = 0
        seen_ids = set()

        try:
            with csv_path.open(
                mode="r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                if not reader.fieldnames:
                    raise CommandError("The CSV file does not have a header.")

                actual_columns = {
                    column.strip()
                    for column in reader.fieldnames
                }

                missing_columns = required_columns - actual_columns

                if missing_columns:
                    raise CommandError(
                        "Missing CSV columns: "
                        + ", ".join(sorted(missing_columns))
                    )

                with transaction.atomic():
                    for row_number, row in enumerate(reader, start=2):
                        try:
                            product_id = int(row["id"].strip())
                            title = row["title"].strip()
                            description = row["description"].strip()
                            price = Decimal(row["price"].strip())
                            location = row["location"].strip().upper()

                            if product_id in seen_ids:
                                raise ValueError(
                                    f"Duplicate product ID: {product_id}"
                                )

                            seen_ids.add(product_id)

                            if not title:
                                raise ValueError("Title cannot be empty.")

                            if not description:
                                raise ValueError(
                                    "Description cannot be empty."
                                )

                            product = Product.objects.filter(
                                id=product_id
                            ).first()

                            created = product is None

                            if created:
                                product = Product(id=product_id)

                            product.title = title
                            product.description = description
                            product.price = price
                            product.location = location

                            product.full_clean()
                            product.save()
                            

                            if created:
                                created_count += 1
                            else:
                                updated_count += 1

                        except (
                            ValueError,
                            InvalidOperation,
                            ValidationError,
                        ) as error:
                            raise CommandError(
                                f"Invalid data on CSV row "
                                f"{row_number}: {error}"
                            ) from error

        except UnicodeDecodeError as error:
            raise CommandError(
                "The CSV file must use UTF-8 encoding."
            ) from error

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed: "
                f"{created_count} created, "
                f"{updated_count} updated."
            )
        )