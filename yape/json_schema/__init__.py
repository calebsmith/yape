"""
json_schema module is written by Ludvig Ericson and is available on Pypi.

The code in this module represents a fork of this library for this sake
of some light customizations

JSON schema defintion & validation

Example:

>>> from yape.json_schema import SchemaCollection, AnyString, AnyInteger
>>> class Foo(SchemaCollection):
...     abc = [u"hello", {u"world": AnyString}]
...     bla = [u"hello", {u"world": AnyInteger}]
...     bli = [u"foo", AnyInteger, u"bar"]
... 
>>> Foo.abc  # doctest: +ELLIPSIS
<yape.json_schema.schema.Schema object at ...
>>> Foo.match_to_schema([u"hello", {u"world": u"Hey"}])
'abc'
>>> Foo.match_to_schema([u"hello", {u"world": 123}])
'bla'
>>> Foo.match_to_schema([u"hey there", {u"world": 123}])
>>> Foo.match_to_schema([u"foo", 1337, u"bar"])
'bli'

See json_schema.tokens for more.
"""

from yape.json_schema.defs import *
from yape.json_schema.schema import SchemaCollection, Schema


if __name__ == "__main__":
    import doctest
    doctest.testmod()
