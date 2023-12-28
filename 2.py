import collections

def main():
    # Load and clean the text
    with open('joey_text.txt', 'r') as file:
        text = file.read().replace('A: ', '').replace('Q: ', '')

    # Split the text into words
    words = text.split()

    # Count the occurrences of each word
    word_counts = collections.Counter(words)

    # Find the 30th most common word
    thirtieth_most_common_word, _ = word_counts.most_common(30)[29]

    # Initialize dictionaries to hold the words that appear before and after the 30th most common word
    before_words = collections.defaultdict(collections.Counter)
    after_words = collections.defaultdict(collections.Counter)

    # Iterate through the words to collect the context of the 30th most common word
    for i in range(len(words)):
        if words[i] == thirtieth_most_common_word:
            for j in range(max(0, i-10), i):
                position = f'-{i - j}'
                before_words[position][words[j]] += 1

            for j in range(i + 1, min(i + 11, len(words))):
                position = f'+{j - i}'
                after_words[position][words[j]] += 1

    # Find the top 10 least used words in the context of the 30th most common word
    least_used_before = {pos: list(collections.Counter(before).most_common()[:-11:-1]) for pos, before in before_words.items()}
    least_used_after = {pos: list(collections.Counter(after).most_common()[:-11:-1]) for pos, after in after_words.items()}

    # Prepare the matrix for the 30th most common word with the top 10 least used words for each position from -10 to +10
    matrix = {
        'word': thirtieth_most_common_word,
        '-10': least_used_before['-10'],
        '-9': least_used_before['-9'],
        '-8': least_used_before['-8'],
        '-7': least_used_before['-7'],
        '-6': least_used_before['-6'],
        '-5': least_used_before['-5'],
        '-4': least_used_before['-4'],
        '-3': least_used_before['-3'],
        '-2': least_used_before['-2'],
        '-1': least_used_before['-1'],
        '+1': least_used_after['+1'],
        '+2': least_used_after['+2'],
        '+3': least_used_after['+3'],
        '+4': least_used_after['+4'],
        '+5': least_used_after['+5'],
        '+6': least_used_after['+6'],
        '+7': least_used_after['+7'],
        '+8': least_used_after['+8'],
        '+9': least_used_after['+9'],
        '+10': least_used_after['+10'],
    }

    # Print the matrix
    for pos, words in matrix.items():
        print(f'{pos}: {words}')

if __name__ == "__main__":
    main()
