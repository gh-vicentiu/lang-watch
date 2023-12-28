import * as THREE from 'https://cdn.skypack.dev/three@0.128.0';
import { scene } from './sceneSetup.js';

// Cube management
let cubeMeshes = {};
let intersected = null; // Renamed to lowercase to avoid naming conflicts

// Texture loader
const loader = new THREE.TextureLoader();
const texture = loader.load('/static/tex.png'); // Update texture path accordingly

// Reset all cubes to default state
export function resetCubes() {
    Object.values(cubeMeshes).forEach(mesh => {
        mesh.material.color.set(0x333333);
        mesh.visible = true;
    });
}

// Load and process cube data
export async function loadCubeData() {
    const response = await fetch('/static/cube_data.json');
    const cubeData = await response.json();

    cubeData.forEach(wordObj => {
        const geometry = new THREE.BoxGeometry(0.02, 0.02, 0.02);
        const material = new THREE.MeshLambertMaterial({ map: texture });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(wordObj.x * 2 - 1, wordObj.y * 2 - 1, wordObj.z * 2 - 1);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData = { word: wordObj.word, connections: wordObj.connections };
        scene.add(mesh);
        cubeMeshes[wordObj.word] = mesh;
    });
}

// Mouse move event handler
export function onMouseMove(event, mouse) {
    event.preventDefault();
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
}

export { cubeMeshes, intersected as INTERSECTED };
