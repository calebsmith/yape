#!/usr/bin/env python

from unittest import TestLoader, TextTestRunner


def run(verbosity=2):
    suite = TestLoader().loadTestsFromName('tests')
    TextTestRunner(verbosity=verbosity).run(suite)


if __name__ == '__main__':
    run()
