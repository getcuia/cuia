"""A base class for all models."""


from typing import Generic, TypeVar


Message = TypeVar("Message")


class Model(Generic[Message]):
    """Base class for all models."""

    pass
