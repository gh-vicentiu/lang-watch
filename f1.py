import json
import numpy as np
import html
import logging
import random
import os

# Setup basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Cube:
    def __init__(self, x, y, z, size):
        self.center = np.array([x, y, z], dtype=float)
        self.size = float(size)

    def subdivide(self):
        offset = np.array([self.size / 4] * 3, dtype=float)
        new_size = self.size / 2
        for dx in (-1, 1):
            for dy in (-1, 1):
                for dz in (-1, 1):
                    yield Cube(
                        self.center[0] + dx * offset[0],
                        self.center[1] + dy * offset[1],
                        self.center[2] + dz * offset[2],
                        new_size
                    )

def assign_words_to_cubes(cubes, words, cube_data):
    logging.debug(f"Assigning {len(words)} words to {len(cubes)} cubes.")
    cubes = list(cubes)  # Convert generator to list to use len()
    random.shuffle(cubes)  # Randomize the order of cubes
    if not words or not cubes:
        return
    for cube, (word, contexts) in zip(cubes, words):
        encoded_word = html.escape(word)
        connections = {w for pos in contexts for w in contexts.get(pos, {}) if w != word}
        try:
            cube_data.append({
                'word': encoded_word,
                'connections': list(connections),
                'x': cube.center[0].item(),
                'y': cube.center[1].item(),
                'z': cube.center[2].item()
            })
            logging.debug(f"Processed word: {word}")
        except Exception as e:
            logging.error(f"Error processing word '{word}': {e}")

    remaining_words = words[len(cubes):]
    if remaining_words:
        logging.debug(f"{len(remaining_words)} words remaining, subdividing cubes for assignment.")
        remaining_cubes = [subcube for cube in cubes for subcube in cube.subdivide()]
        assign_words_to_cubes(remaining_cubes, remaining_words, cube_data)

def process_cube_data(project_id, projects_data):
    try:
        project_info = projects_data.get(project_id, {})
        results_file = project_info.get('string-words', '')
        input_path = os.path.join('projects', project_id, results_file)
        output_path = os.path.join('projects', project_id, 'cube_data.json')

        if not os.path.isfile(input_path):
            logging.error(f"Input file not found: {input_path}")
            return False

        with open(input_path, 'r') as file:
            words_data = json.load(file)

        # Start with a main cube
        main_cube = Cube(0.5, 0.5, 0.5, 1)
        cube_data = []

        # Extract and process <SPACE> first
        space_connections = list({w for pos in words_data.get("<SPACE>", {}) for w in words_data.get("<SPACE>", {}).get(pos, {}) if w != "<SPACE>"})
        cube_data.append({
            'word': '&lt;SPACE&gt;',
            'connections': space_connections,
            'x': main_cube.center[0].item(),
            'y': main_cube.center[1].item(),
            'z': main_cube.center[2].item()
        })

        # Process remaining words
        sorted_words = [(word, data) for word, data in sorted(words_data.items(), key=lambda x: x[1].get('0', {}).get('count', 0), reverse=True) if word != "<SPACE>"]
        assign_words_to_cubes(list(main_cube.subdivide()), sorted_words, cube_data)

        with open(output_path, 'w') as outfile:
            json.dump(cube_data, outfile, indent=4)

        logging.info(f"Cube data processed successfully for project {project_id} with {len(cube_data)} entries.")
        return True

    except Exception as e:
        logging.error(f"Error processing cube data for project {project_id}: {e}")
        return False

if __name__ == "__main__":
    # Example usage, replace with actual project_id and projects_data
    project_id = 'example_project_id'
    projects_data = {
        'example_project_id': {
            'string-words': 'example_results.json'
        }
    }
    process_cube_data(project_id, projects_data)
