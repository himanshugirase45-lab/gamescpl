# SlingShot Adventure

A desktop slingshot game inspired by Angry Birds, developed in Python with Pygame and Pymunk.

## Installation

1. Make sure you have Python installed.
2. Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Running the Game

Run the game with the following command:

```bash
python main.py
```

## Controls

- **Mouse:** Click and drag the bird on the slingshot backwards to aim. Release to launch.
- **Space:** Press during flight when launching the yellow "Speed" bird to activate its speed boost ability.
- **UI Interaction:** Use the mouse to click buttons for menus, pausing, and restarting.

## Troubleshooting

- **Missing Dependencies:** If the game fails to start, ensure `pygame-ce` and `pymunk` are correctly installed. Use the requirements provided in the folder.
- **Audio Error (Not applicable):** This version procedurally generates visuals. If you choose to add sounds later and run into mixer issues, check the `pygame.mixer` initialization block (currently disabled to ensure stability across systems).
- **Display Scaling:** The game uses `pygame.SCALED`. Resizing the window preserves aspect ratio automatically.
