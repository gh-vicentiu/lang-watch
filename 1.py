import json
import numpy as np
import html
import logging
import random

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

try:
    with open('results.json', 'r') as file:
        words_data = json.load(file)
except Exception as e:
    logging.error(f"Error loading JSON: {e}")
    raise

main_cube = Cube(0.5, 0.5, 0.5, 1)

space_connections = list({w for pos in words_data.get("<SPACE>", {}) for w in words_data.get("<SPACE>", {}).get(pos, {}) if w != "<SPACE>"})

cube_data = [{
    'word': '&lt;SPACE&gt;',
    'connections': space_connections,
    'x': 0.5,
    'y': 0.5,
    'z': 0.5
}]

sorted_words = [(word, data) for word, data in sorted(words_data.items(), key=lambda x: x[1].get('0', {}).get('count', 0), reverse=True) if word != "<SPACE>"]

def assign_words_to_cubes(cubes, words):
    cubes = list(cubes)  # Convert generator to list to use len()
    random.shuffle(cubes)  # Randomize the order of cubes
    if not words or not cubes:
        return
    for cube, (word, contexts) in zip(cubes, words):
        encoded_word = html.escape(word)
        connections = {w for pos in contexts for w in contexts[pos] if w != word}
        try:
            cube_data.append({
                'word': encoded_word,
                'connections': list(connections),
                'x': cube.center[0].item(),
                'y': cube.center[1].item(),
                'z': cube.center[2].item()
            })
        except Exception as e:
            logging.error(f"Error processing word '{word}': {e}")

    remaining_words = words[len(cubes):]
    remaining_cubes = [subcube for cube in cubes for subcube in cube.subdivide()]
    assign_words_to_cubes(remaining_cubes, remaining_words)

# Convert the generator to a list before passing it
assign_words_to_cubes(list(main_cube.subdivide()), sorted_words)

try:
    with open('cube_data.json', 'w') as outfile:
        json.dump(cube_data, outfile, indent=4)
except Exception as e:
    logging.error(f"Error saving JSON: {e}")
