import * as THREE from 'https://cdn.skypack.dev/three@0.128.0';
import { scene } from './sceneSetup.js';

let cubeMeshes = {};
let intersected = null;

const loader = new THREE.TextureLoader();
const texture = loader.load('/static/tex.png');

export function resetCubes() {
    Object.values(cubeMeshes).forEach(mesh => {
        mesh.material.color.set(0x333333);
        mesh.visible = true;
    });
}

export async function loadCubeData(cubeDataPath) {
    let cubeData;
    try {
        const response = await fetch(cubeDataPath);
        cubeData = await response.json();
    } catch (error) {
        console.error('Error loading cube data:', error);
        return;  // Early return if fetching or parsing failed
    }

    // Only proceed if cubeData is successfully loaded
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

export function onMouseMove(event, mouse) {
    event.preventDefault();
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
}

export { cubeMeshes, intersected as INTERSECTED };
