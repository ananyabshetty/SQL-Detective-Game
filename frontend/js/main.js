/**
 * SQL Detective Game - Main Entry Point
 * Initializes Three.js scene and manages game state
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DetectiveRoom } from './scene/DetectiveRoom.js';
import { api } from './api/gameAPI.js';

// ============================================
// Game State
// ============================================
const gameState = {
    currentLevel: 1,
    completedLevels: [],
    levelData: null,
    allLevels: [],
    isLoading: false,
    soundEnabled: true
};

// ============================================
// Three.js Setup
// ============================================
let scene, camera, renderer, controls;
let detectiveRoom;
let raycaster, mouse;
let hoveredObject = null;

// DOM Elements
const loadingScreen = document.getElementById('loading-screen');
const gameCanvas = document.getElementById('game-canvas');
const currentLevelEl = document.getElementById('current-level');
const levelTitleEl = document.getElementById('level-title');
const interactionHint = document.getElementById('interaction-hint');

// Panels
const storyPanel = document.getElementById('story-panel');
const evidencePanel = document.getElementById('evidence-panel');
const sqlEditorPanel = document.getElementById('sql-editor-panel');

// SQL Editor elements
const sqlInput = document.getElementById('sql-input');
const lineNumbers = document.getElementById('line-numbers');
const btnExecute = document.getElementById('btn-execute');
const btnSubmit = document.getElementById('btn-submit');
const btnClearQuery = document.getElementById('btn-clear-query');
const btnHint = document.getElementById('btn-hint');
const resultsContainer = document.getElementById('results-container');
const resultsStats = document.getElementById('results-stats');
const feedbackContainer = document.getElementById('feedback-container');
const feedbackMessage = document.getElementById('feedback-message');
const feedbackHints = document.getElementById('feedback-hints');

// Modals
const levelCompleteModal = document.getElementById('level-complete-modal');
const helpModal = document.getElementById('help-modal');
const menuModal = document.getElementById('menu-modal');
const levelSelectModal = document.getElementById('level-select-modal');
const aboutModal = document.getElementById('about-modal');
const progressModal = document.getElementById('progress-modal');

/**
 * Initialize the game
 */
async function init() {
    // Initialize Three.js
    initThree();

    // Load game data
    await loadGameData();

    // Setup event listeners
    setupEventListeners();

    // Start animation loop
    animate();

    // Hide loading screen
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
    }, 2000);
}

/**
 * Initialize Three.js scene, camera, renderer
 */
function initThree() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);
    scene.fog = new THREE.Fog(0x0a0a0f, 5, 15);

    // Camera
    camera = new THREE.PerspectiveCamera(
        60,
        window.innerWidth / window.innerHeight,
        0.1,
        100
    );
    camera.position.set(0, 2.5, 6);
    camera.lookAt(0, 1.5, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas: gameCanvas,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 3;
    controls.maxDistance = 10;
    controls.maxPolarAngle = Math.PI / 2 + 0.1;
    controls.target.set(0, 1, 0);

    // Lighting
    setupLighting();

    // Create room
    detectiveRoom = new DetectiveRoom(scene);

    // Raycaster for interaction
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    // Handle resize
    window.addEventListener('resize', onWindowResize);
}

/**
 * Setup scene lighting
 */
function setupLighting() {
    // Ambient light (very dim)
    const ambient = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambient);

    // Main room light (dim overhead)
    const mainLight = new THREE.PointLight(0xffeedd, 0.5, 15);
    mainLight.position.set(0, 4.5, 0);
    mainLight.castShadow = true;
    scene.add(mainLight);

    // Window light (simulated moonlight through blinds)
    const windowLight = new THREE.DirectionalLight(0x8899aa, 0.3);
    windowLight.position.set(5, 3, 0);
    windowLight.castShadow = true;
    scene.add(windowLight);
}

/**
 * Load initial game data from API
 */
async function loadGameData() {
    try {
        // Get progress
        const progressData = await api.getProgress();
        if (progressData.success) {
            gameState.currentLevel = progressData.current_level || 1;
            gameState.completedLevels = progressData.completed_levels || [];
        }

        // Get all levels
        const levelsData = await api.getLevels();
        if (levelsData.success) {
            gameState.allLevels = levelsData.levels;
        }

        // Load current level
        await loadLevel(gameState.currentLevel);

    } catch (error) {
        console.error('Failed to load game data:', error);
    }
}

