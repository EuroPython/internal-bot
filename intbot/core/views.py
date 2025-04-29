from core.analysis.products import latest_flat_product_data
from core.analysis.submissions import (
    group_submissions_by_state,
    latest_flat_submissions_data,
    piechart_submissions_by_state,
)
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.safestring import mark_safe


def days_until(request):
    delta = settings.CONFERENCE_START - timezone.now()

    return TemplateResponse(
        request,
        "days_until.html",
        {
            "days_until": delta.days,
        },
    )


@login_required
def products(request):
    """
    For now this is just an example of the implementation.

    Table with products is not that useful, but it's the easiest one to
    implement first as proof of concept
    """
    df = latest_flat_product_data()
    columns = df.columns
    rows = df.rows()

    return TemplateResponse(
        request,
        "table.html",
        {
            "columns": columns,
            "rows": rows,
        },
    )


@login_required
def submissions(request):
    """
    Show some basic aggregation of submissions data
    """

    df = latest_flat_submissions_data()
    by_state = group_submissions_by_state(df)
    piechart = piechart_submissions_by_state(by_state)

    return TemplateResponse(
        request,
        "submissions.html",
        {
            "piechart": mark_safe(
                piechart.to_html(
                    full_html=False,
                    include_plotlyjs="cdn",
                )
            ),
        },
    )
