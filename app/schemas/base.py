"""."""

import pydantic
import typing

from pydantic.alias_generators import to_camel


class BaseSchema(pydantic.BaseModel):
    """Base schema."""

    model_config = pydantic.ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


TSchema = typing.TypeVar("TSchema", bound=BaseSchema)
