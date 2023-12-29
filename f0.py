import collections
import json
import re
import os

def tokenize(text):
    tokens = re.findall(r'\b\w+\b|[,.!?;:]|\s', text.lower())
    tokens = ['<SPACE>' if t.isspace() else t for t in tokens]
    return tokens

def process_project_data(project_id, projects_data, config_path='config.json'):
    start_token = '<START>'
    end_token = '<END>'
    context_range = 16

    project_info = projects_data.get(project_id, {})
    file_name = project_info.get('file', '')
    if not file_name:
        print(f"No file found for project {project_id}")
        return

    file_path = os.path.join('projects', project_id, file_name)
    result_file_path = os.path.join('projects', project_id, 'results.json')

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading file for project {project_id}: {e}")
        return

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

    try:
        with open(result_file_path, 'w') as outfile:
            json.dump(readable_matrices, outfile, indent=4)
        print(f"Processed data for project {project_id} saved to {result_file_path}")
        
        # Update the projects_data with the results file path
        projects_data[project_id]['string-words'] = 'results.json'
        # Save the updated projects_data to config.json
        with open(config_path, 'w') as config_file:
            json.dump({'projects': projects_data}, config_file, indent=4)

        return result_file_path  # Return the path to the results file
    except IOError as e:
        print(f"Error saving results for project {project_id}: {e}")

if __name__ == "__main__":
    # Example usage, replace with actual project_id and projects_data
    project_id = 'example_project_id'
    projects_data = {
        'example_project_id': {
            'file': 'example_file.json'
        }
    }
    process_project_data(project_id, projects_data)
