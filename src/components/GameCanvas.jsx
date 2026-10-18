import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { getGameConfig } from '../game/gameConfig.js';

export function GameCanvas({ onDestinationSelected }) {
  const containerRef = useRef(null);
  const gameRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create Phaser game instance
    const config = getGameConfig(onDestinationSelected);
    const game = new Phaser.Game({
      ...config,
      parent: containerRef.current,
    });

    gameRef.current = game;

    // Cleanup on unmount
    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, [onDestinationSelected]);

  return (
    <div
      ref={containerRef}
      className="w-full flex-1"
      style={{
        background: 'linear-gradient(180deg, #87CEEB 0%, #E0F6FF 50%, #F5DEB3 100%)',
        overflow: 'hidden',
      }}
    />
  );
}
