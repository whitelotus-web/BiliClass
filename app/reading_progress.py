"""Remember completed speech chunks within the currently displayed slide."""


class ReadingProgress:
    def __init__(self):
        self.slide = None
        self.position = None
        self.completed = {}
        self.spoken = {}
        self.previous = {}

    def enter(self, slide, position=None):
        if slide != self.slide:
            self.previous = self.spoken if type(position) is int and self.position == position - 1 else {}
            self.spoken = {}
            self.position = position
            self.slide = slide
            self.completed.clear()

    def reset(self):
        self.slide = None
        self.position = None
        self.completed.clear()
        self.spoken = {}
        self.previous = {}

    def choose(self, language, items, *, titles=()):
        done = self.completed.get(language, set())
        repeated = set(titles) & self.previous.get(language, set())
        self.spoken.setdefault(language, set()).update(repeated)
        return [item for item in items if item[0] not in done and item[1] not in repeated]

    def finish(self, slide, language, items):
        if slide == self.slide:
            self.completed.setdefault(language, set()).update(item[0] for item in items)
            self.spoken.setdefault(language, set()).update(item[1] for item in items)