/**
 * Load specific level data
 */
async function loadLevel(levelId) {
    const levelData = await api.getLevel(levelId);
    if (levelData.success) {
        gameState.levelData = levelData.level;
        gameState.currentLevel = levelId;
        updateHUD();
    }
}

/**
 * Update HUD with current level info
 */
function updateHUD() {
    if (gameState.levelData) {
        currentLevelEl.textContent = gameState.currentLevel;
        levelTitleEl.textContent = gameState.levelData.title;
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Canvas interaction
    gameCanvas.addEventListener('mousemove', onMouseMove);
    gameCanvas.addEventListener('click', onCanvasClick);

    // Panel close buttons
    document.querySelectorAll('.panel-close').forEach(btn => {
        btn.addEventListener('click', closeAllPanels);
    });

    // SQL Editor
    sqlInput.addEventListener('input', updateLineNumbers);
    sqlInput.addEventListener('keydown', handleSQLKeydown);
    btnExecute.addEventListener('click', executeQuery);
    btnSubmit.addEventListener('click', submitAnswer);
    btnClearQuery.addEventListener('click', clearQuery);
    btnHint.addEventListener('click', showHint);

    // HUD buttons
    document.getElementById('btn-help').addEventListener('click', () => toggleModal(helpModal));
    document.getElementById('btn-menu').addEventListener('click', () => toggleModal(menuModal));
    document.getElementById('btn-sound').addEventListener('click', toggleSound);
    document.getElementById('btn-progress').addEventListener('click', showProgress);

    // Modal close buttons
    document.querySelectorAll('.modal-close-btn').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    // Level complete
    document.getElementById('btn-next-level').addEventListener('click', goToNextLevel);

    // Menu items
    document.getElementById('menu-restart').addEventListener('click', restartGame);
    document.getElementById('menu-levels').addEventListener('click', showLevelSelect);
    document.getElementById('menu-about').addEventListener('click', showAbout);
    document.getElementById('menu-analytics').addEventListener('click', () => {
        window.location.href = '/analytics';
    });

    // Close panels/modals on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAllPanels();
            closeAllModals();
        }
    });
}

/**
 * Handle mouse move for object highlighting
 */
function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const interactiveObjects = detectiveRoom.getInteractiveObjects();
    const intersects = raycaster.intersectObjects(interactiveObjects, true);

    if (intersects.length > 0) {
        const object = intersects[0].object;
        if (object.userData.interactive) {
            document.body.style.cursor = 'pointer';
            showInteractionHint(object.userData.action);

            if (hoveredObject !== object) {
                hoveredObject = object;
            }
        }
    } else {
        document.body.style.cursor = 'default';
        hideInteractionHint();
        hoveredObject = null;
    }
}

/**
 * Handle canvas click for object interaction
 */
function onCanvasClick(event) {
    if (hoveredObject && hoveredObject.userData.interactive) {
        const action = hoveredObject.userData.action;
        handleInteraction(action);
    }
}

/**
 * Handle interaction based on action type
 */
function handleInteraction(action) {
    closeAllPanels();

    switch (action) {
        case 'open_story':
            openStoryPanel();
            break;
        case 'open_evidence':
            openEvidencePanel();
            break;
        case 'open_terminal':
            openSQLEditor();
            break;
    }
}

/**
 * Show interaction hint
 */
function showInteractionHint(action) {
    const hints = {
        'open_story': '📁 Click to read case file',
        'open_evidence': '📌 Click to view evidence',
        'open_terminal': '💻 Click to open SQL terminal'
    };

    const hintText = interactionHint.querySelector('.hint-text');
    hintText.textContent = hints[action] || 'Click to interact';
    interactionHint.classList.remove('hidden');
}

/**
 * Hide interaction hint
 */
function hideInteractionHint() {
    interactionHint.classList.add('hidden');
}

/**
 * Open story panel with current level data
 */
