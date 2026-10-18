import Phaser from 'phaser';
import { NeighborhoodScene } from './scenes/NeighborhoodScene.js';

export const getGameConfig = (onDestinationSelected) => ({
  type: Phaser.AUTO,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: 1200,
    height: 800,
    min: {
      width: 320,
      height: 240,
    },
    max: {
      width: 1920,
      height: 1440,
    },
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 0 },
      debug: false,
    },
  },
  scene: [NeighborhoodScene],
  callbacks: {
    preBoot: (game) => {
      // Store the callback in the game instance for scenes to access
      game.destinationCallback = onDestinationSelected;
    },
  },
  // Disable some default Phaser features for lighter bundle
  input: {
    keyboard: true,
    mouse: true,
    touch: true,
  },
  render: {
    pixelArt: false,
    antialias: true,
  },
});
