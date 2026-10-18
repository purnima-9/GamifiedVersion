import Phaser from 'phaser';

const DESTINATIONS = [
  {
    id: 'cafe',
    label: 'Morning Café',
    x: 250,
    y: 450,
    color: '#D4892D',
    accentColor: '#F4A460',
    icon: '☕',
    description: 'A cozy morning spot',
  },
  {
    id: 'home',
    label: 'Study Break',
    x: 600,
    y: 420,
    color: '#9B6B45',
    accentColor: '#D4A574',
    icon: '🏠',
    description: 'A place to focus',
  },
  {
    id: 'store',
    label: 'Evening Retreat',
    x: 950,
    y: 450,
    color: '#8B5A8C',
    accentColor: '#B98AC7',
    icon: '🌙',
    description: 'A relaxing escape',
  },
];

export class NeighborhoodScene extends Phaser.Scene {
  constructor() {
    super('neighborhood');
    this.character = null;
    this.destinationZones = [];
    this.selectedDestination = null;
    this.moveSpeed = 200;
    this.keys = {};
  }

  create() {
    const { width, height } = this.cameras.main;

    // ========== BACKGROUND LAYERS ==========

    // Sky gradient
    this.add
      .rectangle(0, 0, width, height * 0.5, 0x87ceeb)
      .setOrigin(0, 0)
      .setDepth(-100);

    // Soft clouds (decorative circles)
    this.add
      .circle(150, 80, 60, 0xffffff, 0.3)
      .setDepth(-95);
    this.add
      .circle(250, 120, 50, 0xffffff, 0.25)
      .setDepth(-95);
    this.add
      .circle(width - 200, 100, 55, 0xffffff, 0.28)
      .setDepth(-95);

    // Ground/grass area
    this.add
      .rectangle(0, height * 0.5, width, height * 0.5, 0xB8860B)
      .setOrigin(0, 0)
      .setDepth(-90);

    // Lighter grass overlay for depth
    this.add
      .rectangle(0, height * 0.55, width, 20, 0xD2B48C, 0.5)
      .setOrigin(0, 0)
      .setDepth(-85);

    // Path/focal area
    const pathY = height * 0.6;
    this.add
      .ellipse(width / 2, pathY + 30, width * 0.3, 50, 0xD4A574, 0.4)
      .setDepth(-80);

    // ========== DISTANT BUILDINGS (BACKGROUND SILHOUETTES) ==========

    // Distant small house (left)
    this.add
      .rectangle(80, height * 0.35, 40, 50, 0x6B4423, 0.4)
      .setOrigin(0.5, 0.5)
      .setDepth(-70);
    this.add
      .polygon(80, height * 0.3, [0, 0, -20, -15, 20, -15], 0x5A3A1A, 0.4)
      .setOrigin(0.5, 0.5)
      .setDepth(-69);

    // Distant building (right)
    this.add
      .rectangle(width - 100, height * 0.4, 50, 60, 0x6B4423, 0.35)
      .setOrigin(0.5, 0.5)
      .setDepth(-70);

    // ========== CHARACTER ==========
    this.character = this.add.circle(width / 2, height * 0.5, 24, 0xFFAA99).setDepth(10);

    // Head detail
    this.add
      .ellipse(width / 2, height * 0.5 - 15, 14, 16, 0xFFCC99)
      .setDepth(11);

    // Eyes
    this.add
      .circle(width / 2 - 5, height * 0.5 - 17, 2, 0x333333)
      .setDepth(12);
    this.add
      .circle(width / 2 + 5, height * 0.5 - 17, 2, 0x333333)
      .setDepth(12);

    // Cute smile
    this.add
      .arc(width / 2, height * 0.5 - 12, 8, Phaser.Math.DegToRad(0), Phaser.Math.DegToRad(180), false, 0x333333)
      .setDepth(12)
      .setLineWidth(1.5);

    // Character shadow
    this.add
      .ellipse(width / 2, height * 0.5 + 28, 35, 8, 0x000000, 0.15)
      .setDepth(5);

    // ========== DESTINATION DOORS/BUILDINGS ==========
    DESTINATIONS.forEach((dest, idx) => {
      const doorGroup = this.add.container(dest.x, dest.y).setDepth(15 + idx * 2);

      // Main building body
      const buildingW = 90;
      const buildingH = 110;
      const building = this.add
        .rectangle(0, 0, buildingW, buildingH, dest.color)
        .setOrigin(0.5, 0.5);

      // Roof (triangle)
      const roofPoints = [[-buildingW / 2, 0], [buildingW / 2, 0], [0, -25]];
      const roof = this.add.polygon(0, -buildingH / 2 - 12, roofPoints, dest.accentColor).setOrigin(0.5, 0.5);

      // Door frame
      const doorW = 40;
      const doorH = 60;
      const doorFrame = this.add
        .rectangle(0, 15, doorW, doorH, 0x3D2817)
        .setOrigin(0.5, 0.5);

      // Door panel (interactive)
      const door = this.add
        .rectangle(0, 15, doorW - 6, doorH - 6, 0x5A3A1A)
        .setOrigin(0.5, 0.5)
        .setInteractive();

      door.setScrollFactor(0);
      door.destinationId = dest.id;
      door.destinationLabel = dest.label;
      door.parentContainer = doorGroup;

      // Door handle
      this.add.circle(doorW / 2 - 8, 15, 3, 0xD4AF37).setOrigin(0.5, 0.5);

      // Window
      this.add.rectangle(-doorW / 2 + 15, -15, 20, 20, 0x87CEEB, 0.6).setOrigin(0.5, 0.5);

      // Label above door
      const labelText = this.add
        .text(0, -buildingH / 2 - 35, dest.label, {
          font: 'bold 16px Arial',
          fill: '#2D1810',
          align: 'center',
          wordWrap: { width: 120 },
        })
        .setOrigin(0.5, 1)
        .setDepth(16);

      // Description
      const descText = this.add
        .text(0, buildingH / 2 + 20, dest.description, {
          font: '12px Arial',
          fill: '#5A3A1A',
          align: 'center',
          wordWrap: { width: 90 },
        })
        .setOrigin(0.5, 0)
        .setDepth(16);

      // Hover effects
      door.on('pointerover', () => {
        building.setFillStyle(dest.accentColor, 1);
        door.setFillStyle(dest.accentColor, 0.8);
        labelText.setStyle({ fill: '#D4A574' });
        doorGroup.setScale(1.05);
      });

      door.on('pointerout', () => {
        building.setFillStyle(dest.color, 1);
        door.setFillStyle(0x5a3a1a, 1);
        labelText.setStyle({ fill: '#2D1810' });
        doorGroup.setScale(1);
      });

      // Click/tap
      door.on('pointerdown', () => {
        this.selectDestination(dest.id, dest.label);
      });

      doorGroup.add([building, roof, doorFrame, door]);

      this.destinationZones.push({ door, building, doorGroup, label: dest.label, id: dest.id });
    });

    // ========== DECORATIVE ELEMENTS ==========

    // Flowers/bushes
    this.add
      .circle(120, height * 0.68, 15, 0x228B22, 0.6)
      .setDepth(8);
    this.add
      .circle(width - 140, height * 0.7, 12, 0x228B22, 0.5)
      .setDepth(8);

    // Info text
    this.add
      .text(width / 2, height * 0.95, '🎮 Click a door to explore • Use arrow keys to move', {
        font: '13px Arial',
        fill: '#8B5A00',
        align: 'center',
        backgroundColor: '#F5DEB3',
        padding: { x: 12, y: 6 },
        borderRadius: { tl: 4, tr: 4, bl: 4, br: 4 },
      })
      .setOrigin(0.5, 1)
      .setDepth(20);

    // ========== KEYBOARD INPUT ==========
    this.keys = this.input.keyboard.addKeys({
      up: Phaser.Input.Keyboard.KeyCodes.UP,
      down: Phaser.Input.Keyboard.KeyCodes.DOWN,
      left: Phaser.Input.Keyboard.KeyCodes.LEFT,
      right: Phaser.Input.Keyboard.KeyCodes.RIGHT,
      w: Phaser.Input.Keyboard.KeyCodes.W,
      a: Phaser.Input.Keyboard.KeyCodes.A,
      s: Phaser.Input.Keyboard.KeyCodes.S,
      d: Phaser.Input.Keyboard.KeyCodes.D,
      one: Phaser.Input.Keyboard.KeyCodes.ONE,
      two: Phaser.Input.Keyboard.KeyCodes.TWO,
      three: Phaser.Input.Keyboard.KeyCodes.THREE,
    });

    // Keyboard shortcuts
    this.input.keyboard.on('keydown', event => {
      const destMap = { '1': 0, '2': 1, '3': 2 };
      if (destMap[event.key]) {
        const dest = DESTINATIONS[destMap[event.key]];
        this.selectDestination(dest.id, dest.label);
      }
    });

    console.log('🎮 NeighborhoodScene ready! Click a door to begin your journey.');
  }

