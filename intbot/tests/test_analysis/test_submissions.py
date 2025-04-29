from datetime import datetime

import polars as pl
import pytest
from core.analysis.submissions import (
    Submission,
    group_submissions_by_state,
    latest_flat_submissions_data,
    piechart_submissions_by_state,
)
from core.models import PretalxData
from polars.testing import assert_frame_equal


def _create_pretalx_data():
    PretalxData.objects.create(
        resource=PretalxData.PretalxResources.submissions,
        content=[
            {
                "code": "ABCDEF",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "",
                "state": "submitted",
                "title": "Title",
                "track": {"en": "Machine Learning, NLP and CV"},
                "created": "2025-01-14T01:24:36",
                "answers": [],
                "tag_ids": [],
                "abstract": "Abstract",
                "duration": 30,
                "speakers": [],
                "submission_type": "Talk",
            },
            {
                "code": "FGHIJKL",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "",
                "state": "submitted",
                "title": "Title",
                "track": {"en": "Machine Learning, NLP and CV"},
                "created": "2025-01-14T01:24:36",
                "answers": [],
                "tag_ids": [],
                "abstract": "Abstract",
                "duration": 30,
                "speakers": [],
                "submission_type": "Talk",
            },
            {
                "code": "XYZF12",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "Notes",
                "state": "withdrawn",
                "title": "Title 2",
                "track": {"en": "Track 2"},
                "answers": [],
                "created": "2025-01-16T11:44:26",
                "tag_ids": [],
                "abstract": "Minimal Abstract",
                "duration": 45,
                "speakers": [],
                "submission_type": {"en": "Talk (long session)"},
            },
        ],
    )


def test_submission_is_answer_to():
    answers = [
        {
            "id": 123,
            "answer": "1. Introduction - 5 minutes",
            "person": None,
            "review": None,
            "options": [],
            "question": {"id": 1111, "question": {"en": "Outline"}},
            "submission": "ABCDE",
            "answer_file": None,
        },
    ]

    if answers[0]["question"]["question"]["en"] == "Outline":
        assert Submission.matches_question(answers[0], "Outline")


@pytest.mark.django_db
def test_latest_flat_product_data():
    """
    Bigger integrated tests going through everything from getting data from the
    database to returning a polars dataframe
    """
    _create_pretalx_data()
    expected = pl.DataFrame(
        [
            Submission(
                code="ABCDEF",
                title="Title",
                submission_type="Talk",
                track="Machine Learning, NLP and CV",
                state="submitted",
                abstract="Abstract",
                duration=30,
                created=datetime(2025, 1, 14, 1, 24, 36),
                level="",
                outline=None,
                event="ep2025",
            ),
            Submission(
                code="FGHIJKL",
                title="Title",
                submission_type="Talk",
                track="Machine Learning, NLP and CV",
                state="submitted",
                abstract="Abstract",
                duration=30,
                created=datetime(2025, 1, 14, 1, 24, 36),
                level="",
                outline=None,
                event="ep2025",
            ),
            Submission(
                code="XYZF12",
                title="Title 2",
                submission_type="Talk (long session)",
                track="Track 2",
                state="withdrawn",
                abstract="Minimal Abstract",
                duration=45,
                created=datetime(2025, 1, 16, 11, 44, 26),
                level="",
                outline=None,
                event="ep2025",
            ),
        ]
    )

    df = latest_flat_submissions_data()

    assert_frame_equal(df, expected)


@pytest.mark.django_db
def test_group_submissions_by_state():
    """
    Bigger integrated tests going through everything from getting data from the
    database to returning a polars dataframe
    """
    _create_pretalx_data()
    expected = pl.DataFrame(
        {
            "state": ["submitted", "withdrawn"],
            "len": [2, 1],
        }
    )
    expected = expected.cast({"len": pl.UInt32})  # need cast to make it consistent

    df = group_submissions_by_state(latest_flat_submissions_data())

    assert_frame_equal(df, expected)


@pytest.mark.django_db
def test_piechart_submissions_by_state():
    """
    Bigger integrated tests going through everything from getting data from the
    database to returning a polars dataframe
    """
    _create_pretalx_data()
    df = group_submissions_by_state(latest_flat_submissions_data())

    # There are actually no assertions here, just running this code in case it
    # fails :D
    piechart_submissions_by_state(df)
