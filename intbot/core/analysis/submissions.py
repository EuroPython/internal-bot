"""
Basic analysis of Pretalx Submissions data
"""

from datetime import datetime
from typing import ClassVar, Iterable

import plotly.express as px
import polars as pl
from core.models import PretalxData
from pydantic import BaseModel, model_validator


class LocalisedFieldsMixin:
    # Marking as ClassVar here is important. It doens't work without it :)
    _localised_fields: ClassVar[Iterable[str]] = ()

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values):
        for field in cls._localised_fields:
            if isinstance(values[field], dict) and "en" in values[field]:
                values[field] = values[field]["en"]
                continue

        return values


class Submission(LocalisedFieldsMixin, BaseModel):
    code: str
    title: str
    submission_type: str | dict
    track: str | None
    state: str
    abstract: str
    duration: int
    created: datetime
    level: str = ""
    outline: str | None = None
    event: str = "ep2025"

    _localised_fields = ["submission_type", "track"]

    class Questions:
        level = "Expected audience expertise"
        outline = "Outline"

    @model_validator(mode="before")
    def extract_answers(cls, values):
        # Some things are available as answers to questions and we can extract
        # them here
        # Using .get since this should be optional when creating Submission
        # objects manually
        for answer in values.get("answers", ""):
            # Submission in the API will include answers to questions asked on
            # submission and on the speaker. Let's explicitly filter out only
            # submission questions.
            is_submission_question = answer["submission"] is not None

            if is_submission_question and cls.matches_question(answer, cls.Questions.level):
                values["level"] = answer["answer"]

            if is_submission_question and cls.matches_question(answer, cls.Questions.outline):
                values["outline"] = answer["answer"]

        return values

    @staticmethod
    def matches_question(answer: dict, question: str) -> bool:
        """
        Returns True if the answer corresponds to the question passed as the second
        argument.

        Answers come in a nested structure that includes localised question
        text. This function is a small wrapper to encapsulate that behaviour.
        """
        return question == answer.get("question", {}).get("question", {}).get("en")


def get_latest_submissions_data() -> PretalxData:
    return PretalxData.objects.filter(
        resource=PretalxData.PretalxResources.submissions
    ).latest("created_at")


def parse_latest_submissions_to_objects(pretalx_data: PretalxData) -> list[Submission]:
    data = pretalx_data.content
    # NOTE: add event as context here
    submissions = [Submission.model_validate(entry) for entry in data]
    return submissions


def flat_submissions_data(submissions: list[Submission]) -> pl.DataFrame:
    """
    Returns a polars data frame with flat description of Submissions

    This functions mostly exists to make the API consistent between different
    types of data
    """
    return pl.DataFrame(submissions)


def latest_flat_submissions_data() -> pl.DataFrame:
    """
    Thin wrapper on getting latest information from the database, and
    converting into a polars data frame
    """
    pretalx_data = get_latest_submissions_data()
    submissions = parse_latest_submissions_to_objects(pretalx_data)
    return flat_submissions_data(submissions)


def group_submissions_by_state(submissions: pl.DataFrame) -> pl.DataFrame:
    return submissions.group_by("state").len().sort("len", descending=True)


def piechart_submissions_by_state(submissions_by_state: pl.DataFrame):
    fig = px.pie(
        submissions_by_state,
        values="len",
        names="state",
        title="state of the submission",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    return fig
