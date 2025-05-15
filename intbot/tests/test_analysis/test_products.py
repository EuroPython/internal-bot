from decimal import Decimal

import polars as pl
import pytest
from core.analysis.products import (
    FlatProductDescription,
    Product,
    ProductVariation,
    flat_product_data,
    latest_flat_product_data,
)
from core.models import PretixData
from polars.testing import assert_frame_equal



def test_flat_product_data():
    products = [
        Product(
            id=100,
            name="Business",
            description="Business ticket",
            variations=[
                ProductVariation(id=1, value="Combined", description="", price=800),
                ProductVariation(id=2, value="Conference", description="", price=500),
                ProductVariation(id=3, value="Tutorial", description="", price=400),
            ],
        ),
        Product(
            id=200,
            name="Personal",
            description="Personal ticket",
            variations=[
                ProductVariation(id=4, value="Combined", description="", price=400),
                ProductVariation(id=5, value="Conference", description="", price=300),
                ProductVariation(id=6, value="Tutorial", description="", price=200),
            ],
        ),
    ]

    df = flat_product_data(products)

    assert df.shape == (6, 6)
    assert df.schema == pl.Schema(
        {
            "product_id": pl.Int64,
            "variation_id": pl.Int64,
            "product_name": pl.String,
            "type": pl.String,
            "variant": pl.String,
            "price": pl.Decimal(precision=None, scale=0),
        }
    )


@pytest.mark.django_db
def test_latest_flat_product_data(pretix_data):
    """
    Bigger integrated tests going through everything from getting data from the
    database to returning a polars dataframe
    """
    PretixData.objects.create(
        resource=PretixData.PretixResources.products,
        content=pretix_data["products"],
    )


    # NOTE: Real data from pretix contains more details, this is abbreviated
    # just for the necessary data we need for parsing.
    expected = pl.DataFrame(
        [
            FlatProductDescription(
                product_id=100,
                variation_id=1,
                product_name="Business",
                variant="Conference",
                type="Regular",
                price=Decimal("605.00"),
            ),
            FlatProductDescription(
                product_id=100,
                variation_id=2,
                product_name="Business",
                variant="Tutorials",
                type="Regular",
                price=Decimal("484.00"),
            ),
            FlatProductDescription(
                product_id=100,
                variation_id=3,
                product_name="Business",
                variant="Combined",
                type="Regular",
                price=Decimal("968.00"),
            ),
            FlatProductDescription(
                product_id=100,
                variation_id=4,
                product_name="Business",
                variant="Conference",
                type="Late",
                price=Decimal("907.50"),
            ),
            FlatProductDescription(
                product_id=100,
                variation_id=5,
                product_name="Business",
                variant="Combined",
                type="Late",
                price=Decimal("1452.00"),
            ),
            FlatProductDescription(
                product_id=200,
                variation_id=6,
                product_name="Personal",
                variant="Conference",
                type="Regular",
                price=Decimal("300.00"),
            ),
            FlatProductDescription(
                product_id=200,
                variation_id=7,
                product_name="Personal",
                variant="Tutorials",
                type="Regular",
                price=Decimal("200.00"),
            ),
            FlatProductDescription(
                product_id=200,
                variation_id=8,
                product_name="Personal",
                variant="Combined",
                type="Regular",
                price=Decimal("450.00"),
            ),
            FlatProductDescription(
                product_id=200,
                variation_id=9,
                product_name="Personal",
                variant="Conference",
                type="Late",
                price=Decimal("450.00"),
            ),
            FlatProductDescription(
                product_id=200,
                variation_id=10,
                product_name="Personal",
                variant="Combined",
                type="Late",
                price=Decimal("675.00"),
            ),
        ]
    )

    df = latest_flat_product_data()

    assert_frame_equal(df, expected)
