"""
Tickets tests
"""

import polars as pl
import pytest
from core.analysis.orders import latest_flat_tickets_data
from core.models import PretixData
from polars.testing import assert_frame_equal

random_order = {
    "url": "https://tickets.europython.eu/order/CODE/secret-goes-here/",
    "code": "CODE",
    "fees": [],
    "email": "artur+test@europython.eu",
    "event": "ep2025",
    "phone": None,
    "total": "2.00",
    "locale": "en",
    "secret": "secret-goes-here",
    "status": "p",
    "comment": "",
    "expires": "2025-04-10T23:59:59+02:00",
    "refunds": [],
    "api_meta": {},
    "customer": None,
    "datetime": "2025-03-27T03:04:17+01:00",
    "payments": [],
    "testmode": False,
    "positions": [
        {
            "id": 1000,
            "item": 100,
            "answers": [
                {
                    "answer": "EPS",
                    "options": [],
                    "question": 184831,
                    "option_identifiers": [],
                    "question_identifier": "TWPG9CEQ",
                },
                {
                    "answer": "35",
                    "options": [],
                    "question": 184832,
                    "option_identifiers": [],
                    "question_identifier": "3PGQBFXV",
                },
            ],
            "voucher": 8868743,
            "variation": 1,
            "positionid": 1,
            "canceled": False,
            "attendee_name": "Artur Czepiel",
            "attendee_email": "artur+test@europython.eu",
        },
        {
            "id": 101,
            "item": 725441,
            "order": "CODE",
            "price": "0.00",
            "variation": None,
            "canceled": False,
            "secret": "t-shirt-secret",
            "answers": [
                {
                    "answer": "L - straight cut",
                    "options": [335101],
                    "question": 184841,
                    "option_identifiers": ["WHUDNPJK"],
                    "question_identifier": "A8JP9TRN",
                }
            ],
        },
    ],
    "payment_date": "2025-03-27",
    "last_modified": "2025-03-27T03:04:20+01:00",
    "invoice_address": {
        "city": "Krak\u00f3w",
        "name": "Artur Czepiel",
        "state": "",
        "street": "Krakowska 123",
        "vat_id": "",
        "company": "",
        "country": "PL",
        "zipcode": "30-100",
        "name_parts": {
            "_scheme": "given_family",
            "given_name": "Artur",
            "family_name": "Czepiel",
        },
        "is_business": False,
        "custom_field": None,
        "vat_id_validated": False,
        "internal_reference": "No internal reference",
    },
}


@pytest.mark.django_db
def test_latest_flat_tickets_data(pretix_data):
    """
    Big integrated tests doing a simple sanity check through all the layers.
    Storage+Parsing+Reporting.
    """
    PretixData.objects.create(
        content=pretix_data["products"],
        resource=PretixData.PretixResources.products,
    )
    PretixData.objects.create(
        content=pretix_data["orders"],
        resource=PretixData.PretixResources.orders,
    )

    expected = pl.DataFrame(
        {
            "state": ["submitted", "withdrawn"],
            "len": [2, 1],
        }
    )

    df = latest_flat_tickets_data()

    assert_frame_equal(df, expected)
