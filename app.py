from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Helper function to load data from a file
def load_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

# Load data from the respective JSON files
words_data = load_data('results.json')
qa_data = load_data('joey.json')
words_list = sorted(words_data.keys())

@app.route('/')
def index():
    total_words = len(words_data)
    total_qa_pairs = len(qa_data)
    return render_template('index.html', total_words=total_words, total_qa_pairs=total_qa_pairs)

@app.route('/words', methods=['GET', 'POST'])
def words():
    default_word = 'hey'
    current_word = request.args.get('word', default_word).lower()

    if request.method == 'POST':
        current_word = request.form.get('navigate', request.form.get('word', default_word)).strip().lower()

    if current_word not in words_list:
        current_word = words_list[0]

    context = words_data.get(current_word, {})
    positions = range(-16, 17)
    context_with_positions = {pos: sorted(context.get(str(pos), {}).items(), key=lambda x: x[1], reverse=True) for pos in positions}

    current_index = words_list.index(current_word)
    next_word = words_list[(current_index + 1) % len(words_list)]
    prev_word = words_list[(current_index - 1) % len(words_list)]

    word_counts = [(key, words_data[key]['0'].get(key, 0)) for key in words_list]
    word_counts_sorted = sorted(word_counts, key=lambda x: x[1], reverse=True)

    return render_template('words.html', word=current_word, next_word=next_word, prev_word=prev_word,
                           positions=positions, context=context_with_positions, keys=words_list,
                           word_counts_sorted=word_counts_sorted)


@app.route('/qa', methods=['GET', 'POST'])
def edit_qa():
    global qa_data

    if request.method == 'POST':
        index = int(request.form.get('index'))
        qa_data[index]['question'] = request.form.get('question').strip()
        qa_data[index]['answer'] = request.form.get('answer').strip()

        with open('joey.json', 'w') as file:
            json.dump(qa_data, file, indent=4)

        qa_data = load_data('joey.json')
        return redirect(url_for('edit_qa'))

    return render_template('qa.html', qa_pairs=enumerate(qa_data))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    pass

@app.route('/cube')
def cube():
    # Assuming words_data is sorted by frequency
    word_counts = [(key, words_data[key]['0'].get(key, 0)) for key in words_list]
    word_counts_sorted = sorted(word_counts, key=lambda x: x[1], reverse=True)

    # Prepare data for the cube, starting with '<space>' in the center
    cube_data = ["<space>"] + [word for word, count in word_counts_sorted]

    return render_template('cube.html', cube_data=cube_data)


if __name__ == '__main__':
    app.run(debug=True)
