import collections
import json
import re

def tokenize(text):
    # Lowercase the text and then split into words, treating punctuation and spaces as separate tokens
    tokens = re.findall(r'\b\w+\b|[,.!?;:]|\s', text.lower())
    # Replace spaces with a special <SPACE> token
    tokens = ['<SPACE>' if t.isspace() else t for t in tokens]
    return tokens

def main():
    start_token = '<START>'
    end_token = '<END>'
    context_range = 16

    with open('joey.json', 'r') as file:
        data = json.load(file)

    all_matrices = collections.defaultdict(lambda: {i: collections.Counter() for i in range(-context_range, context_range + 1)})

    for entry in data:
        for text_type in ['question', 'answer']:
            words = [start_token] * context_range + tokenize(entry[text_type]) + [end_token] * context_range
            for i, word in enumerate(words):
                for offset in range(-context_range, context_range + 1):
                    if 0 <= i + offset < len(words):
                        adjacent_word = words[i + offset]
                        all_matrices[word][offset][adjacent_word] += 1

    readable_matrices = {
        word: {pos: dict(context.most_common(32)) for pos, context in contexts.items()}
        for word, contexts in all_matrices.items()
    }

    with open('results.json', 'w') as outfile:
        json.dump(readable_matrices, outfile, indent=4)

if __name__ == "__main__":
    main()
