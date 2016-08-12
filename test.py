import re

PATTERN_1 = '(?<=\s)([A-Z]\w+(?:\s[A-Z]\w+?)?\s(?:[A-Z]\w+?)?(?=[\s\.\,\;\:]))'
PATTERN_2 = '(?<=\s)([A-Z]\w+\s{1}[A-Z]\w+(?=[\s\.\,\;\:]))'
text = """score=23523

Hello 1234 Maksim Gurov, how are you? What is Your name, Marcusss-sss Paprika Vladimir Ghbhjvghv Gfbfhj. """

print re.findall(PATTERN_2, text)