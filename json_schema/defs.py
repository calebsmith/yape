"""Those handy tokens, metatokens and whatnot."""

from json_schema.tokens import StringToken, IntegerToken, MetaToken

class UnsignedIntegerToken(IntegerToken):
    def validate(self, value):
        return super(UnsignedIntegerToken, self).validate(value) \
          and value >= 0

class UInt32Token(UnsignedIntegerToken):
    def validate(self, value):
        return super(UInt32Token, self).validate(value) \
          and value <= 2 ** 32

class AnyString(MetaToken): matching_token_types = (StringToken,)
class AnyInteger(MetaToken): matching_token_types = (IntegerToken,)
