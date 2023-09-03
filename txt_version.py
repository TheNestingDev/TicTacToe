import os
import colorama

# player infos
PLAYER_O= "O"
PLAYER_X= "X"
FIELD_EMPTY = " "

# deco
colorama.init()
color = colorama.Fore

PLAYER_X_COLOR = color.BLUE
PLAYER_O_COLOR = color.MAGENTA
FIELD_COLOR = color.GREEN

# game flags
GAME_ACTIVE = object()
GAME_WON = object()
GAME_DRAW = object()

class Field:
    def clear_screen(self):
        os.system("cls")

    def create_field(self):
        field = []
        for _ in range(3):
            field.append([FIELD_EMPTY]*3)

        self.field = field

    def setup(self):
        self.create_field()
        self.current_player = PLAYER_X
        self.game_state = GAME_ACTIVE

    def draw(self):
        green = FIELD_COLOR
        rst = color.RESET

        self.clear_screen()
        print(green, "-"*13, rst, sep="")
        for row in self.field:
            line = ""
            for c in row:
                player_color = PLAYER_O_COLOR if c == PLAYER_O else PLAYER_X_COLOR
                line += f" {player_color}{c} {green}|"

            print(f"{green}|{rst}", line, sep="")
            print(green, "-"*13, rst, sep="")
        print("")

    def switch_player(self):
        if self.current_player == PLAYER_O:
            self.current_player = PLAYER_X
        else:
            self.current_player = PLAYER_O

    def check_input(self):
        print(f"PLAYER: {self.current_player}")
        player_input = input("> ")

        if len(player_input) != 2:
            self.switch_player()
            return

        if not player_input.isdigit():
            self.switch_player()
            return

        target_index_x = int(player_input[0])-1
        target_index_y = int(player_input[1])-1
        target_x_invalid = 0 < target_index_x > 2
        target_y_invalid = 0 < target_index_y > 2
        if target_x_invalid or target_y_invalid:
            self.switch_player()
            return

        if self.field[target_index_y][target_index_x] != FIELD_EMPTY:
            self.switch_player()
            return

        self.field[target_index_y][target_index_x] = self.current_player
        self.switch_player()

    def check_game_winner(self):
        """has one player won already? update the game_state accordingly"""
        win_chases = []

        # horizontals
        win_chases.extend(self.field)

        # verticals
        for i in range(3):
            win_chases.append([self.field[0][i], self.field[1][i], self.field[2][i]])

        # diagonals
        win_chases.append([self.field[0][0], self.field[1][1], self.field[2][2]])
        win_chases.append([self.field[0][2], self.field[1][1], self.field[2][0]])

        for win in win_chases:
            if not win[0] == win[1] == win[2]:
                continue

            if win[0] == FIELD_EMPTY:
                continue

            self.game_state = GAME_WON

    def check_game_draw(self):
        """is the game a draw? update the game_state accordingly"""
        if not self.game_state == GAME_ACTIVE:
            return

        check_result = []
        for row in self.field:
            check_result.append(FIELD_EMPTY in row)

        if not any(check_result):
            self.game_state = GAME_DRAW

    def show_game_state(self):
        """show the game result who won or if its a draw"""
        self.switch_player() # we need to switch the player again to show the right player
        if self.game_state == GAME_WON:
            print(f"\n{color.GREEN}PLAYER {color.MAGENTA}{self.current_player}{color.GREEN} HAS WON{color.RESET}")
        else:
            print(f"\n{color.YELLOW}NO WINNER EXISTS HA{color.RESET}")

    def run(self):
        while self.game_state == GAME_ACTIVE:
            self.draw()
            self.check_input()
            self.check_game_winner()
            self.check_game_draw()

        self.draw()
        self.show_game_state()

def main():
    field = Field()
    play_again = "1"

    while play_again == "1":
        field.setup()
        field.run()
        play_again = input("enter 1 to play again: ")

if __name__ == "__main__":
    main()