function openStoryPanel() {
    if (!gameState.levelData) return;

    const level = gameState.levelData;
    document.getElementById('case-number').textContent = `LEVEL ${gameState.currentLevel}`;
    document.getElementById('story-text').textContent = level.story.trim();
    document.getElementById('objective-text').textContent = level.objective;

    const conceptsEl = document.getElementById('sql-concepts');
    conceptsEl.innerHTML = level.sql_concepts.map(c =>
        `<span class="concept-tag">${c}</span>`
    ).join('');

    storyPanel.classList.remove('hidden');
}

/**
 * Open evidence panel with available tables
 */
async function openEvidencePanel() {
    const tablesData = await api.getTables();

    if (tablesData.success) {
        const tablesList = document.getElementById('tables-list');
        const tableDescriptions = {
            'suspects': 'Profiles of persons of interest',
            'phone_records': 'Call and SMS logs',
            'cctv_logs': 'Surveillance footage records',
            'locations': 'City locations data',
            'bank_transactions': 'Financial transaction records',
            'crime_scenes': 'Crime scene details',
            'case_progress': 'Investigation progress'
        };

        const tableIcons = {
            'suspects': '👤',
            'phone_records': '📱',
            'cctv_logs': '📹',
            'locations': '📍',
            'bank_transactions': '💰',
            'crime_scenes': '🔍',
            'case_progress': '📊'
        };

        tablesList.innerHTML = tablesData.tables.map(table => `
            <div class="table-card" data-table="${table}">
                <div class="table-card-icon">${tableIcons[table] || '📋'}</div>
                <div class="table-card-name">${table}</div>
                <div class="table-card-desc">${tableDescriptions[table] || ''}</div>
            </div>
        `).join('');

        // Add click handlers for table cards
        tablesList.querySelectorAll('.table-card').forEach(card => {
            card.addEventListener('click', () => showTablePreview(card.dataset.table));
        });

        // Hide preview initially
        document.getElementById('table-preview').classList.add('hidden');
    }

    evidencePanel.classList.remove('hidden');
}

/**
 * Show table preview with schema and sample data
 */
