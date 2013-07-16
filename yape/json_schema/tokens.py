"""Tokens and all that.

A token (TK): a basic atom that only has a context.
A value token (VTK): an atom that has yet another dimension: its value.
A metatoken (MTK): not really an atom, could be matching anything.

See the class' individual documentation for more, and a lot of examples.
"""

from yape.types import JSONDict, JSONList


class TokenError(Exception):
    @classmethod
    def with_token(self, token):
        self.token = token
        message = repr(token)
        for subtoken in token:
            message += " in %r" % (subtoken,)
        super(TokenError, self).__init__((subtoken, message))


class InvalidTokenValue(TokenError):
    pass


class BadInputValue(TokenError):
    def __init__(self, value, context=None):
        context = context or ()
        self.value = value
        message = repr(context)
        for token in context:
            message += " in %r" % (token,)
        super(BadInputValue, self).__init__((message, value))


class Token(object):
    """A token is a representation of an atomic part of a schema.

    The basic token has only one property to it: its context. Contexts are what
    allow tokens to be useful. 
    
    A token with the same context as another compares equal if they share the
    same class. Comparison is pretty important in schema validation, I'd say.
    
    But let's get an example going.

    >>> foo = Token()
    >>> bar = Token()
    >>> foo == bar
    True
    >>> foo != bar
    False

    So yeah, big deal. But let's have a look at contexts, eh?
    >>> subbar = Token(bar)
    >>> subbar == bar
    False

    By the way, if you wanted to know if *subbar* is a descendant of *bar*
    context-wise, you'd do:
    >>> subbar in bar
    True

    And if we'd want to see the whole chain, just use list():
    >>> list(subbar)
    [<Token>]
    """
    __slots__ = ("context",)

    def __init__(self, context=None):
        self.context = context

    def __eq__(self, other):
        return hasattr(other, "context") and other.context == self.context

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__,)

    def __iter__(self):
        """Yield the whole context chain up to the top-level."""
        context = self.context
        while context is not None:
            yield context
            context = context.context

    def __contains__(self, other):
        """Return whether or not *other* is a contextual descendant of *self*.
        """
        for value in other:
            if value is self:
                return True
        return False


class ValueToken(Token):
    """A token which has an actual value.

    Some tokens aren't just simply tokens. Lists are simple tokens, which
    contain other tokens, but for example integers are tokens which have
    multiple representations that aren't equal unless they're specified to be
    equal.

    Two value tokens (henceforth known as VTKs) are only equal if their values
    compare equal, and their contexts.
    >>> ValueToken("abc") == ValueToken("abc")
    True
    >>> ValueToken("abcd") == ValueToken("abc")
    False

    As we'll see shortly, the context matters.
    >>> vtk_a1 = ValueToken("a", ValueToken(123))
    >>> vtk_a2 = ValueToken("a", ValueToken(321))
    >>> vtk_a1 == vtk_a2
    False

    Now, the correct context and value:
    >>> vtk_a3 = ValueToken("a", ValueToken(123))
    >>> vtk_a1 is vtk_a3, vtk_a1 == vtk_a3
    (False, True)

    Contexts recurse. This is interesting, and indeed a requirement for a
    useful comparison.
    >>> a = ValueToken(1)
    >>> b = ValueToken(2, a)
    >>> c1 = ValueToken(3, b)
    >>> c2 = ValueToken(3, a)
    >>> d1 = ValueToken(4, c1)
    >>> d2 = ValueToken(4, c2)
    >>> d1 == d2
    False

    Now let's look at the two context chains here.
    >>> list(d1)
    [<ValueToken 3>, <ValueToken 2>, <ValueToken 1>]
    >>> list(d2)
    [<ValueToken 3>, <ValueToken 1>]

    It's pretty obvious that *d2* is missing a VTK of 1. Let's create a new VTK
    of 2 with a context of *a*, and set it as the context of *c2*.
    >>> b2 = ValueToken(2, a)
    >>> c2.context = b2

    Now the context chain should be correct, and `d1 == d2` should be True,
    even though we made new VTK objects.
    >>> list(d2)
    [<ValueToken 3>, <ValueToken 2>, <ValueToken 1>]
    >>> d1 == d2
    True
    """
    __slots__ = ("value",)
    valid_types = (object,)

    def __init__(self, value, context=None):
        super(ValueToken, self).__init__(context)
        if not self.validate(value):
            raise InvalidTokenValue.with_token(self, value)
        self.value = value

    def validate(self, value):
        """Validate that *value* is a valid value for this type of value
        token.
        """
        return isinstance(value, self.valid_types)

    def __eq__(self, other):
        return super(ValueToken, self).__eq__(other) \
          and other.value == self.value

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.value)


class SequenceToken(Token):
    pass


class MappingToken(Token):
    pass


class NullToken(Token):
    pass


class TrueToken(Token):
    pass


class FalseToken(Token):
    pass


class MapKeyToken(Token):
    pass


class MapValueToken(Token):
    pass


class StringToken(ValueToken):
    valid_types = (unicode, str)


class IntegerToken(ValueToken):
    valid_types = (int, long)


class DecimalToken(ValueToken):
    valid_types = (float,)


