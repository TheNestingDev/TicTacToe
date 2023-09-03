from __future__ import annotations
import pygame
import sys

pygame.init()

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600

PLAYER_O = "O"
PLAYER_X = "X"
GAME_ACTIVE = object()
GAME_WON = object()
GAME_DRAW = object()

MAX_FPS = 60

class Field:
    def __init__(self, screen, field_id:tuple, pos:tuple, size:tuple, game:Game):
        self.game = game
        self.screen = screen
        self.field_id = field_id

        self.pos = pos
        self.size = size
        self.center_pos = self.get_center()

        self.body = pygame.Rect(*pos, *size)
        self.color = (255, 0, 0)

        self.state = None

    def get_center(self):
        half_width = self.size[0]/2
        half_height= self.size[1]/2
        x, y = self.pos
        return (x+half_width, y+half_height)

    def check(self, mouse_pressed:bool, mouse_pos:tuple):
        if not mouse_pressed:
            return

        mouse_x, mouse_y = mouse_pos
        my_x, my_y = self.pos
        width, height = self.size

        if mouse_x < my_x:
            return
        if mouse_x > my_x+width:
            return

        if mouse_y < my_y:
            return
        if mouse_y > my_y+height:
            return

        if self.game.game_state != GAME_ACTIVE:
            self.game.field_event(self)
            return

        if self.state is not None:
            return

        self.state = self.game.current_player
        self.game.field_event(self)

    def draw_mark_x(self):
        pygame.draw.line(self.screen, (0, 0, 255),
                         self.pos, (self.pos[0]+self.size[0], self.pos[1]+self.size[1]), 15)
        pygame.draw.line(self.screen, (0, 0, 255),
                         (self.pos[0]+self.size[0], self.pos[1]),
                         (self.pos[0], self.pos[1]+self.size[1]), 15)

    def draw_mark_circle(self):
        pygame.draw.circle(self.screen, (0, 0, 255), self.center_pos, 70)

    def draw_mark(self):
        if self.state == PLAYER_O:
            self.draw_mark_circle()
        elif self.state == PLAYER_X:
            self.draw_mark_x()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.body)
        self.draw_mark()

class Game:
    def create_fields(self):
        result = {}
        pos_x = 50
        pos_y = 50
        width = 150
        height = 150

        for y in range(3):
            for x in range(3):
                field_id = f"{x}{y}"
                field = Field(self.screen, field_id, (pos_x, pos_y), (width, height), self)
                result[field_id] = field

                pos_x += width + 10

            pos_y += height + 10
            pos_x = 50

        return result

    def __init__(self):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("TicTacToe")

        self.delta_time = 1
        self.font = pygame.font.Font(None, 30)

        self.fields = self.create_fields()

    def setup(self):
        self.current_player = PLAYER_X
        self.game_state = GAME_ACTIVE
        self.old_mouse_state = False
        self.after_game_lock = False

        for field in self.fields.values():
            field.state = None

    def mouse_state_changed(self):
        new_mouse_state = pygame.mouse.get_pressed()[0]
        old_mouse_state = self.old_mouse_state
        self.old_mouse_state = new_mouse_state
        return not new_mouse_state and old_mouse_state

    def show_txt(self, text:str, pos:tuple):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, pos)

    def draw(self, scr):
        for field in self.fields.values():
            field.draw()

        if self.game_state == GAME_ACTIVE:
            self.show_txt(f"Current Player: {self.current_player}", (550, 50))
        elif self.game_state == GAME_WON:
            self.show_txt(f"PLAYER {self.current_player} HAS WON", (550, 50))
        elif self.game_state == GAME_DRAW:
            self.show_txt(f"NO WINNER EXISTS...", (550, 50))

        if self.game_state != GAME_ACTIVE:
            self.show_txt("Please press any", (550, 90))
            self.show_txt("field to play again!", (550, 110))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def switch_player(self):
        if self.current_player == PLAYER_O:
            self.current_player = PLAYER_X
        else:
            self.current_player = PLAYER_O

    def field_event(self, field:Field):
        if self.game_state != GAME_ACTIVE:
            self.setup()
            return

        self.switch_player()

    def check_game_winner(self):
        win_chases = []

        # horizontals
        for i in range(3):
            win_chases.append([self.fields[str(i)+"0"], self.fields[str(i)+"1"], self.fields[str(i)+"2"]])

        # verticals
        for i in range(3):
            win_chases.append([self.fields["0"+str(i)], self.fields["1"+str(i)], self.fields["2"+str(i)]])

        # diagonals
        win_chases.append([self.fields["00"], self.fields["11"], self.fields["22"]])
        win_chases.append([self.fields["02"], self.fields["11"], self.fields["20"]])

        for win in win_chases:
            if not win[0].state == win[1].state == win[2].state:
                continue

            if win[0].state is None:
                continue

            self.game_state = GAME_WON
            self.after_lock()
            self.switch_player()

    def check_game_draw(self):
        if not self.game_state == GAME_ACTIVE:
            return

        check_result = []
        for y in range(3):
            row = []
            for x in range(3):
                row.append(self.fields[f"{x}{y}"].state)
            check_result.append(None in row)

        if not any(check_result):
            self.game_state = GAME_DRAW
            self.after_lock()

    def update(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        for field in self.fields.values():
            field.check(mouse_pressed, mouse_pos)

        if self.game_state != GAME_ACTIVE:
            return

        self.check_game_winner()
        self.check_game_draw()

    def run(self):
        while True:
            self.handle_events()
            self.update()

            self.screen.fill((0, 0, 0))
            self.draw(self.screen)
            pygame.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)


def main():
    game = Game()
    game.setup()
    game.run()

if __name__ == "__main__":
    main()
