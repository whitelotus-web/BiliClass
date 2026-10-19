"""Remember completed speech chunks within the currently displayed slide."""


class ReadingProgress:
    def __init__(self):
        self.slide = None
        self.completed = {}

    def enter(self, slide):
        if slide != self.slide:
            self.slide = slide
            self.completed.clear()

    def reset(self):
        self.slide = None
        self.completed.clear()

    def choose(self, language, items):
        done = self.completed.get(language, set())
        remaining = [item for item in items if item[0] not in done]
        return remaining or items  # Nothing new is visible: replay what is on screen.

    def finish(self, slide, language, items):
        if slide == self.slide:
            self.completed.setdefault(language, set()).update(item[0] for item in items)
