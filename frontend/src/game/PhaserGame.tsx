import { useEffect, useRef } from 'react'
import * as Phaser from 'phaser'
import { BootScene } from './scenes/BootScene'
import { LibraryScene } from './scenes/LibraryScene'

const WIDTH = 640
const HEIGHT = 400

export function PhaserGame() {
  const containerRef = useRef<HTMLDivElement>(null)
  const gameRef = useRef<Phaser.Game | null>(null)

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return

    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      width: WIDTH,
      height: HEIGHT,
      parent: containerRef.current,
      backgroundColor: '#0f1320',
      pixelArt: true,
      scene: [BootScene, LibraryScene],
      physics: {
        default: 'arcade',
        arcade: { debug: false },
      },
    })

    return () => {
      gameRef.current?.destroy(true)
      gameRef.current = null
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="mx-auto overflow-hidden rounded-lg border border-neutral-800 shadow-lg"
      style={{ width: WIDTH, height: HEIGHT }}
    />
  )
}
