import * as Phaser from 'phaser'

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot')
  }

  preload() {
    const g = this.make.graphics({ x: 0, y: 0 }, false)
    g.fillStyle(0xffe066, 1)
    g.fillRect(0, 0, 16, 16)
    g.fillStyle(0x1f2937, 1)
    g.fillRect(4, 4, 3, 3)
    g.fillRect(9, 4, 3, 3)
    g.fillStyle(0x1f2937, 1)
    g.fillRect(5, 10, 6, 2)
    g.generateTexture('librarian', 16, 16)
    g.destroy()
  }

  create() {
    this.scene.start('Library')
  }
}
