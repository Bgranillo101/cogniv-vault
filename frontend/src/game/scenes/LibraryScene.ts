import * as Phaser from 'phaser'

const SPEED = 120

export class LibraryScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys

  constructor() {
    super('Library')
  }

  create() {
    this.add
      .text(12, 8, 'Library — arrow keys to move', {
        fontFamily: 'monospace',
        fontSize: '12px',
        color: '#9ca3af',
      })
      .setScrollFactor(0)

    this.player = this.physics.add.sprite(320, 200, 'librarian')
    this.player.setScale(3)
    this.player.setCollideWorldBounds(true)

    this.cursors = this.input.keyboard!.createCursorKeys()
  }

  update() {
    const body = this.player.body as Phaser.Physics.Arcade.Body
    body.setVelocity(0)

    if (this.cursors.left?.isDown) body.setVelocityX(-SPEED)
    else if (this.cursors.right?.isDown) body.setVelocityX(SPEED)

    if (this.cursors.up?.isDown) body.setVelocityY(-SPEED)
    else if (this.cursors.down?.isDown) body.setVelocityY(SPEED)
  }
}
