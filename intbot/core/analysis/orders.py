"""
Parse Pretix Orders
"""

from datetime import date
from decimal import Decimal

import polars as pl
from core.analysis.products import (
    FlatProductDescription,
    get_latest_products_data,
    get_product_lookup,
)
from core.models import PretixData
from pydantic import BaseModel, ValidationInfo, model_validator


class InvoiceAddress(BaseModel):
    company: str
    country: str
    vat_id: str


class OrderItem(BaseModel):
    id: int
    item: int
    product: FlatProductDescription | None = None
    attendee_email: str | None
    attendee_name: str | None
    price: Decimal
    voucher: int | None = None
    # answers: list[dict]
    previous_conferences: str | None = None
    addon_to: int | None
    canceled: bool
    order_date: date | None = None
    country: str | None = None
    company: str | None = None
    affiliation: str | None = None

    class Questions:
        previous_conferences = "S7CSFACW"
        affiliation = "TWPG9CEQ"

    @model_validator(mode="before")
    def extract(cls, values):
        # Some things are available as answers to questions and we can extract
        # them here
        for answer in values["answers"]:
            if cls.matches_question(answer, cls.Questions.previous_conferences):
                values["previous_conferences"] = answer["answer"]

            if cls.matches_question(answer, cls.Questions.affiliation):
                values["affiliation"] = answer["answer"]

        return values

    @model_validator(mode="before")
    def map_product(cls, values, info: ValidationInfo):
        # year = info.context["year"]
        products = info.context["products_lookup"]
        # passing product to make sure
        values["product"] = products.get(values["item"], values["variation"])

        return values

    @staticmethod
    def matches_question(answer: dict, question: str) -> bool:
        return answer.get("question_identifier", "") == question


class Order(BaseModel):
    code: str
    status: str
    email: str
    payment_date: date | None
    total: Decimal
    positions: list[OrderItem]
    invoice_address: InvoiceAddress
    status: str

    class Status:
        PAID = "p"


class Ticket(BaseModel):
    order_code: str
    order_status: str
    email: str | None
    order_date: date | None
    product_name: str
    product_id: int
    variation_id: int
    product_type: str
    full_name: str | None
    country: str
    company: str | None
    affiliation: str | None
    voucher: int | None


def get_latest_orders_data() -> PretixData:
    return PretixData.objects.filter(resource=PretixData.PretixResources.orders).latest(
        "created_at"
    )


def parse_latest_orders_to_objects(
    *,
    pretix_data_orders: PretixData,
    pretix_data_products: PretixData,
) -> list[Order]:
    products_lookup = get_product_lookup(pretix_data_products)
    orders_data = pretix_data_orders.content
    orders = [
        Order.model_validate(entry, context={"products_lookup": products_lookup})
        for entry in orders_data
    ]
    return orders


def flat_tickets(orders: list[Order]) -> list[Ticket]:
    ONSITE_PRODUCTS = [
        "Business",
        "Personal",
        "Education",
        "Presenter",
        "Sponsor Conference Pass",
        "Community Contributors",
        "Grant ticket",
    ]

    tickets = []
    for order in orders:
        if order.status != Order.Status.PAID:
            continue

        for pos in order.positions:
            # NOTE: This should be a different check in the future, but for now
            # it's good enough

            # Assume product already exists here
            assert pos.product

            if pos.product.product_name in ONSITE_PRODUCTS:
                ticket = Ticket(
                    order_code=order.code,
                    order_status=order.status,
                    order_date=order.payment_date,
                    product_name=pos.product.product_name,
                    product_id=pos.product.product_id,
                    variation_id=pos.product.variation_id,
                    product_type=pos.product.type,
                    email=pos.attendee_email,
                    full_name=pos.attendee_name,
                    affiliation=pos.affiliation,
                    country=order.invoice_address.country,
                    company=order.invoice_address.company,
                    voucher=pos.voucher,
                )

                tickets.append(ticket)


    return tickets

def flat_tickets_data(orders: list[Order]) -> pl.DataFrame:
    tickets = flat_tickets(orders)
    return pl.DataFrame(tickets, infer_schema_length=None)


def latest_flat_tickets_data() -> pl.DataFrame:
    """
    Thin wrapper on getting latest information from the database, and
    converting into a polars data frame
    """
    orders_data = get_latest_orders_data()
    products_data = get_latest_products_data()
    orders = parse_latest_orders_to_objects(
        pretix_data_orders=orders_data, pretix_data_products=products_data
    )
    return flat_tickets_data(orders)


def group_tickets_by_product(tickets_data: pl.DataFrame) -> pl.DataFrame:
    return tickets_data.group_by("product_name").len().sort("len", descending=True)
