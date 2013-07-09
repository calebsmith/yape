from unittest import TestCase

from yape.utils import (is_non_string_iterable, validate_data_against_schema,
    word_wrap)


class IsNonStringIterable(TestCase):

    def test_strs_are_false(self):
        self.assertFalse(any(map(is_non_string_iterable,
            [3, 'str', u'unicode', b'bytes', bytearray('bytarray')]
        )))

    def test_list_things_are_true(self):
        self.assertTrue(all(map(is_non_string_iterable,
            [[], (), set([]), frozenset([]), {}]
        )))


class WordWrapTestCase(TestCase):

    def test_hyphenate_multiple_words(self):
        sentence = 'antidisestablishmentarianism is how those folkses rollll'
        expected = [
            'anti-', 'dise-', 'stab-', 'lish-', 'ment-', 'aria-', 'nism',
            'is', 'how', 'those', 'folk-', 'ses', 'roll-', 'll',
        ]
        self.assertEqual(expected, word_wrap(sentence, 5))

    def test_no_hyphenate(self):
        sentence = 'antidisestablishmentarianism is how those folkses rollll'
        expected = [
            'antid', 'isest', 'ablis', 'hment', 'arian', 'ism', 'is', 'how',
            'those', 'folks', 'es', 'rolll', 'l',
        ]
        self.assertEqual(expected, word_wrap(sentence, 5, hyphenate=False))

    def test_limit_0(self):
        sentence = 'this might break with the limit at 0'
        expected = ['']
        self.assertEqual(expected, word_wrap(sentence, 0))

    def test_limit_1(self):
        sentence = 'this might break with the limit at 1'
        expected = list(sentence)
        self.assertEqual(expected, word_wrap(sentence, 1))

    def test_limit_2_hyphenated(self):
        sentence = 'this will be long'
        expected = [
            't-', 'h-', 'i-', 's', 'w-', 'i-', 'l-', 'l', 'be', 'l-', 'o-',
            'n-', 'g',
        ]
        self.assertEqual(expected, word_wrap(sentence, 2))

    def test_multple_words_per_line(self):
        sentence = 'this has multiple words when that is possible'
        expected = [
            'this has', 'multiple', 'words', 'when that', 'is', 'possible'
        ]
        self.assertEqual(expected, word_wrap(sentence, 9))

