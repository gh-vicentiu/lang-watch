from flask import Flask, render_template, request, redirect, url_for, flash
import json
import uuid
import os
import shutil
from f0 import process_project_data 

app = Flask(__name__)
app.secret_key = '<tZ\x98\x8f\xf3\xc2mt\xe1\x97\xff\xe7Q4\xd9\x810\xfb\xe3(`\xd5<'

# Helper function to load data from a file
def load_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

# Helper function to save data to a file
def save_data(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)



# Load initial data
config_data = load_data('config.json')
projects_data = config_data.get('projects', {})
# Load data from the respective JSON files
words_data = load_data('results.json')
qa_data = load_data('joey.json')
words_list = sorted(words_data.keys())

def create_project_folder(project_id):
    os.makedirs(f'projects/{project_id}', exist_ok=True)

def calculate_project_counters(project_id):
    try:
        # Access the global projects_data
        global projects_data

        # Retrieve the file name for the given project_id
        project_info = projects_data.get(project_id, {})
        file_name = project_info.get('file', '')
        if not file_name:
            return 0, 0  # If there's no file associated, return 0

        # Construct the file path and load the data
        file_path = f"projects/{project_id}/{file_name}"
        qa_data = load_data(file_path)
        total_qa_pairs = len(qa_data)

        # Initialize total_words to 0
        total_words = 0

        # Count words in the 'answer' field of each QA pair
        for item in qa_data:
            if 'answer' in item and isinstance(item['answer'], str):
                total_words += len(item['answer'].split())

        return total_words, total_qa_pairs
    except (FileNotFoundError, json.JSONDecodeError):
        # Return 0,0 if file doesn't exist or is improperly formatted
        return 0, 0  

# Routes
@app.route('/')
def index():
    global projects_data
    for project_id, details in projects_data.items():
        # Update to use the new function signature
        total_words, total_qa_pairs = calculate_project_counters(project_id)
        projects_data[project_id].update({
            'total_words': total_words,
            'total_qa_pairs': total_qa_pairs
        })
    return render_template('index.html', projects=projects_data)

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form.get('name').strip()
        description = request.form.get('description').strip()

        # Generate a unique ID and create folder for the project
        project_id = str(uuid.uuid4())
        create_project_folder(project_id)

        # Update the projects data
        projects_data[project_id] = {
            'name': project_name,
            'description': description,
            'file': ''  # Initially, no file is uploaded
        }

        # Save updated projects data
        save_data('config.json', config_data)
        flash('Project added successfully!', 'success')

        return redirect(url_for('index'))

    return render_template('add_project.html')


@app.route('/upload/<project_id>', methods=['GET', 'POST'])
def upload_file(project_id):
    if request.method == 'GET':
        project = projects_data.get(project_id, {})
        if not project:
            flash("Project not found!", "error")
            return redirect(url_for('index'))
        return render_template('upload.html', project=project, project_id=project_id)

    if request.method == 'POST':
        # Check if a file has been uploaded
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            # Rename the file to 'project_id.json'
            filename = f"{project_id}.json"
            file_path = os.path.join(f'projects/{project_id}', filename)
            file.save(file_path)
            
            # Update the project data
            projects_data[project_id]['file'] = filename
            projects_data[project_id]['file_exists'] = os.path.exists(file_path)
            
            # Save the updated data to the config file
            save_data('config.json', config_data)
            flash('File uploaded and renamed successfully!', 'success')
            
            # Redirect to the index page after successful upload
            return redirect(url_for('index'))

    return render_template('upload.html', project=projects_data.get(project_id, {}), project_id=project_id)