  update() {
    if (!this.character) return;

    const { width, height } = this.cameras.main;
    const moveX =
      Number(this.keys.right.isDown || this.keys.d.isDown) -
      Number(this.keys.left.isDown || this.keys.a.isDown);
    const moveY =
      Number(this.keys.down.isDown || this.keys.s.isDown) -
      Number(this.keys.up.isDown || this.keys.w.isDown);

    // Move character
    if (moveX !== 0 || moveY !== 0) {
      const length = Math.sqrt(moveX * moveX + moveY * moveY);
      this.character.x += (moveX / length) * this.moveSpeed * (1 / 60);
      this.character.y += (moveY / length) * this.moveSpeed * (1 / 60);

      // Boundaries
      this.character.x = Phaser.Math.Clamp(this.character.x, 40, width - 40);
      this.character.y = Phaser.Math.Clamp(this.character.y, 40, height - 40);
    }
  }

  selectDestination(destinationId, label) {
    if (this.selectedDestination === destinationId) return;

    this.selectedDestination = destinationId;

    // Visual feedback: screen flash and shake
    this.cameras.main.shake(150, 0.02);

    // Emit to React
    if (this.game.destinationCallback) {
      this.game.destinationCallback({
        type: 'DESTINATION_SELECTED',
        destinationId,
        label,
      });
    }
  }

  shutdown() {
    this.input.keyboard.removeAllListeners();
  }
}
