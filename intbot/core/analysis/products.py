"""
Prase Products from PretixData for further joins and analysis in other places.
"""

from decimal import Decimal
from typing import ClassVar, Iterable

import polars as pl
from core.models import PretixData
from pydantic import BaseModel, model_validator


class LocalisedFieldsMixin:
    # Marking as ClassVar here is importnat. It doens't work without it :)
    _localised_fields: ClassVar[Iterable[str]] = ()

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values):
        for field in cls._localised_fields:
            if isinstance(values[field], dict) and "en" in values[field]:
                values[field] = values[field]["en"]
                continue

        return values


class ProductVariation(LocalisedFieldsMixin, BaseModel):
    id: int
    value: str
    description: str | dict
    price: Decimal

    _localised_fields = ["value", "description"]


class Product(LocalisedFieldsMixin, BaseModel):
    id: int
    name: str
    description: str | dict
    variations: list[ProductVariation]
    default_price: Decimal | None = None

    _localised_fields = ["name", "description"]


class FlatProductDescription(BaseModel):
    product_id: int
    variation_id: int | None
    product_name: str
    type: str
    variant: str
    price: Decimal | None


def get_latest_products_data() -> PretixData:
    qs = PretixData.objects.filter(resource=PretixData.PretixResources.products)
    return qs.latest("created_at")


def parse_latest_products_to_objects(pretix_data: PretixData) -> list[Product]:
    data = pretix_data.content
    products = [Product.model_validate(entry) for entry in data]
    return products


def flat_product_data(products: list[Product]) -> pl.DataFrame:
    rows = []
    for p in products:
        if p.variations:
            for v in p.variations:
                if "Late" in v.value:
                    type_ = "Late"
                    name = v.value.replace("Late", "").strip()
                else:
                    type_ = "Regular"
                    name = v.value

                if "Combined" in name:
                    name = "Combined"

                rows.append(
                    FlatProductDescription(
                        product_id=p.id,
                        variation_id=v.id,
                        product_name=p.name,
                        type=type_,
                        variant=name,
                        price=v.price,
                    )
                )
        else:
            rows.append(
                FlatProductDescription(
                    product_id=p.id,
                    variation_id=None,
                    product_name=p.name,
                    variant=p.name,
                    type="Late" if "Late" in p.name else "Regular",
                    price=p.default_price,
                )
            )

    return pl.DataFrame(rows)


def latest_flat_product_data():
    """
    Thin wrapper on getting latest information from the database, and
    converting into a polars data frame
    """
    pretix_data = get_latest_products_data()
    products = parse_latest_products_to_objects(pretix_data)
    return flat_product_data(products)
