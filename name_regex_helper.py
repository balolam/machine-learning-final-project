# coding=utf-8
import re
# http://stackoverflow.com/questions/2385701/regular-expression-for-first-and-last-name
NAME_PATTERN_1 = "/\b([A-Z]{1}[a-z]{1,30}[- ]{0,1}|[A-Z]{1}[- \']{1}[A-Z]{0,1}[a-z]{1,30}[- ]{0,1}|[a-z]{1,2}[ -\']{1}[A-Z]{1}[a-z]{1,30}){2,5}/"
class NameRegexHelper(object):
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def has(self, text):
        return len() != 0
