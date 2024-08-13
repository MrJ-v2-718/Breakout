# MrJ
# Breakout
# 7/25/2024


import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import json
import os
import pygame

# Path to high score file
HIGH_SCORE_FILE = 'high_scores.json'

# Initialize pygame for sound effects
pygame.init()
SOUND_ENABLED = True

# Load sound effects
try:
    PADDLE_HIT_SOUND = pygame.mixer.Sound('sound_effects/paddle_hit.wav')
    WALL_HIT_SOUND = pygame.mixer.Sound('sound_effects/wall_hit.wav')
    BRICK_HIT_SOUND = pygame.mixer.Sound('sound_effects/brick_hit.wav')
    WIN_SOUND = pygame.mixer.Sound('sound_effects/win.wav')
    LOSE_SOUND = pygame.mixer.Sound('sound_effects/lose.wav')
except pygame.error as e:
    SOUND_ENABLED = False
    print(f"Warning: {e}")


def view_help():
    messagebox.showinfo(
        "Help",
        "Select Start Game in the Game menu to start playing or check out the high scores. "
        "Select your preferred difficulty in the Difficulty menu. "
        "Enjoy the game!"
    )


def show_about():
    messagebox.showinfo(
        "About",
        "Breakout - A Classic Video Game\n"
        f"\tCreated by MrJ\n\t        2024©"
    )