async function showTablePreview(tableName) {
    const preview = document.getElementById('table-preview');
    const schemaDiv = document.getElementById('table-schema');
    const sampleDiv = document.getElementById('table-sample');

    document.getElementById('preview-table-name').textContent = tableName;

    // Get schema
    const schemaData = await api.getTableSchema(tableName);
    if (schemaData.success) {
        schemaDiv.innerHTML = `
            <table class="schema-table">
                <thead>
                    <tr><th>Column</th><th>Type</th><th>Key</th></tr>
                </thead>
                <tbody>
                    ${schemaData.schema.map(col => `
                        <tr>
                            <td class="col-name">${col.name}</td>
                            <td class="col-type">${col.type}</td>
                            <td class="col-pk">${col.primary_key ? '🔑 PK' : ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    // Get sample data
    const sampleData = await api.getTableSample(tableName);
    if (sampleData.success && sampleData.rows.length > 0) {
        sampleDiv.innerHTML = `
            <h4>Sample Data (${sampleData.rows.length} rows):</h4>
            <div class="sample-table-wrapper">
                <table class="sample-table">
                    <thead>
                        <tr>${sampleData.columns.map(c => `<th>${c}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${sampleData.rows.map(row => `
                            <tr>${row.map(cell => `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`).join('')}</tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // Update active state on cards
    document.querySelectorAll('.table-card').forEach(c => c.classList.remove('active'));
    document.querySelector(`.table-card[data-table="${tableName}"]`)?.classList.add('active');

    preview.classList.remove('hidden');
}

/**
 * Open SQL editor panel
 */
function openSQLEditor() {
    // Clear previous results
    clearResults();
    hideFeedback();

    sqlEditorPanel.classList.remove('hidden');
    sqlInput.focus();
}

/**
 * Update line numbers in SQL editor
 */
function updateLineNumbers() {
    const lines = sqlInput.value.split('\n').length;
    lineNumbers.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join('<br>');
}

/**
 * Handle special keystrokes in SQL editor
 */
function handleSQLKeydown(e) {
    // Ctrl/Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        executeQuery();
    }

    // Tab for indentation
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = sqlInput.selectionStart;
        const end = sqlInput.selectionEnd;
        sqlInput.value = sqlInput.value.substring(0, start) + '    ' + sqlInput.value.substring(end);
        sqlInput.selectionStart = sqlInput.selectionEnd = start + 4;
    }
}

/**
 * Execute query and show results
 */
async function executeQuery() {
    const query = sqlInput.value.trim();
    if (!query) return;

    btnExecute.disabled = true;
    btnExecute.classList.add('loading');
    hideFeedback();

    try {
        const result = await api.executeQuery(query);
        displayResults(result);

        if (!result.success) {
            showFeedback(false, result.error);
        }
    } catch (error) {
        showFeedback(false, 'An error occurred. Please try again.');
    } finally {
        btnExecute.disabled = false;
        btnExecute.classList.remove('loading');
    }
}

/**
 * Submit answer for current level
 */
async function submitAnswer() {
    const query = sqlInput.value.trim();
    if (!query) return;

    btnSubmit.disabled = true;
    btnSubmit.classList.add('loading');

    try {
        const result = await api.checkAnswer(query, gameState.currentLevel);

        if (result.correct) {
            // Success!
            displayResults(result.user_result);
            showFeedback(true, result.message);

            // Update game state
            if (!gameState.completedLevels.includes(gameState.currentLevel)) {
                gameState.completedLevels.push(gameState.currentLevel);
            }

            // Show success modal after delay
            setTimeout(() => {
                showLevelComplete(result);
            }, 1500);
        } else {
            // Incorrect
            displayResults(result.user_result);
            showFeedback(false, result.message, result.hints);

            // Shake animation on panel
            sqlEditorPanel.classList.add('shake');
            setTimeout(() => sqlEditorPanel.classList.remove('shake'), 500);
        }
    } catch (error) {
        showFeedback(false, 'An error occurred. Please try again.');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.classList.remove('loading');
    }
}

/**
 * Display query results in table format
 */
function displayResults(result) {
    if (!result || !result.columns || result.columns.length === 0) {
        resultsContainer.innerHTML = '<div class="results-placeholder">No results to display</div>';
        resultsStats.textContent = '';
        return;
    }

    const { columns, rows, row_count, execution_time, truncated } = result;

    resultsStats.textContent = `${row_count} row${row_count !== 1 ? 's' : ''} • ${execution_time}ms${truncated ? ' (truncated)' : ''}`;

    resultsContainer.innerHTML = `
        <table class="results-table">
            <thead>
                <tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${rows.map(row => `
                    <tr>${row.map(cell => `<td>${cell !== null ? cell : '<span class="null-value">NULL</span>'}</td>`).join('')}</tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

/**
 * Clear query results
 */
function clearResults() {
    resultsContainer.innerHTML = '<div class="results-placeholder">Execute a query to see results here...</div>';
    resultsStats.textContent = '';
}

/**
 * Show feedback message
 */
function showFeedback(success, message, hints = []) {
    feedbackContainer.classList.remove('hidden', 'success', 'error');
    feedbackContainer.classList.add(success ? 'success' : 'error');
    feedbackMessage.textContent = message;

    if (hints && hints.length > 0) {
        feedbackHints.innerHTML = hints.map(h => `<div class="feedback-hint">${h}</div>`).join('');
        feedbackHints.classList.remove('hidden');
    } else {
        feedbackHints.classList.add('hidden');
    }
}

/**
 * Hide feedback message
 */
function hideFeedback() {
    feedbackContainer.classList.add('hidden');
}

/**
 * Clear SQL input
 */
function clearQuery() {
    sqlInput.value = '';
    updateLineNumbers();
    clearResults();
    hideFeedback();
    sqlInput.focus();
}

/**
 * Show hint for current level
 */
function showHint() {
    if (gameState.levelData && gameState.levelData.hint) {
        showFeedback(true, '💡 ' + gameState.levelData.hint);
    }
}

/**
 * Show level complete modal
 */
function showLevelComplete(result) {
    document.getElementById('success-message').textContent = result.message;

    const nextBtn = document.getElementById('btn-next-level');
    if (result.next_level) {
        nextBtn.textContent = `Continue to Level ${result.next_level} →`;
        nextBtn.onclick = goToNextLevel;
    } else {
        nextBtn.textContent = '🎉 Game Complete! Play Again';
        nextBtn.onclick = restartGame;
    }

    levelCompleteModal.classList.remove('hidden');
}

/**
 * Go to next level
 */
async function goToNextLevel() {
    levelCompleteModal.classList.add('hidden');
    closeAllPanels();

    await loadLevel(gameState.currentLevel + 1);
    clearQuery();
}

/**
 * Restart game
 */
async function restartGame() {
    closeAllModals();
    closeAllPanels();

    await api.resetProgress();
    gameState.currentLevel = 1;
    gameState.completedLevels = [];
    await loadLevel(1);
    clearQuery();
}

/**
 * Close all panels
 */
function closeAllPanels() {
    storyPanel.classList.add('hidden');
    evidencePanel.classList.add('hidden');
    sqlEditorPanel.classList.add('hidden');
}

/**
 * Toggle modal visibility
 */
function toggleModal(modal) {
    modal.classList.toggle('hidden');
}

/**
 * Close all modals
 */
function closeAllModals() {
    helpModal.classList.add('hidden');
    menuModal.classList.add('hidden');
    levelCompleteModal.classList.add('hidden');
    levelSelectModal.classList.add('hidden');
    aboutModal.classList.add('hidden');
    progressModal.classList.add('hidden');
}

/**
 * Toggle sound on/off
 */
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    const soundBtn = document.getElementById('btn-sound');
    soundBtn.textContent = gameState.soundEnabled ? '🔊' : '🔇';
    soundBtn.title = gameState.soundEnabled ? 'Sound On' : 'Sound Off';
}

/**
 * Show level select modal
 */
function showLevelSelect() {
    closeAllModals();

    const levelsGrid = document.getElementById('levels-grid');
    levelsGrid.innerHTML = gameState.allLevels.map(level => {
        const isCompleted = gameState.completedLevels.includes(level.id);
        const isCurrent = level.id === gameState.currentLevel;
        const isLocked = level.id > gameState.currentLevel && !isCompleted;

        return `
            <div class="level-card ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''} ${isLocked ? 'locked' : ''}"
                 data-level="${level.id}" ${isLocked ? 'disabled' : ''}>
                <div class="level-number">${isLocked ? '🔒' : level.id}</div>
                <div class="level-title">${level.title}</div>
                <div class="level-status">
                    ${isCompleted ? '✅ Completed' : isCurrent ? '🔹 Current' : isLocked ? '🔒 Locked' : ''}
                </div>
            </div>
        `;
    }).join('');

    // Add click handlers
    levelsGrid.querySelectorAll('.level-card:not(.locked)').forEach(card => {
        card.addEventListener('click', async () => {
            const levelId = parseInt(card.dataset.level);
            await loadLevel(levelId);
            closeAllModals();
            closeAllPanels();
            clearQuery();
        });
    });

    levelSelectModal.classList.remove('hidden');
}

/**
 * Show about modal
 */
function showAbout() {
    closeAllModals();
    aboutModal.classList.remove('hidden');
}

/**
 * Show level progress modal
 */
function showProgress() {
    const progressDetails = document.getElementById('progress-details');
    const totalLevels = gameState.allLevels.length || 7;
    const completedCount = gameState.completedLevels.length;
    const progressPercent = Math.round((completedCount / totalLevels) * 100);

    progressDetails.innerHTML = `
        <div class="progress-summary">
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${progressPercent}%"></div>
            </div>
            <div class="progress-text">${completedCount} of ${totalLevels} levels completed (${progressPercent}%)</div>
        </div>
        <div class="progress-levels">
            ${gameState.allLevels.map(level => {
        const isCompleted = gameState.completedLevels.includes(level.id);
        const isCurrent = level.id === gameState.currentLevel;
        return `
                    <div class="progress-level ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}">
                        <span class="progress-level-num">${level.id}</span>
                        <span class="progress-level-title">${level.title}</span>
                        <span class="progress-level-status">${isCompleted ? '✅' : isCurrent ? '🔹' : '⬜'}</span>
                    </div>
                `;
    }).join('')}
        </div>
    `;

    progressModal.classList.remove('hidden');
}

/**
 * Handle window resize
 */
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

/**
 * Animation loop
 */
function animate() {
    requestAnimationFrame(animate);

    const deltaTime = 0.016; // ~60fps

    // Update controls
    controls.update();

    // Update room animations
    if (detectiveRoom) {
        detectiveRoom.update(deltaTime);
    }

    // Render
    renderer.render(scene, camera);
}

// Start the game when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
