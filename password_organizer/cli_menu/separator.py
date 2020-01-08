class Separator(object):
    line = '-' * 15

    def __init__(self, line=None):
        if line:
            self.line = line

    def __str__(self):
        return self.line
