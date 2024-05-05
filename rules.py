def first_letter_validate(text: str, position: int) -> bool:
    return (position > 0 and text[position - 1] == '\n') or \
           (position >= 2 and not text[position - 1].isalpha() and text[position - 2] == '\n')


def letter_after_end_sentence_validate(text: str, position: int) -> bool:
    return (position >= 2 and
            text[position - 1].isspace() and
            text[position - 2] in ['!', '.', '?', '”'])


def pronoun_validate(text: str, position: int) -> bool:
    return (position != 0 and
            position < len(text) - 1 and
            not text[position - 1].isalpha() and
            not text[position + 1].isalpha())
