import * as THREE from 'https://cdn.skypack.dev/three@0.128.0';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.128.0/examples/jsm/controls/OrbitControls.js';
import { scene, camera, renderer, controls, light, ambientLight, raycaster, mouse } from './sceneSetup.js';
import { cubeMeshes, resetCubes, loadCubeData, onMouseMove, INTERSECTED } from './cubeManager.js';

// Attach renderer to the page
document.getElementById('cube-container').appendChild(renderer.domElement);

// Load and process cube data using the dynamic path
loadCubeData(cubeDataPath).then(() => {  // Pass the cubeDataPath to the loadCubeData function
    camera.position.z = 2;
    animate();
}).catch(error => {
    console.error('Error loading cube data:', error);
});

let currentlyIntersected = INTERSECTED; // Use a local variable for tracking

// Animation loop function
function animate() {
    requestAnimationFrame(animate);
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(Object.values(cubeMeshes));
    const infoPanel = document.getElementById('info-panel');
    const cubeNameElement = document.getElementById('cube-name');

    // Check if any checkbox is checked
    const isAnyCheckboxChecked = document.getElementById('common-connections').checked || document.getElementById('common-connections-color').checked;

    if (intersects.length > 0) {
        const firstIntersectedObject = intersects[0].object;
        if (currentlyIntersected !== firstIntersectedObject) {
            if (!isAnyCheckboxChecked) {
                resetCubes();
                currentlyIntersected = firstIntersectedObject;
                currentlyIntersected.material.color.set(0xffa500);
                currentlyIntersected.visible = true;
                currentlyIntersected.userData.connections.forEach(word => {
                    if (cubeMeshes[word]) {
                        cubeMeshes[word].material.color.set(0xffa500);
                        cubeMeshes[word].visible = true;
                    }
                });
            }

            // Update the info panel with the name of the hovered cube
            cubeNameElement.textContent = firstIntersectedObject.userData.word || 'Unknown';
            infoPanel.style.display = 'block';
        }
    } else {
        currentlyIntersected = null;
        // Hide the info panel when not hovering over any cube
        infoPanel.style.display = 'none';
    }

    controls.update();
    renderer.render(scene, camera);
}

// Event Listeners for mouse movement
window.addEventListener('mousemove', (event) => onMouseMove(event, mouse));

// Function to calculate common connections
function getCommonConnections(searchTerms, commonConnectionsOnly) {
    if (!commonConnectionsOnly) {
        return new Set([].concat(...searchTerms.map(term => cubeMeshes[term]?.userData.connections || [])));
    } else {
        const allConnections = searchTerms.map(term => new Set(cubeMeshes[term]?.userData.connections || []));
        return allConnections.reduce((common, set) => new Set([...common].filter(word => set.has(word))), new Set([...allConnections[0]]));
    }
}

// Event listener for the input field to handle search terms and update connection lists
document.getElementById('word-search').addEventListener('input', event => {
    resetCubes();  // Reset cubes to their default state each time the input changes

    const inputText = event.target.value.toLowerCase();
    const searchTerms = inputText.split(/\s+/).filter(term => term.length > 1 || cubeMeshes[term]);
    const isCommonConnectionsChecked = document.getElementById('common-connections').checked;

    // Clear the lists if the input is empty
    const activeConnectionsList = document.getElementById('active-connections-list');
    const commonConnectionsWords = document.getElementById('common-connections-words');
    if (inputText.trim() === '') {
        activeConnectionsList.textContent = 'None';
        commonConnectionsWords.textContent = 'None';
        return;  // Skip further processing if the input is empty
    }

    // Calculate all connections and common connections
    const allConnections = getCommonConnections(searchTerms, false);
    const commonConnections = getCommonConnections(searchTerms, true);

    // Update the active connections list
    activeConnectionsList.textContent = Array.from(allConnections).join(', ');

    // Update the common connections list
    commonConnectionsWords.textContent = Array.from(commonConnections).join(', ');


    Object.values(cubeMeshes).forEach(mesh => {
        const word = mesh.userData.word.toLowerCase();
        if (searchTerms.includes(word)) {
            mesh.material.color.set(0xffa500); // Color for direct matches
            mesh.visible = true;
        } else if (allConnections.has(word)) {
            // If the cube is part of all connections, it remains visible but only colored if it's a common connection
            mesh.visible = true;
            if (isCommonConnectionsChecked && commonConnections.has(word)) {
                mesh.material.color.set(0xff0000); // Color for common connections
            } else {
                mesh.material.color.set(0xcdcdcd); // Different color for all other connections
            }
        } else {
            // If the cube is not part of the connections, its visibility is determined by the 'common-connections-color' checkbox
            mesh.visible = document.getElementById('common-connections-color').checked ? false : true;
        }
    });
});

// Event listeners for checkboxes - trigger input event for word-search to update connections lists
document.getElementById('common-connections').addEventListener('change', () => {
    document.getElementById('word-search').dispatchEvent(new Event('input'));
});

document.getElementById('common-connections-color').addEventListener('change', () => {
    document.getElementById('word-search').dispatchEvent(new Event('input'));
});
