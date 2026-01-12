/**
 * SQL Detective Game - Detective Room 3D Scene
 * Creates an immersive noir detective office using Three.js
 */

import * as THREE from 'three';

export class DetectiveRoom {
    constructor(scene) {
        this.scene = scene;
        this.interactiveObjects = new Map();
        this.animatedLights = [];
        this.time = 0;

        this.createRoom();
        this.createDesk();
        this.createEvidenceBoard();
        this.createComputer();
        this.createAmbience();
        this.createAtmosphericLighting();
    }

    /**
     * Create the room structure (walls, floor, ceiling)
     */
    createRoom() {
        const roomWidth = 12;
        const roomHeight = 5;
        const roomDepth = 10;

        // Floor
        const floorGeometry = new THREE.PlaneGeometry(roomWidth, roomDepth);
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: 0x2a1810,
            roughness: 0.9,
            metalness: 0.1
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        floor.receiveShadow = true;
        this.scene.add(floor);

        // Add floor planks texture effect
        const plankLines = new THREE.Group();
        for (let i = -5; i <= 5; i++) {
            const lineGeometry = new THREE.PlaneGeometry(0.02, roomDepth);
            const lineMaterial = new THREE.MeshBasicMaterial({ color: 0x1a0f08 });
            const line = new THREE.Mesh(lineGeometry, lineMaterial);
            line.rotation.x = -Math.PI / 2;
            line.position.set(i * 1, 0.001, 0);
            plankLines.add(line);
        }
        this.scene.add(plankLines);

        // Back Wall
        const wallMaterial = new THREE.MeshStandardMaterial({
            color: 0x3a3028,
            roughness: 0.8,
            metalness: 0
        });

        const backWall = new THREE.Mesh(
            new THREE.PlaneGeometry(roomWidth, roomHeight),
            wallMaterial
        );
        backWall.position.set(0, roomHeight / 2, -roomDepth / 2);
        backWall.receiveShadow = true;
        this.scene.add(backWall);

        // Left Wall
        const leftWall = new THREE.Mesh(
            new THREE.PlaneGeometry(roomDepth, roomHeight),
            wallMaterial
        );
        leftWall.rotation.y = Math.PI / 2;
        leftWall.position.set(-roomWidth / 2, roomHeight / 2, 0);
        leftWall.receiveShadow = true;
        this.scene.add(leftWall);

        // Right Wall
        const rightWall = new THREE.Mesh(
            new THREE.PlaneGeometry(roomDepth, roomHeight),
            wallMaterial
        );
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.position.set(roomWidth / 2, roomHeight / 2, 0);
        rightWall.receiveShadow = true;
        this.scene.add(rightWall);

        // Ceiling
        const ceiling = new THREE.Mesh(
            new THREE.PlaneGeometry(roomWidth, roomDepth),
            new THREE.MeshStandardMaterial({ color: 0x252018, roughness: 1 })
        );
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = roomHeight;
        this.scene.add(ceiling);

        // Add baseboards
        this.createBaseboards(roomWidth, roomDepth);
    }

