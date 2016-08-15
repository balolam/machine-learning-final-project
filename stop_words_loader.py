class StopWordsLoader(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def get(self):
        words = []

        f = open(self.file_name, 'r')

        for line in f:
            words.append(line.strip())

        f.close()

        return list(set(words))

from sklearn.feature_extraction import text