class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Breakout")

        # Make the mouse cursor invisible
        self.root.config(cursor="none")

        # High Scores
        self.high_scores = self.load_high_scores()

        # Game settings
        self.speed = tk.StringVar(value="Normal")
        self.game_over = False
        self.score = 0

        # Create UI components
        self.create_ui()

        # Initialize game elements
        self.create_game_elements()

    def create_ui(self):
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="Start Game", command=self.start_game)
        game_menu.add_command(label="View High Scores", command=self.view_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.root.quit)

        # Difficulty menu
        difficulty_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Difficulty", menu=difficulty_menu)
        difficulty_menu.add_radiobutton(label="Easy", variable=self.speed, value="Easy")
        difficulty_menu.add_radiobutton(label="Normal", variable=self.speed, value="Normal")
        difficulty_menu.add_radiobutton(label="Hard", variable=self.speed, value="Hard")

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View Help", command=view_help)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=show_about)

        # Canvas for the game
        self.canvas = tk.Canvas(self.root, bg='black', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Score label
        self.score_label = tk.Label(
            self.root,
            text=f"Score: {self.score}",
            font=("Arial", 14),
            background="black",
            foreground="white"
        )
        self.score_label.pack(side=tk.TOP, fill=tk.X)

        self.root.bind('<Motion>', self.mouse_move)
        self.root.bind('<Key>', self.key_press)

    def create_game_elements(self):
        self.paddle = self.canvas.create_rectangle(350, 580, 450, 590, fill='white')
        self.ball = self.canvas.create_oval(390, 570, 410, 590, fill='white')
        self.bricks = []
        self.text_id = None
        self.create_bricks()

    def create_bricks(self):
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'cyan']
        brick_height = 20
        brick_spacing = 5
        rows = 8
        start_y = 5

        # Set maximum brick length
        max_brick_length = 200

        for row in range(rows):
            x_offset = 5
            y_offset = start_y + (brick_height + brick_spacing) * row
            total_width = 800 - x_offset * 2
            num_bricks = random.randint(6, 15)
            # Pass the maximum brick length to generate_brick_lengths
            brick_lengths = self.generate_brick_lengths(total_width, num_bricks, brick_spacing, max_brick_length)

            for brick_length in brick_lengths:
                color = random.choice(colors)
                brick = self.canvas.create_rectangle(x_offset, y_offset, x_offset + brick_length,
                                                     y_offset + brick_height, fill=color)
                self.bricks.append(brick)
                x_offset += brick_length + brick_spacing

    def generate_brick_lengths(self, total_width, num_bricks, spacing, max_length):
        lengths = []
        remaining_width = total_width - spacing * (num_bricks - 1)
        min_length = 50

        if remaining_width <= min_length * num_bricks:
            return [min_length] * num_bricks

        for _ in range(num_bricks):
            # Ensure max_length is integer and within the range
            max_length = int(min(max_length, remaining_width - (num_bricks - 1) * min_length))
            if max_length < min_length:
                max_length = min_length
            length = random.randint(min_length, max_length)
            lengths.append(length)
            remaining_width -= length

        if remaining_width > 0:
            lengths[-1] += remaining_width

        return lengths

    def start_game(self):
        if self.text_id:
            self.canvas.delete(self.text_id)
            self.text_id = None
        self.ball_speed = {'Easy': 10, 'Normal': 15, 'Hard': 20}[self.speed.get()]
        self.dx = self.ball_speed
        self.dy = -self.ball_speed
        self.score = 0
        self.game_over = False
        self.update_score()
        self.reset_bricks()
        self.reset_ball_position()
        self.play_game()

    def reset_ball_position(self):
        self.canvas.coords(self.ball, 390, 570, 410, 590)

    def play_game(self):
        if not self.game_over:
            self.move_ball()
            self.check_collisions()
            self.root.after(50, self.play_game)

    def move_ball(self):
        self.canvas.move(self.ball, self.dx, self.dy)
        ball_pos = self.canvas.coords(self.ball)
        if ball_pos[0] <= 0 or ball_pos[2] >= 800:
            self.dx = -self.dx
            if SOUND_ENABLED:
                WALL_HIT_SOUND.play()
        if ball_pos[1] <= 0:
            self.dy = -self.dy
            if SOUND_ENABLED:
                WALL_HIT_SOUND.play()
        if ball_pos[3] >= 600:
            if SOUND_ENABLED:
                LOSE_SOUND.play()
            self.end_game("You Lose")

    def check_collisions(self):
        ball_pos = self.canvas.coords(self.ball)
        paddle_pos = self.canvas.coords(self.paddle)

        if self.overlap(ball_pos, paddle_pos):
            self.dy = -self.dy
            if SOUND_ENABLED:
                PADDLE_HIT_SOUND.play()

        for brick in self.bricks:
            if self.overlap(ball_pos, self.canvas.coords(brick)):
                self.canvas.delete(brick)
                self.bricks.remove(brick)
                self.dy = -self.dy
                if SOUND_ENABLED:
                    BRICK_HIT_SOUND.play()
                self.score += 10
                self.update_score()
                if not self.bricks:
                    if SOUND_ENABLED:
                        WIN_SOUND.play()
                    self.end_game("You Win")
                break

    def overlap(self, pos1, pos2):
        return not (pos1[2] < pos2[0] or pos1[0] > pos2[2] or pos1[3] < pos2[1] or pos1[1] > pos2[3])

    def mouse_move(self, event):
        paddle_pos = self.canvas.coords(self.paddle)
        new_x = event.x
        if new_x < 50:
            new_x = 50
        if new_x > 750:
            new_x = 750
        self.canvas.coords(self.paddle, new_x - 50, paddle_pos[1], new_x + 50, paddle_pos[3])

    def key_press(self, event):
        paddle_pos = self.canvas.coords(self.paddle)
        if event.keysym in ['Left', 'A'] and paddle_pos[0] > 0:
            self.canvas.move(self.paddle, -20, 0)
        if event.keysym in ['Right', 'D'] and paddle_pos[2] < 800:
            self.canvas.move(self.paddle, 20, 0)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def end_game(self, message):
        self.game_over = True
        self.text_id = self.canvas.create_text(400, 300, text=message, font=("Arial", 24), fill="white")
        self.save_high_score()

    def reset_bricks(self):
        for brick in self.bricks:
            self.canvas.delete(brick)
        self.bricks = []
        self.create_bricks()

    def load_high_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                high_scores = json.load(file)
                # Validate the loaded data
                if isinstance(high_scores, list):
                    return [entry for entry in high_scores if
                            isinstance(entry, dict) and 'name' in entry and 'score' in entry]
        return []

    def save_high_score(self):
        if self.game_over:  # Ensure name is prompted only after game ends
            name = simpledialog.askstring("Name", "\tEnter your name:\t\t")
            if name:
                self.high_scores.append({"name": name, "score": self.score})
                self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)[:10]
                with open(HIGH_SCORE_FILE, 'w') as file:
                    json.dump(self.high_scores, file)

    def view_scores(self):
        scores_text = "\n".join([f"{entry['name']}: {entry['score']}" for entry in self.high_scores])
        messagebox.showinfo("High Scores", scores_text)


if __name__ == "__main__":
    root = tk.Tk()
    game = BreakoutGame(root)
    root.mainloop()