    createBaseboards(width, depth) {
        const boardMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1008 });
        const boardHeight = 0.15;

        // Back baseboard
        const backBoard = new THREE.Mesh(
            new THREE.BoxGeometry(width, boardHeight, 0.05),
            boardMaterial
        );
        backBoard.position.set(0, boardHeight / 2, -depth / 2 + 0.025);
        this.scene.add(backBoard);

        // Left baseboard
        const leftBoard = new THREE.Mesh(
            new THREE.BoxGeometry(0.05, boardHeight, depth),
            boardMaterial
        );
        leftBoard.position.set(-width / 2 + 0.025, boardHeight / 2, 0);
        this.scene.add(leftBoard);

        // Right baseboard
        const rightBoard = new THREE.Mesh(
            new THREE.BoxGeometry(0.05, boardHeight, depth),
            boardMaterial
        );
        rightBoard.position.set(width / 2 - 0.025, boardHeight / 2, 0);
        this.scene.add(rightBoard);
    }

    /**
     * Create the detective's desk with case files
     */
    createDesk() {
        const deskGroup = new THREE.Group();
        deskGroup.name = 'desk';

        // Desk surface
        const deskTopGeometry = new THREE.BoxGeometry(3, 0.08, 1.5);
        const deskMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a3020,
            roughness: 0.7,
            metalness: 0.1
        });
        const deskTop = new THREE.Mesh(deskTopGeometry, deskMaterial);
        deskTop.position.y = 0.8;
        deskTop.castShadow = true;
        deskTop.receiveShadow = true;
        deskGroup.add(deskTop);

        // Desk legs
        const legGeometry = new THREE.BoxGeometry(0.1, 0.8, 0.1);
        const legMaterial = new THREE.MeshStandardMaterial({ color: 0x3a2515 });
        const legPositions = [
            [-1.4, 0.4, -0.65],
            [1.4, 0.4, -0.65],
            [-1.4, 0.4, 0.65],
            [1.4, 0.4, 0.65]
        ];
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeometry, legMaterial);
            leg.position.set(...pos);
            leg.castShadow = true;
            deskGroup.add(leg);
        });

        // Case file folder on desk
        const folderGroup = new THREE.Group();
        folderGroup.name = 'case_file';

        const folderGeometry = new THREE.BoxGeometry(0.35, 0.02, 0.45);
        const folderMaterial = new THREE.MeshStandardMaterial({ color: 0x8b6914 });
        const folder = new THREE.Mesh(folderGeometry, folderMaterial);
        folder.castShadow = true;
        folderGroup.add(folder);

        // Papers sticking out
        const paperGeometry = new THREE.BoxGeometry(0.3, 0.015, 0.4);
        const paperMaterial = new THREE.MeshStandardMaterial({ color: 0xfff8e7 });
        const papers = new THREE.Mesh(paperGeometry, paperMaterial);
        papers.position.set(0, 0.015, -0.02);
        folderGroup.add(papers);

        // Label on folder
        const labelGeometry = new THREE.BoxGeometry(0.15, 0.005, 0.04);
        const labelMaterial = new THREE.MeshStandardMaterial({ color: 0xff4444 });
        const label = new THREE.Mesh(labelGeometry, labelMaterial);
        label.position.set(0, 0.015, 0.18);
        folderGroup.add(label);

        folderGroup.position.set(-0.8, 0.85, 0);
        folderGroup.rotation.y = 0.1;
        deskGroup.add(folderGroup);

        // Register as interactive
        this.registerInteractive(folderGroup, 'open_story');

        // Desk lamp
        this.createDeskLamp(deskGroup);

        // Position desk in room
        deskGroup.position.set(0, 0, 1);
        this.scene.add(deskGroup);
    }

    createDeskLamp(parent) {
        const lampGroup = new THREE.Group();

        // Lamp base
        const baseGeometry = new THREE.CylinderGeometry(0.12, 0.15, 0.05, 16);
        const baseMaterial = new THREE.MeshStandardMaterial({
            color: 0x2a5a3a,
            metalness: 0.5,
            roughness: 0.3
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        lampGroup.add(base);

        // Lamp arm
        const armGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 8);
        const arm = new THREE.Mesh(armGeometry, baseMaterial);
        arm.position.set(0, 0.27, 0);
        arm.rotation.z = 0.3;
        lampGroup.add(arm);

        // Lamp shade
        const shadeGeometry = new THREE.ConeGeometry(0.18, 0.15, 16, 1, true);
        const shadeMaterial = new THREE.MeshStandardMaterial({
            color: 0x1a4a2a,
            side: THREE.DoubleSide,
            metalness: 0.3,
            roughness: 0.5
        });
        const shade = new THREE.Mesh(shadeGeometry, shadeMaterial);
        shade.position.set(0.15, 0.45, 0);
        shade.rotation.z = -0.3;
        shade.rotation.x = Math.PI;
        lampGroup.add(shade);

        // Lamp light (actual light source) - Enhanced with warm glow
        const lampLight = new THREE.PointLight(0xffaa55, 2.5, 6);
        lampLight.position.set(0.15, 0.4, 0);
        lampLight.castShadow = true;
        lampLight.shadow.mapSize.width = 1024;
        lampLight.shadow.mapSize.height = 1024;
        lampGroup.add(lampLight);

        // Add lamp to animated lights for flicker effect
        this.animatedLights.push({ light: lampLight, baseIntensity: 2.5, type: 'flicker' });

        // Warm glow sphere inside lamp shade
        const glowSphere = new THREE.Mesh(
            new THREE.SphereGeometry(0.05, 16, 16),
            new THREE.MeshBasicMaterial({ color: 0xffcc88 })
        );
        glowSphere.position.set(0.15, 0.38, 0);
        lampGroup.add(glowSphere);

        lampGroup.position.set(1, 0.85, -0.4);
        parent.add(lampGroup);
    }

    /**
     * Create the evidence board on the wall
     */
    createEvidenceBoard() {
        const boardGroup = new THREE.Group();
        boardGroup.name = 'evidence_board';

        // Cork board
        const boardGeometry = new THREE.BoxGeometry(2.5, 1.8, 0.08);
        const boardMaterial = new THREE.MeshStandardMaterial({
            color: 0xa67c52,
            roughness: 0.9
        });
        const board = new THREE.Mesh(boardGeometry, boardMaterial);
        board.castShadow = true;
        boardGroup.add(board);

        // Frame
        const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x2a1a0a });

        // Top frame
        const topFrame = new THREE.Mesh(
            new THREE.BoxGeometry(2.6, 0.08, 0.12),
            frameMaterial
        );
        topFrame.position.y = 0.94;
        boardGroup.add(topFrame);

        // Bottom frame
        const bottomFrame = new THREE.Mesh(
            new THREE.BoxGeometry(2.6, 0.08, 0.12),
            frameMaterial
        );
        bottomFrame.position.y = -0.94;
        boardGroup.add(bottomFrame);

        // Left frame
        const leftFrame = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 1.96, 0.12),
            frameMaterial
        );
        leftFrame.position.x = -1.3;
        boardGroup.add(leftFrame);

        // Right frame
        const rightFrame = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 1.96, 0.12),
            frameMaterial
        );
        rightFrame.position.x = 1.3;
        boardGroup.add(rightFrame);

        // Add pins and notes
        this.addBoardDecorations(boardGroup);

        // Position on back wall
        boardGroup.position.set(-2.5, 2, -4.9);
        this.scene.add(boardGroup);

        // Register as interactive
        this.registerInteractive(boardGroup, 'open_evidence');
    }

    addBoardDecorations(parent) {
        // Colorful sticky notes
        const noteColors = [0xffeb3b, 0x4caf50, 0x2196f3, 0xff5722, 0xffffff];
        const notePositions = [
            [-0.8, 0.5, 0.05],
            [-0.3, 0.6, 0.05],
            [0.4, 0.4, 0.05],
            [0.8, 0.6, 0.05],
            [-0.5, -0.3, 0.05],
            [0.2, -0.4, 0.05],
            [0.7, -0.2, 0.05]
        ];

        notePositions.forEach((pos, i) => {
            const noteGeometry = new THREE.BoxGeometry(0.25, 0.2, 0.01);
            const noteMaterial = new THREE.MeshStandardMaterial({
                color: noteColors[i % noteColors.length]
            });
            const note = new THREE.Mesh(noteGeometry, noteMaterial);
            note.position.set(...pos);
            note.rotation.z = (Math.random() - 0.5) * 0.3;
            parent.add(note);

            // Pin
            const pinGeometry = new THREE.SphereGeometry(0.02, 8, 8);
            const pinMaterial = new THREE.MeshStandardMaterial({ color: 0xff0000 });
            const pin = new THREE.Mesh(pinGeometry, pinMaterial);
            pin.position.set(pos[0], pos[1] + 0.08, pos[2] + 0.02);
            parent.add(pin);
        });

        // String connections
        const stringMaterial = new THREE.LineBasicMaterial({ color: 0xff0000 });
        const stringPoints = [
            [new THREE.Vector3(-0.8, 0.5, 0.06), new THREE.Vector3(-0.3, 0.6, 0.06)],
            [new THREE.Vector3(-0.3, 0.6, 0.06), new THREE.Vector3(0.4, 0.4, 0.06)],
            [new THREE.Vector3(0.4, 0.4, 0.06), new THREE.Vector3(0.2, -0.4, 0.06)]
        ];

        stringPoints.forEach(points => {
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, stringMaterial);
            parent.add(line);
        });
    }

    /**
     * Create the computer terminal
     */
    createComputer() {
        const computerGroup = new THREE.Group();
        computerGroup.name = 'computer';

        // Monitor
        const monitorGeometry = new THREE.BoxGeometry(0.8, 0.5, 0.05);
        const monitorMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1a1a });
        const monitor = new THREE.Mesh(monitorGeometry, monitorMaterial);
        monitor.position.y = 0.3;
        monitor.castShadow = true;
        computerGroup.add(monitor);

        // Screen (glowing) - Enhanced neon effect
        const screenGeometry = new THREE.PlaneGeometry(0.7, 0.42);
        const screenMaterial = new THREE.MeshBasicMaterial({
            color: 0x0a3322,
            opacity: 0.95,
            transparent: true
        });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.set(0, 0.3, 0.03);
        screen.name = 'monitor_screen';
        computerGroup.add(screen);

        // Screen glow - Multiple layers for depth
        const glowGeometry = new THREE.PlaneGeometry(0.75, 0.47);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ff88,
            transparent: true,
            opacity: 0.15
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.set(0, 0.3, 0.02);
        computerGroup.add(glow);

        // Outer glow halo
        const haloGeometry = new THREE.PlaneGeometry(0.85, 0.55);
        const haloMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ff88,
            transparent: true,
            opacity: 0.05
        });
        const halo = new THREE.Mesh(haloGeometry, haloMaterial);
        halo.position.set(0, 0.3, 0.01);
        computerGroup.add(halo);

        // Screen scanlines effect
        const scanlineGeometry = new THREE.PlaneGeometry(0.7, 0.42);
        const scanlineMaterial = new THREE.ShaderMaterial({
            transparent: true,
            uniforms: {
                time: { value: 0 }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec2 vUv;
                uniform float time;
                void main() {
                    float scanline = sin(vUv.y * 100.0 + time * 2.0) * 0.03 + 0.97;
                    float flicker = sin(time * 10.0) * 0.01 + 0.99;
                    gl_FragColor = vec4(0.0, 1.0, 0.5, 0.1 * scanline * flicker);
                }
            `
        });
        this.scanlineMaterial = scanlineMaterial;
        const scanlines = new THREE.Mesh(scanlineGeometry, scanlineMaterial);
        scanlines.position.set(0, 0.3, 0.035);
        computerGroup.add(scanlines);

        // Monitor stand
        const standGeometry = new THREE.BoxGeometry(0.15, 0.15, 0.1);
        const stand = new THREE.Mesh(standGeometry, monitorMaterial);
        stand.position.set(0, 0, 0);
        computerGroup.add(stand);

        // Monitor base
        const baseGeometry = new THREE.BoxGeometry(0.35, 0.02, 0.2);
        const base = new THREE.Mesh(baseGeometry, monitorMaterial);
        base.position.set(0, -0.05, 0.05);
        computerGroup.add(base);

        // Keyboard
        const keyboardGeometry = new THREE.BoxGeometry(0.5, 0.02, 0.15);
        const keyboardMaterial = new THREE.MeshStandardMaterial({ color: 0x2a2a2a });
        const keyboard = new THREE.Mesh(keyboardGeometry, keyboardMaterial);
        keyboard.position.set(0, -0.04, 0.35);
        keyboard.rotation.x = -0.1;
        computerGroup.add(keyboard);

        // Add screen light - Enhanced
        const screenLight = new THREE.PointLight(0x00ff88, 1.2, 3);
        screenLight.position.set(0, 0.3, 0.5);
        computerGroup.add(screenLight);
        this.animatedLights.push({ light: screenLight, baseIntensity: 1.2, type: 'pulse' });

        // Position on desk
        computerGroup.position.set(0.3, 0.88, 1);
        this.scene.add(computerGroup);

        // Register as interactive
        this.registerInteractive(computerGroup, 'open_terminal');
    }

    /**
     * Create ambient room decorations
     */
    createAmbience() {
        // Venetian blinds on right wall (window suggestion)
        this.createBlinds();

        // Bookshelf on left wall
        this.createBookshelf();

        // Filing cabinet
        this.createFilingCabinet();

        // Add dust particles
        this.createDustParticles();
    }

    createBlinds() {
        const blindsGroup = new THREE.Group();
        const blindMaterial = new THREE.MeshStandardMaterial({ color: 0xccccbb });

        for (let i = 0; i < 15; i++) {
            const blind = new THREE.Mesh(
                new THREE.BoxGeometry(0.02, 0.08, 1.5),
                blindMaterial
            );
            blind.position.set(0, i * 0.12, 0);
            blind.rotation.z = 0.3; // Partially open
            blindsGroup.add(blind);
        }

        // Frame
        const frameMaterial = new THREE.MeshStandardMaterial({ color: 0x4a3a2a });
        const topFrame = new THREE.Mesh(
            new THREE.BoxGeometry(0.08, 0.1, 1.6),
            frameMaterial
        );
        topFrame.position.y = 1.9;
        blindsGroup.add(topFrame);

        blindsGroup.position.set(5.9, 1.5, 0);
        blindsGroup.rotation.y = -Math.PI / 2;
        this.scene.add(blindsGroup);

        // Light streaming through blinds
        const blindLight = new THREE.SpotLight(0xffeedd, 0.3, 8, Math.PI / 6);
        blindLight.position.set(5.5, 2.5, 0);
        blindLight.target.position.set(0, 0, 0);
        this.scene.add(blindLight);
        this.scene.add(blindLight.target);
    }

    createBookshelf() {
        const shelfGroup = new THREE.Group();
        const woodMaterial = new THREE.MeshStandardMaterial({ color: 0x3a2515 });

        // Shelf frame
        // Back
        const back = new THREE.Mesh(
            new THREE.BoxGeometry(1.5, 2, 0.05),
            woodMaterial
        );
        back.position.z = -0.2;
        shelfGroup.add(back);

        // Shelves
        for (let i = 0; i < 4; i++) {
            const shelf = new THREE.Mesh(
                new THREE.BoxGeometry(1.5, 0.05, 0.4),
                woodMaterial
            );
            shelf.position.y = i * 0.5 - 0.75;
            shelfGroup.add(shelf);
        }

        // Side panels
        const leftSide = new THREE.Mesh(
            new THREE.BoxGeometry(0.05, 2, 0.4),
            woodMaterial
        );
        leftSide.position.x = -0.75;
        shelfGroup.add(leftSide);

        const rightSide = new THREE.Mesh(
            new THREE.BoxGeometry(0.05, 2, 0.4),
            woodMaterial
        );
        rightSide.position.x = 0.75;
        shelfGroup.add(rightSide);

        // Add some books
        const bookColors = [0x8b0000, 0x00008b, 0x006400, 0x8b4513, 0x2f4f4f];
        for (let shelf = 0; shelf < 3; shelf++) {
            for (let book = 0; book < 6; book++) {
                const height = 0.25 + Math.random() * 0.15;
                const bookMesh = new THREE.Mesh(
                    new THREE.BoxGeometry(0.15, height, 0.2),
                    new THREE.MeshStandardMaterial({
                        color: bookColors[Math.floor(Math.random() * bookColors.length)]
                    })
                );
                bookMesh.position.set(
                    -0.5 + book * 0.2,
                    shelf * 0.5 - 0.75 + 0.025 + height / 2,
                    0
                );
                shelfGroup.add(bookMesh);
            }
        }

        shelfGroup.position.set(-5.8, 1.5, -2);
        shelfGroup.rotation.y = Math.PI / 2;
        this.scene.add(shelfGroup);
    }

    createFilingCabinet() {
        const cabinetGroup = new THREE.Group();
        const metalMaterial = new THREE.MeshStandardMaterial({
            color: 0x4a4a4a,
            metalness: 0.6,
            roughness: 0.4
        });

        // Cabinet body
        const body = new THREE.Mesh(
            new THREE.BoxGeometry(0.5, 1.2, 0.6),
            metalMaterial
        );
        body.position.y = 0.6;
        body.castShadow = true;
        cabinetGroup.add(body);

        // Drawers
        for (let i = 0; i < 3; i++) {
            const drawer = new THREE.Mesh(
                new THREE.BoxGeometry(0.45, 0.35, 0.02),
                metalMaterial
            );
            drawer.position.set(0, 0.25 + i * 0.38, 0.29);
            cabinetGroup.add(drawer);

            // Handle
            const handle = new THREE.Mesh(
                new THREE.BoxGeometry(0.15, 0.02, 0.03),
                new THREE.MeshStandardMaterial({ color: 0x888888, metalness: 0.8 })
            );
            handle.position.set(0, 0.25 + i * 0.38, 0.32);
            cabinetGroup.add(handle);
        }

        cabinetGroup.position.set(4, 0, -3);
        this.scene.add(cabinetGroup);
    }

    createDustParticles() {
        const particleCount = 100;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 10;
            positions[i + 1] = Math.random() * 4 + 0.5;
            positions[i + 2] = (Math.random() - 0.5) * 8;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.02,
            transparent: true,
            opacity: 0.4
        });

        this.dustParticles = new THREE.Points(geometry, material);
        this.scene.add(this.dustParticles);
    }

    /**
     * Register an object as interactive
     */
    registerInteractive(object, action) {
        this.interactiveObjects.set(object.uuid, { object, action });
        // Store action on the object for raycast identification
        object.userData.action = action;
        object.userData.interactive = true;
    }

    /**
     * Get all interactive objects for raycasting
     */
    getInteractiveObjects() {
        const objects = [];
        this.interactiveObjects.forEach(({ object }) => {
            object.traverse((child) => {
                if (child.isMesh) {
                    child.userData.action = object.userData.action;
                    child.userData.interactive = true;
                    objects.push(child);
                }
            });
        });
        return objects;
    }

    /**
     * Update dust particle animation
     */
    update(deltaTime) {
        this.time += deltaTime;

        // Update dust particles
        if (this.dustParticles) {
            const positions = this.dustParticles.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                positions[i + 1] += Math.sin(Date.now() * 0.001 + i) * 0.001;
                positions[i] += Math.sin(Date.now() * 0.0005 + i) * 0.0005;
                if (positions[i + 1] > 4.5) positions[i + 1] = 0.5;
            }
            this.dustParticles.geometry.attributes.position.needsUpdate = true;
        }

        // Update animated lights
        this.animatedLights.forEach(({ light, baseIntensity, type }) => {
            if (type === 'flicker') {
                // Subtle lamp flicker
                const flicker = Math.sin(this.time * 15) * 0.05 + Math.sin(this.time * 23) * 0.03;
                light.intensity = baseIntensity * (1 + flicker);
            } else if (type === 'pulse') {
                // Smooth pulse for screen
                const pulse = Math.sin(this.time * 2) * 0.15;
                light.intensity = baseIntensity * (1 + pulse);
            }
        });

        // Update scanline shader
        if (this.scanlineMaterial) {
            this.scanlineMaterial.uniforms.time.value = this.time;
        }

        // Update neon sign if exists
        if (this.neonLight) {
            const neonFlicker = Math.sin(this.time * 8) * 0.1 + Math.sin(this.time * 13) * 0.05;
            this.neonLight.intensity = 0.8 * (1 + neonFlicker);
        }
    }

    /**
     * Create atmospheric lighting effects
     */
    createAtmosphericLighting() {
        // Subtle pink accent light on left wall
        this.neonLight = new THREE.PointLight(0xff3366, 0.5, 6);
        this.neonLight.position.set(-5, 2.5, -3);
        this.scene.add(this.neonLight);

        // Blue accent light from window blinds area
        const moonLight = new THREE.SpotLight(0x4488ff, 0.4, 12, Math.PI / 4, 0.5);
        moonLight.position.set(6, 4, 0);
        moonLight.target.position.set(0, 0, 0);
        moonLight.castShadow = true;
        this.scene.add(moonLight);
        this.scene.add(moonLight.target);

        // Volumetric light beams through blinds
        const beamMaterial = new THREE.MeshBasicMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.03,
            side: THREE.DoubleSide
        });

        for (let i = 0; i < 5; i++) {
            const beamGeometry = new THREE.PlaneGeometry(0.1, 5);
            const beam = new THREE.Mesh(beamGeometry, beamMaterial);
            beam.position.set(4 - i * 0.8, 2, -1 + i * 0.5);
            beam.rotation.y = -0.3;
            beam.rotation.x = 0.1;
            this.scene.add(beam);
        }

        // Warm fill light from below (simulate floor bounce)
        const bounceLight = new THREE.PointLight(0xffaa66, 0.15, 8);
        bounceLight.position.set(0, 0.3, 2);
        this.scene.add(bounceLight);

        // Cool rim light for depth
        const rimLight = new THREE.DirectionalLight(0x6688cc, 0.2);
        rimLight.position.set(-3, 3, 5);
        this.scene.add(rimLight);
    }
}

export default DetectiveRoom;

