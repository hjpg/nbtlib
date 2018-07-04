"""This module defines tools for creating tag schemas.

Exported items:
    schema         -- Helper function to define compound schemas
    CompoundSchema -- `Compound` subclass that enforces a tag schema
"""


__all__ = ['schema', 'CompoundSchema']


from itertools import chain

from .tag import Compound


def schema(name, dct, *, strict=False):
    """Create a compound tag schema.

    This function is a short convenience function that makes it easy to
    subclass the base `CompoundSchema` class.

    The `name` argument is the name of the class and `dct` should be a
    dictionnary containing the actual schema. The schema should map keys
    to tag types or other compound schemas.

    If the `strict` keyword only argument is set to True, interacting
    with keys that are not defined in the schema will raise a
    `TypeError`.
    """
    return type(name, (CompoundSchema,), {'__slots__': (), 'schema': dct,
                                          'strict': strict})


class CompoundSchema(Compound):
    """Class that extends the base `Compound` tag by enforcing a schema.

    Defining a custom schema is really useful if you're dealing with
    recurring data structures. Subclassing the `CompoundSchema` class
    with your own schema will save you some typing by casting all the
    keys defined in the schema to the appropriate tag type.

    The class inherits from `Compound` and will cast values to the
    predefined tag types for all of the inherited mutating operations.

    Class attributes:
        schema -- Dictionnary mapping keys to tag types or other schemas
        strict -- Boolean enabling strict schema validation
    """

    __slots__ = ()
    schema = {}
    strict = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in self.items():
            correct_value = self._cast(key, value)
            if correct_value is not value:
                super().__setitem__(key, correct_value)

    def __setitem__(self, key, value):
        super().__setitem__(key, self._cast(key, value))

    def update(self, mapping, **kwargs):
        pairs = chain(mapping.items(), kwargs.items())
        super().update(
            (key, self._cast(key, value)) for key, value in pairs
        )

    def _cast(self, key, value):
        schema_type = self.schema.get(key, None)
        if schema_type is None:
            if self.strict:
                raise TypeError(f'Invalid key {key!r}')
        elif not isinstance(value, schema_type):
            return schema_type(value)
        return value
