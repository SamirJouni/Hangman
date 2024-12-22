'''
Prepared class and methods for a hangman game.
'''
import os
import threading
import random
import tkinter as tk
from tkinter import ttk, Canvas
import tkinter.messagebox as messagebox
import json
from functools import partial
from playsound import playsound


class HangmanGame():
    '''
    Class representation of a classic hangman game.
    '''
    # Predefined game possible status
    IN_PROGRESS = 'in_progress'
    WIN = 'win'
    LOSE = 'lose'

    def __init__(self, wordlist, allowed_fails, master):
        '''
        Initialize the game. The hidden word gets selected from a given list
        of words.

        Args:
            wordlist: List of all possible hidden words
            num_tries: Number of failed attempts allowed
        '''
        # Game Logic
        self.censored = ""
        self.allowed_fails = allowed_fails
        self.hidden_word = random.choice(wordlist).casefold()
        self.word_length = len(self.hidden_word)
        self.status = self.IN_PROGRESS
        self.screen = ""
        self.fails = ""

        # GUI
        self.master = master
        self.master.title("HANGMAN")
        self.master.geometry("900x600")
        self.master.config(cursor="hand2", bg="#274c43")
        if "nt" == os.name:
            self.master.iconbitmap(r'./hangman-icon.ico')
        else:
            try:
                icon = tk.PhotoImage(file='hangman_icon.png')
                self.master.call('wm', 'iconphoto', self.master._w, icon)
            except Exception as e:
                print(f"Error setting icon: {e}")
        self.hangman_canvas = Canvas()
        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')
        # Load settings button icon
        self.settings_img = tk.PhotoImage(
            file="./settings.png"
            )
        # Game Title Style Config
        self.style.configure('TLabel',
                             background="#274c43",
                             foreground='white',
                             font=("Papyrus", 39),
                             justify="center"
                             )
        # Start Game Button Style Config
        self.style.configure('TButton',
                             relief='flat',
                             focuscolor='',
                             anchor="center",
                             font=("Papyrus", 20)
                             )
        self.style.map("TButton",
                       foreground=[('!active', 'white'), ('pressed', 'black'),
                                   ('active', '#D7D7D7')],
                       background=[('!active', '#305D52'),
                                   ('pressed', '#274C43'),
                                   ('active', '#49907F')])
        # Settings button style
        self.style.configure('s.TButton',
                             relief='flat',
                             focuscolor='',
                             anchor="center",
                             font=("Papyrus", 15)
                             )
        self.style.map("s.TButton",
                       foreground=[('!active', 'white'), ('pressed', 'black'),
                                   ('active', '#D7D7D7')],
                       background=[('!active', '#274c43'),
                                   ('pressed', '#274C43'),
                                   ('active', '#49907F')])

    def draw_head(self):
        """
            Draw head of unfortunate person
        """
        self.hangman_canvas.create_oval(125, 50, 185, 110, outline="white")

    def draw_body(self):
        """
            Draw body of unfortunate person
        """
        self.hangman_canvas.create_line(155, 110, 155, 170, fill="white")

    def draw_left_arm(self):
        """
            Draw left arm of unfortunate person
        """
        self.hangman_canvas.create_line(155, 130, 125, 150, fill="white")

    def draw_right_arm(self):
        """
            Draw right arm of unfortunate person
        """
        self.hangman_canvas.create_line(155, 130, 185, 150, fill="white")

    def draw_left_leg(self):
        """
            Draw left leg of unfortunate person
        """
        self.hangman_canvas.create_line(155, 170, 125, 200, fill="white")

    def draw_right_leg(self):
        """
            Draw right leg of unfortunate person
        """
        self.hangman_canvas.create_line(155, 170, 185, 200, fill="white")

    def draw_face_alive(self):
        """
            Draw face of unfortunate person
        """
        self.hangman_canvas.create_line(140, 70, 150, 80, fill="white")
        self.hangman_canvas.create_line(160, 70, 170, 80, fill="white")
        self.hangman_canvas.create_arc(140, 85, 170, 105, start=0, extent=-180,
                                       fill="white")

    def draw_face_dead(self):
        """
            Draw face of unfortunate person
        """
        self.hangman_canvas.create_oval(140, 70, 145, 75, outline="white")
        self.hangman_canvas.create_oval(165, 70, 170, 75, outline="white")
        self.hangman_canvas.create_arc(140, 85, 170, 105, start=0, extent=180,
                                       fill="white")

    def set_allowed_fails(self, up_down):
        """
            Changes allowed fails
        """
        match up_down:
            case "up":
                self.allowed_fails += 1
                update = {
                    "allowed_fails": self.allowed_fails
                }
                new_settings = json.dumps(update, indent=4)
                with open("./settings.json",
                          "w", -1, "UTF8") as s:
                    s.write(new_settings)

            case "down":
                self.allowed_fails -= 1
                update = {
                    "allowed_fails": self.allowed_fails
                }
                new_settings = json.dumps(update, indent=4)
                with open("./settings.json",
                          "w", -1, "UTF8") as s:
                    s.write(new_settings)
        self.settings_screen()

    def play_sound(self, sound: str):
        """
            Plays sound effects
        """
        try:
            playsound(f"./sounds/{sound}.wav")
        except Exception as e:
            print(f"Error playing sound: {sound} \n {e}")

    def detect_keypress(self, event):
        """
            Detects keypressed on keyboard
        """
        user_input = event.char
        if user_input.isalpha() and self.screen == "game":
            # update user_input
            self.guess_letter(letter=user_input)
            self.update_game()
        elif event.keysym == "Return" and self.screen == "start":
            self.update_game()
        elif event.keysym == "Escape":
            self.master.destroy()
        self.check_win_lose()

    def check_win_lose(self):
        """
            Checks for win or lose
        """
        self.get_status()
        # Detect win/lose
        if self.status == self.WIN:
            threading.Thread(target=self.play_sound, args=("win",)).start()
            messagebox.showinfo(message="You Won!", title="HANGMAN")
            self.reset()
        elif self.status == self.LOSE:
            threading.Thread(
                target=self.play_sound, args=("die_lose",)).start()
            messagebox.showinfo(message="You Lost!", title="HANGMAN")
            self.reset()

    def start_screen(self):
        """
            Start Screen
        """
        # Delete previous Screen
        for widget in self.master.winfo_children():
            widget.destroy()
        self.screen = "settings"
        # Settings Button
        settings_button = ttk.Button(self.master,
                                     command=self.settings_screen,
                                     image=self.settings_img,
                                     style='s.TButton'
                                     )
        settings_button.pack(anchor="ne", padx=35, pady=35)

        self.screen = "start"
        # Game Title
        game_name = ttk.Label(self.master,
                              text='HANGMAN',
                              style='TLabel'
                              )
        game_name.pack(padx=100, pady=75)

        # Start Game Button
        start_button = ttk.Button(self.master,
                                  text="Start Game!",
                                  command=self.update_game,
                                  style='TButton',
                                  cursor="man"
                                  )
        start_button.pack(padx=20, pady=20)

    def settings_screen(self):
        """
            Change game settings
        """
        # Delete previous Screen
        for widget in self.master.winfo_children():
            widget.destroy()
        self.screen = "settings"
        # Main Menu Button
        menu_button = ttk.Button(self.master,
                                 text="Main Menu",
                                 command=self.start_screen,
                                 style='TButton'
                                 )
        menu_button.pack(anchor="ne", padx=20, pady=20)

        # Show allowed fail guesses
        fails = ttk.Label(
            self.master,
            style='TLabel',
            text="Allowed Fails: " + str(self.allowed_fails)
        )
        fails.pack(anchor="center", padx=20, pady=(100, 0))

        # plus minus button
        down_button = ttk.Button(self.master,
                                 text="-",
                                 command=partial(self.set_allowed_fails,
                                                 "down"),
                                 style='TButton'
                                 )
        down_button.pack(side=tk.LEFT, padx=(200, 0), pady=(0, 200))

        up_button = ttk.Button(self.master,
                               text="+",
                               command=partial(self.set_allowed_fails, "up"),
                               style='TButton'
                               )
        up_button.pack(side=tk.RIGHT, padx=(0, 200), pady=(0, 200))

    def update_game(self):
        """
            Updates game
        """
        # Delete previous Screen
        for widget in self.master.winfo_children():
            widget.destroy()
        self.screen = "game"
        # Noose Representation
        self.hangman_canvas = Canvas(self.master, width=300,
                                     height=300, bg="#274c43",
                                     highlightthickness=0, relief="ridge")
        self.hangman_canvas.pack(anchor="nw", pady=5)
        if self.allowed_fails >= 0:
            self.hangman_canvas.create_line(70, 20, 70, 250, fill="white",
                                            width=3)
            self.hangman_canvas.create_line(70, 20, 154, 20, fill="white",
                                            width=3)
            self.hangman_canvas.create_line(154, 20, 154, 50, fill="white",
                                            width=3, dash=(5, 1))
        # Draw Man
        self.draw_man()

        # Word representation
        word = ttk.Label(
            self.master,
            style='TLabel',
            text=" ".join(self.censored)
                            )
        word.pack(anchor="s", padx=20, pady=20)

        # Show fail guesses
        fails = ttk.Label(
            self.master,
            style='TLabel',
            text="Fails:"
        )
        fails.pack(anchor="center", padx=20, pady=0)
        fail_chars = ttk.Label(
            self.master,
            style='TLabel',
            text=" ".join(self.fails)
        )
        fail_chars.pack(anchor="center", padx=20, pady=0)

    def guess_letter(self, letter: str):
        '''
        Gets called when the user guesses a letter. Checks if the letter is
        contained in the guessed words and uncovers all of it's appearances.

        Args:
            letter: Guessed letter from user

        Returns:
            bool: If the guessed letter is contained in the hidden word
            string: String with all letters uncovered that have been guessed
            int: Number of remaining fail attempts
        '''
        letter = letter.casefold()
        # Correctly guessed
        if letter in self.hidden_word:
            indexes = [index for index, char in enumerate(self.hidden_word)
                       if char == letter]
            if letter not in self.censored:
                threading.Thread(target=self.play_sound,
                                 args=("correct",)).start()
            for x in indexes:
                self.censored = self.censored[:x
                                              ] + letter + self.censored[x+1:]
            return True, self.censored, self.allowed_fails
        # Wrong guess
        else:
            self.allowed_fails -= 1
            threading.Thread(target=self.play_sound, args=("wrong",)).start()
            self.fails += letter
            return False, self.censored, self.allowed_fails

    def draw_man(self):
        """
            Draws another part of the unfortunate man on each wrong guess
        """
        match self.allowed_fails:
            case 5:
                self.draw_head()
                self.draw_face_alive()
            case 4:
                self.draw_head()
                self.draw_body()
                self.draw_face_alive()
            case 3:
                self.draw_head()
                self.draw_body()
                self.draw_left_arm()
                self.draw_face_alive()
            case 2:
                self.draw_head()
                self.draw_body()
                self.draw_left_arm()
                self.draw_right_arm()
                self.draw_face_alive()
            case 1:
                self.draw_head()
                self.draw_body()
                self.draw_left_arm()
                self.draw_right_arm()
                self.draw_left_leg()
                self.draw_face_alive()
            case 0:
                self.draw_head()
                self.draw_body()
                self.draw_left_arm()
                self.draw_right_arm()
                self.draw_left_leg()
                self.draw_right_leg()
                self.draw_face_dead()

    def get_status(self):
        '''
        Returns the status of the game.
        IN_PROGESS: Solution not yet found
        WIN: Solution found, all letters guessed
        LOSE: Reached allowed fail attempts without finding a solution

        Returns:
            Current game status as a string
        '''
        if "_" not in self.censored:
            self.status = self.WIN
        elif self.allowed_fails == 0:
            self.status = self.LOSE

    def reset(self):
        """
            Resets game parameters
        """
        self.status = self.IN_PROGRESS
        self.master.destroy()


def main():
    '''
    Main function handling inputs and returns.
    '''
    while True:
        # Start GUI Window
        root = tk.Tk()
        # Import words from file
        with open("./words.txt", "rt", -1, "UTF8") as w:
            words = w.read()
        # Import settings
        with open("./settings.json", "rt", -1, "UTF8") as s:
            settings = json.load(s)
        # Initialize instance
        hangman_game = HangmanGame(
            wordlist=words.split(", "),
            allowed_fails=settings['allowed_fails'],
            master=root
            )
        # Initiate Start Screen
        hangman_game.start_screen()
        root.bind("<Key>", hangman_game.detect_keypress)
        # Print censored word
        hangman_game.censored = "_" * hangman_game.word_length
        root.mainloop()
        hangman_game.get_status()
        if hangman_game.status in ('win', 'lose'):
            continue
        break


if __name__ == '__main__':
    main()
