class ContextModel:
    def __init__(self, string: str):
        self.string = string
        self.occurrences_counter = 0
        self.characters_encountered_with_left_text = {}

    def add_occurrence(self, next_character: str):
        self.occurrences_counter += 1
        if next_character not in self.characters_encountered_with_left_text:
            self.characters_encountered_with_left_text[next_character] = 0
        self.characters_encountered_with_left_text[next_character] += 1

    @property
    def characters_encountered_with_left_text_count(self):
        return len(self.characters_encountered_with_left_text)
