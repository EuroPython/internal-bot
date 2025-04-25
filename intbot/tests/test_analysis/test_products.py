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
def test_latest_flat_product_data():
    """
    Bigger integrated tests going through everything from getting data from the
    database to returning a polars dataframe
    """
    # NOTE: Real data from pretix contains more details, this is abbreviated
    # just for the necessary data we need for parsing.
    PretixData.objects.create(
        resource=PretixData.PretixResources.products,
        content=[
            {
                "id": 100,
                "category": 2000,
                "name": {"en": "Business"},
                "description": {
                    "en": "If your company pays for you to attend, or if you use Python professionally. When you purchase a Business Ticket, you help us keep the conference affordable for everyone. \r\nThank you!"
                },
                "default_price": "500.00",
                "admission": True,
                "variations": [
                    {
                        "id": 1,
                        "value": {"en": "Conference"},
                        "active": True,
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are **NOT** included. To access Tutorial days please buy a Tutorial or Combined ticket.\r\n\r\n**Net price \u20ac500.00 + 21% Czech VAT**.  \r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "605.00",
                        "price": "605.00",
                    },
                    {
                        "id": 2,
                        "value": {"en": "Tutorials"},
                        "active": True,
                        "description": {
                            "en": "Access to Workshop/Tutorial Days (14-15 July) and the Sprint Weekend (19-20 July), but **NOT** the main conference (16-18 July). \r\n**Net price \u20ac400.00+ 21% Czech VAT.**\r\n\r\nTutorial tickets are only available until 27 June"
                        },
                        "default_price": "484.00",
                        "price": "484.00",
                    },
                    {
                        "id": 3,
                        "value": {"en": "Combined (Conference + Tutorials)"},
                        "active": True,
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n**Net price \u20ac800.00 + 21% Czech VAT.**\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "968.00",
                        "price": "968.00",
                    },
                    {
                        "id": 4,
                        "value": {"en": "Late Conference"},
                        "active": True,
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July) & limited access to specific sponsored/special workshops during the Workshop/Tutorial Days (14-15 July).\r\n**Net price \u20ac750.00 + 21% Czech VAT**\r\n\r\nAvailable from 27 June or after regular Conference tickets are sold out."
                        },
                        "default_price": "907.50",
                        "price": "907.50",
                    },
                    {
                        "id": 5,
                        "value": {"en": "Late Combined"},
                        "active": True,
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n**Net price \u20ac1,200.00 + 21% Czech VAT.**\r\n\r\nAvailable from 27 June or after regular Combined tickets are sold out."
                        },
                        "default_price": "1452.00",
                        "price": "1452.00",
                    },
                ],
            },
            {
                "id": 200,
                "category": 2000,
                "name": {"en": "Personal"},
                "active": True,
                "description": {
                    "en": "If you enjoy Python as a hobbyist or use it as a freelancer."
                },
                "default_price": "300.00",
                "variations": [
                    {
                        "id": 6,
                        "value": {"en": "Conference"},
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are **NOT** included. \r\nTo access Tutorial days please buy a Tutorial or Combined ticket.\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "300.00",
                        "price": "300.00",
                    },
                    {
                        "id": 7,
                        "value": {"en": "Tutorials"},
                        "description": {
                            "en": "Access to Workshop/Tutorial Days (14-15 July) and the Sprint Weekend (19-20 July), but **NOT** the main conference (16-18 July).\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "200.00",
                        "price": "200.00",
                    },
                    {
                        "id": 8,
                        "value": {"en": "Combined (Conference + Tutorials)"},
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "position": 2,
                        "default_price": "450.00",
                        "price": "450.00",
                    },
                    {
                        "id": 9,
                        "value": {"en": "Late Conference"},
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are NOT included. To access Tutorial days please buy a Tutorial or Combined ticket.\r\n\r\nAvailable from 27 June or after regular Conference tickets are sold out."
                        },
                        "default_price": "450.00",
                        "price": "450.00",
                    },
                    {
                        "id": 10,
                        "value": {"en": "Late Combined"},
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n\r\nAvailable from 27 June or after regular Combined tickets are sold out."
                        },
                        "default_price": "675.00",
                        "price": "675.00",
                    },
                ],
            },
        ],
    )
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
