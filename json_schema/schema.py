"""The actual schema part of `json_schema`."""

from itertools import izip

from json_schema.tokens import token_stream


json_types = (
    list, dict, unicode, int, long, bool, type(None)
)


class SchemaError(Exception):
    pass


class UnexpectedToken(SchemaError):

    def __init__(self, token, expected=None):
        self.token = token
        message = repr(token)
        if expected is not None:
            self.expected = expected
            message += " (expected %r)" % (expected,)
        super(UnexpectedToken, self).__init__(message)


class Schema(object):

    def __init__(self, value):
        self.tokens = list(token_stream(value))

    def validate(self, value):
        """Validate *value* against the schema."""
        return self.validate_tokens(token_stream(value))

    def validate_tokens(self, tokens):
        """Validate *tokens* against the schema."""
        combined_tokens = izip(self.tokens, tokens)
        for (schema_token, real_token) in combined_tokens:
            if schema_token != real_token:
                return (False, schema_token, real_token)
        return (True, None, None)


class SchemaCollectionType(type):

    def __new__(self, name, bases, attrs):
        schema_attnames = tuple(attname for attname in attrs
            if not attname.startswith("_") \
              and isinstance(attrs[attname], json_types))
        schemas = dict((attname, Schema(attrs[attname])) for attname in schema_attnames)
        attrs["schemas"] = schemas
        attrs.update(schemas)
        return super(SchemaCollectionType, self).__new__(self, name, bases, attrs)


class SchemaCollection(object):

    __metaclass__ = SchemaCollectionType

    @classmethod
    def match_to_schema(cls, value):
        tokens = list(token_stream(value))
        for (schema_name, schema) in cls.schemas.iteritems():
            (valid, expected, got) = schema.validate_tokens(tokens)
            if valid:
                return schema_name
