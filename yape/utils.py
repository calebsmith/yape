from collections import Iterable


def is_non_string_iterable(item):
    """
    Returns True if the given item is an Iterable and is not a str, unicode,
    bytes, or bytearray; otherwise returns False.
    """
    is_iterable = isinstance(item, Iterable)
    is_string_type = isinstance(item, (str, unicode, bytes, bytearray))
    return is_iterable and not is_string_type


def validate_data_against_schema(data, schema):
    """
    Given `data`, and a `schema`, returns True if the data conforms to the
    schema provided; otherwise returns False
    """
    # Dictionaries
    if hasattr(schema, 'keys'):
        for key in schema:
            if not key in data:
                return False
            if not validate_data_against_schema(data[key], schema[key]):
                return False
    # List
    elif is_non_string_iterable(schema):
        if is_non_string_iterable(data) and not hasattr(data, 'keys'):
            for value in data:
                if not validate_data_against_schema(value, schema):
                    return False
        else:
            for key in schema:
                if not validate_data_against_schema(data, key):
                    return False
    # Everything else, probably strings and numbers
    else:
        if not schema in data:
            return False
    return True


def word_wrap(sentence, limit, hyphenate=True):
    """
    A simple word wrap utility function.

    Given a sentence and a limit, return a list of strings such that no string
    is longer than the `limit`. If a single word is longer than the limit, it
    is made into two or more strings in the list, with hyphens appended at the
    end of all but the last of these strings.
    """
    if limit < 1:
        return ['']
    elif limit == 1:
        return list(sentence)
    results = []
    current = ''
    limit_offset = 1 if hyphenate else 0
    for word in sentence.split(' '):
        separator = ' ' if current else ''
        # If existing phrase, a space, and a new word will fit
        if len(current) + len(word) + len(separator) <= limit:
            current += separator + word
        else:
            if current:
                results.append(current)
            if (len(word) <= limit):
                current = word
            # Word is longer than the limit, hyphenate
            else:
                end = limit - limit_offset
                for start in xrange(0, len(word), end):
                    current = word[start:start + end]
                    # If this is not the last iteration
                    if start + end < len(word):
                        if hyphenate:
                            current += '-'
                        results.append(current)
    if current:
        results.append(current)
    return results