@app.route('/edit_project/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if request.method == 'POST':
        # Update the project details
        projects_data[project_id]['name'] = request.form.get('name').strip()
        projects_data[project_id]['description'] = request.form.get('description').strip()
        projects_data[project_id]['file'] = request.form.get('file').strip()

        # Save updated projects data
        save_data('config.json', config_data)

        return redirect(url_for('index'))

    project = projects_data.get(project_id, {})
    return render_template('edit_project.html', project_id=project_id, project=project)

@app.route('/delete_project/<project_id>')
def delete_project(project_id):
    # Remove the project from the projects_data
    if project_id in projects_data:
        projects_data.pop(project_id, None)

        # Construct the path to the project's directory
        project_dir = os.path.join('projects', project_id)

        # Check if the directory exists
        if os.path.isdir(project_dir):
            try:
                # Remove the directory and all its contents
                shutil.rmtree(project_dir)
                flash(f'Project {project_id} and all associated files have been deleted.', 'success')
            except Exception as e:
                # Handle exceptions that might occur, e.g., issues with file permissions
                flash(f'An error occurred while attempting to delete project {project_id}: {e}', 'error')

        # Save updated projects data
        save_data('config.json', config_data)
    else:
        # If the project doesn't exist, flash an error message
        flash(f'Project {project_id} does not exist.', 'error')

    # Redirect to the index page
    return redirect(url_for('index'))

@app.route('/process_project/<project_id>')
def process_project_route(project_id):
    global projects_data
    config_path = 'config.json'  # Path to your config.json

    if project_id in projects_data:
        result_path = process_project_data(project_id, projects_data, config_path)
        if result_path:
            flash(f'Project processed successfully. Results saved to {result_path}', 'success')
        else:
            flash('Failed to process project', 'error')
    else:
        flash('Project not found', 'error')
    
    return redirect(url_for('index'))

@app.route('/words/<project_id>', methods=['GET', 'POST'])
def words(project_id):
    project = projects_data.get(project_id)
    if not project:
        flash("Project not found!", "error")
        return redirect(url_for('index'))

    # Use 'string-words' to get the results file name
    file_name = project.get('string-words', '')
    if not file_name:
        flash("Results file name not specified in project!", "error")
        return redirect(url_for('index'))

    file_path = os.path.join('projects', project_id, file_name)
    if not os.path.isfile(file_path):
        flash(f"Project file not found at {file_path}!", "error")
        return redirect(url_for('index'))

    # Load the data for the specific project
    project_data = load_data(file_path)
    words_list = sorted(project_data.keys())

    default_word = 'hey'
    current_word = request.args.get('word', default_word).lower()

    if request.method == 'POST':
        current_word = request.form.get('navigate', request.form.get('word', default_word)).strip().lower()

    if current_word not in words_list:
        current_word = words_list[0]

    context = project_data.get(current_word, {})
    positions = range(-16, 17)
    context_with_positions = {str(pos): sorted(context.get(str(pos), {}).items(), key=lambda x: x[1], reverse=True) for pos in positions}

    current_index = words_list.index(current_word)
    next_word = words_list[(current_index + 1) % len(words_list)] if (current_index + 1) < len(words_list) else words_list[0]
    prev_word = words_list[(current_index - 1) % len(words_list)] if current_index > 0 else words_list[-1]

    word_counts = [(key, project_data[key]['0'].get(key, 0)) for key in words_list]
    word_counts_sorted = sorted(word_counts, key=lambda x: x[1], reverse=True)

    return render_template('words.html', project_id=project_id, project=project, word=current_word,
                           next_word=next_word, prev_word=prev_word, positions=positions,
                           context=context_with_positions, keys=words_list, word_counts_sorted=word_counts_sorted)


@app.route('/qa/<project_id>', methods=['GET', 'POST'])
def edit_qa(project_id):
    # Retrieve the project's information from the global projects_data
    project = projects_data.get(project_id)
    if not project:
        flash("Project not found!", "error")
        return redirect(url_for('index'))

    # Determine the file path for the project's Q&A data
    file_name = project.get('file', '')
    if not file_name:
        flash("Q&A file name not specified in project!", "error")
        return redirect(url_for('index'))

    file_path = os.path.join('projects', project_id, file_name)
    if not os.path.isfile(file_path):
        flash(f"Q&A file not found at {file_path}!", "error")
        return redirect(url_for('index'))

    # Load the Q&A data for the specified project
    qa_data = load_data(file_path)

    if request.method == 'POST':
        # Update the Q&A data based on the form input
        index = int(request.form.get('index'))
        if 0 <= index < len(qa_data):
            qa_data[index]['question'] = request.form.get('question').strip()
            qa_data[index]['answer'] = request.form.get('answer').strip()

            # Save the updated Q&A data back to the project's file
            with open(file_path, 'w') as file:
                json.dump(qa_data, file, indent=4)
        else:
            flash(f"Invalid Q&A index: {index}", "error")

        return redirect(url_for('edit_qa', project_id=project_id))

    # Pass the project and qa_pairs to the template
    return render_template('qa.html', project_id=project_id, project=project, qa_pairs=enumerate(qa_data))

@app.route('/cube/<project_id>')
def cube(project_id):
    # Retrieve the project's information from the global projects_data
    project = projects_data.get(project_id)
    if not project:
        flash("Project not found!", "error")
        return redirect(url_for('index'))

    # Determine the file path for the project's word data
    file_name = project.get('string-words', '')
    if not file_name:
        flash("Word data file name not specified in project!", "error")
        return redirect(url_for('index'))

    file_path = os.path.join('projects', project_id, file_name)
    if not os.path.isfile(file_path):
        flash(f"Word data file not found at {file_path}!", "error")
        return redirect(url_for('index'))

    # Load the word data for the specified project
    words_data = load_data(file_path)
    words_list = sorted(words_data.keys())

    # Assuming words_data is sorted by frequency
    word_counts = [(key, words_data[key]['0'].get(key, 0)) for key in words_list]
    word_counts_sorted = sorted(word_counts, key=lambda x: x[1], reverse=True)

    # Prepare data for the cube, starting with '<space>' in the center
    cube_data = ["<space>"] + [word for word, count in word_counts_sorted]

    # Pass the project and cube_data to the template
    return render_template('cube.html', project_id=project_id, project=project, cube_data=cube_data)



if __name__ == '__main__':
    app.run(debug=True)
