#!/usr/bin/python

class JSONDict(dict):
    """A dictionary for storing JSON data that can be weak referenced"""

    def __init__(self, json_data):
        self.update(json_data)


class JSONList(list):
    """A list for storing JSON data that can be weak referenced"""

    def __init__(self, json_data):
        self.extend(json_data)

