from math import log2, ceil
from encoders import ArithmeticEncoder, DeltaEncoder, HuffmanEncoder
from model import ContextModel
from rules import first_letter_validate, letter_after_end_sentence_validate, pronoun_validate

rules = [first_letter_validate, letter_after_end_sentence_validate, pronoun_validate]


def complies_with_rules(text, position):
    return any(validate(text, position) for validate in rules)


def get_entropy(bytes_array):
    probabilities = [0] * 256
    for byte in bytes_array:
        probabilities[byte] += 1
    probabilities = [p / len(bytes_array) for p in probabilities if p != 0]
    return -sum(p * log2(p) for p in probabilities)


def get_context_models(text, k):
    context_models = {}

    def update_context_model(substring, next_character):
        if substring not in context_models:
            context_models[substring] = ContextModel(substring)
        context_models[substring].add_occurrence(next_character)

    for i in range(len(text)):
        substring = ''
        update_context_model(substring, text[i].lower())
        for j in range(i, min(i + k, len(text))):
            substring += text[j].lower()
            if j < len(text) - 1:
                update_context_model(substring, text[j + 1].lower())
    return context_models


def get_size(models):
    size = 0
    for model in models.values():
        size += len(model.string)
        size += 4
        size += model.characters_encountered_with_left_text_count * (1 + 4)
    return size


def main():
    k = 3
    with open('11-22-63.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    byte_size = 8
    positions = [0] * ceil(len(text) / byte_size)
    for i in range(len(text)):
        index = i // byte_size
        if text[i].isupper() and not complies_with_rules(text, i):
            positions[index] += 1 << (byte_size - 1 - i % byte_size)

    entropy = get_entropy(positions)
    print(f"Capital letters byte array entropy: {entropy}")

    ArithmeticEncoder(12).encode(bytes(positions))
    DeltaEncoder().encode(bytes(positions))
    HuffmanEncoder().encode(bytes(positions))

    context_models = get_context_models(text, k)
    print(f"ContextModels size {get_size(context_models)} bytes")


if __name__ == "__main__":
    main()