class MetaTokenType(type):

    def __new__(self, name, bases, attrs):
        if "predicate" in attrs:
            attrs["predicate"] = classmethod(attrs["predicate"])
        attrs["__eq__"] = classmethod(self.__eq__)
        attrs["__ne__"] = classmethod(self.__eq__)
        return super(MetaTokenType, self).__new__(self, name, bases, attrs)

    def __eq__(self, other):
        return isinstance(other, self.matching_token_types) \
          and self.predicate(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def predicate(self, other):
        return True


class MetaToken(Token):
    r"""Metatokens (MTKs) are just like ordinary tokens but they compare a bit
    differently.
    
    They can match any token you'd like, and are never generated by the
    *token_stream* function, because they're not really concrete tokens.

    To customize the behavior of MTKs, let's have some examples! The most
    common use of MTKs is to have a type of token in a schema that matches some
    arbitrary other token which you might even have to run some tests on.

    A basic example is the "any string" type of deal. Let's implement our own.
    >>> class AnyString(MetaToken):
    ...     matching_token_types = (StringToken,)
    ... 
    >>> AnyString == StringToken(u"Hello world!")
    True
    >>> AnyString == IntegerToken(123)
    False

    Neat, huh? But what if we wanted a more rigorous example. Like, only
    unsigned 15-bit integers where the seventh bit may be set only if the third
    is.
    >>> class VerySpecialInteger(MetaToken):
    ...     matching_token_types = (IntegerToken,)
    ...     def predicate(cls, token):
    ...         v = getattr(token, "value", 0)
    ...         return v >= 0 and v < 2 ** 15 - 1 \
    ...           and (v & 0x44 in (0x44, 0))
    ... 

    Quick explanation: `0x44` is the hexadecimal representation of the seventh
    and third bit set alone, we use the bitwise and operator to filter out
    these two bits and check if they're either both set or both unset.

    But words pale in comparison to a test!
    >>> VerySpecialInteger == IntegerToken(0)
    True

    All nice and that, but what if we pass one with the third bit set alone?
    >>> VerySpecialInteger == IntegerToken(int("100", 2))
    False

    Ah, nice. What about our 15-bit bound?
    >>> bits = "1000000001000100"
    >>> len(bits)
    16
    >>> VerySpecialInteger == IntegerToken(int(bits, 2))
    False

    On a last note, this machinery works on class-level with all-confusing
    metaclasses and that. This means that the *predicate* function above is
    actually not an instance method, but a *bound classmethod*:

    >>> VerySpecialInteger.predicate
    <bound method MetaTokenType.predicate of <class '__main__.VerySpecialInteger'>>
    """
    __metaclass__ = MetaTokenType
    matching_token_types = ()


sequence_types = (list, JSONList)

map_types = (dict, JSONDict)

valuetoken_type_map = {
    unicode: StringToken,
    str: StringToken,
    int: IntegerToken,
    long: IntegerToken,
    float: DecimalToken
}

token_value_map = {
    True: TrueToken,
    False: FalseToken,
    None: NullToken
}


def token_stream(value, context=None):
    """Parse any number of tokens from *value*, yielding the tokens in
    *context*.
    
    Let's have some examples:
    >>> token_stream(1).next()
    <IntegerToken 1>
    >>> list(token_stream([1, 2]))
    [<SequenceToken>, <IntegerToken 1>, <IntegerToken 2>]

    Stop right there. If the above is how it works, then it surely must get
    misguided in a case like `[[1, 2], 3, 4]` and `[[], 1, 2, 3, 4]`. Let's
    look at it.
    >>> list(token_stream([[1, 2], 3, 4]))
    [<SequenceToken>, <SequenceToken>, <IntegerToken 1>, <IntegerToken 2>, <IntegerToken 3>, <IntegerToken 4>]
    >>> list(token_stream([[], 1, 2, 3, 4]))
    [<SequenceToken>, <SequenceToken>, <IntegerToken 1>, <IntegerToken 2>, <IntegerToken 3>, <IntegerToken 4>]

    By gods! It's flawed! Just look!
    >>> list(token_stream([[1], 2])) == list(token_stream([[1, 2]]))
    False

    You really thought so, didn't you? :-) Alas, tokens know about their
    context, a fact that isn't shown in their representation (because that'd
    mean showing the whole tree all the time, which wouldn't be very nice.)

    So let's look at how dictionaries are represented.
    >>> list(token_stream({u"a": u"b"}))
    [<MappingToken>, <MapKeyToken>, <StringToken u'a'>, <MapValueToken>, <StringToken u'b'>]

    So why is it like that? Because the policy is that whatever comes out as
    context will have gone out as a token, and the context of a key clearly is
    a key token, and the same for values.

    JSON also supports `null`, `true`, `false` and decimal numbers. Let's try
    them all in one go just to be sure.
    >>> list(token_stream([None, True, False, 3.1412]))
    [<SequenceToken>, <NullToken>, <TrueToken>, <FalseToken>, <DecimalToken 3.1412>]

    Here we also see that the tokens represent the JSON view, not Python's. In
    Python, True and False are merely singleton instances of the type `bool`,
    but they're represented as single tokens here.

    """
    typ = type(value)
    if any([typ is seq_type for seq_type in sequence_types]):
        token = SequenceToken(context)
        yield token
        for subvalue in value:
            for subtoken in token_stream(subvalue, context=token):
                yield subtoken
    elif any([typ is map_type for map_type in map_types]):
        token = MappingToken(context)
        yield token
        for subkey, subval in sorted(value.items()):
            # Yield keys.
            key_token = MapKeyToken(token)
            yield key_token
            for subkeytoken in token_stream(subkey, context=key_token):
                yield subkeytoken
            # Yield values.
            val_token = MapValueToken(token)
            yield val_token
            for subvaltoken in token_stream(subval, context=val_token):
                yield subvaltoken
    elif typ in valuetoken_type_map:
        yield valuetoken_type_map[typ](value, context)
    elif value in token_value_map:
        yield token_value_map[value](context)
    elif typ is MetaTokenType:
        yield value
    else:
        raise BadInputValue(value, context=context)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
