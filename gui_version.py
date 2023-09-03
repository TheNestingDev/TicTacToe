from __future__ import annotations
import pygame
import sys

pygame.init()

SCREEN_SIZE = WIDTH, HEIGHT = 800, 600

PLAYER_O = "O"
PLAYER_X = "X"

PLAYER_X_COLOR = (50, 50, 80)
PLAYER_O_COLOR = (20, 50, 60)
FIELD_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (40, 40, 40)

MAX_ROUND_DURATION = 20
MAX_MOVE_DURATION = 5

GAME_ACTIVE = object()
GAME_WON = object()
GAME_DRAW = object()
GAME_TIMEOUT = object()

NORMAL_MODE = object()
CHALLENGE_MODE = object()

MAX_FPS = 60

class Settings:
    GAME_MODE = NORMAL_MODE

class Field:
    def __init__(self, screen, field_id:tuple, pos:tuple, size:tuple, game:GameView):
        self.game = game
        self.screen = screen
        self.field_id = field_id

        self.pos = pos
        self.size = size
        self.center_pos = self.get_center()

        self.body = pygame.Rect(*pos, *size)
        self.color = FIELD_COLOR

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
            self.game.field_click_event(self)
            return

        if self.state is not None:
            return

        self.state = self.game.current_player
        self.game.field_click_event(self)
        self.game.moves_played += 1
        self.game.move_timer = MAX_MOVE_DURATION

    def draw_mark_x(self):
        pygame.draw.line(self.screen, PLAYER_X_COLOR,
                         (self.pos[0]+7, self.pos[1]), (self.pos[0]+self.size[0]-7, self.pos[1]+self.size[1]), 15)
        pygame.draw.line(self.screen, PLAYER_X_COLOR,
                         (self.pos[0]+self.size[0]-7, self.pos[1]),
                         (self.pos[0]+7, self.pos[1]+self.size[1]), 15)

    def draw_mark_circle(self):
        pygame.draw.circle(self.screen, PLAYER_O_COLOR, self.center_pos, 85)
        pygame.draw.circle(self.screen, FIELD_COLOR, self.center_pos, 60)

    def draw_mark(self):
        if self.state == PLAYER_O:
            self.draw_mark_circle()
        elif self.state == PLAYER_X:
            self.draw_mark_x()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.body)
        self.draw_mark()

class View:
    def __init__(self, screen:pygame.Surface, clock:pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.delta_time = 1
        self.font = pygame.font.Font(None, 30)
        self.old_mouse_state = False

        self.change_menu = None

    def show_txt(self, text:str, pos:tuple):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, pos)

    def mouse_state_changed(self):
        new_mouse_state = pygame.mouse.get_pressed()[0]
        old_mouse_state = self.old_mouse_state
        self.old_mouse_state = new_mouse_state
        return not new_mouse_state and old_mouse_state

    def setup(self):
        self.old_mouse_state = False

    def draw(self, screen:pygame.Surface):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        pass

    def run(self):
        while True:
            self.handle_events()
            self.update()

            self.screen.fill(BACKGROUND_COLOR)
            self.draw(self.screen)
            pygame.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)

            if self.change_menu is not None:
                return self.change_menu

class GameView(View):
    def create_fields(self):
        result = {}
        pos_x = 20
        pos_y = 20
        width = 180
        height = 180

        for y in range(3):
            for x in range(3):
                field_id = f"{x}{y}"
                field = Field(self.screen, field_id, (pos_x, pos_y), (width, height), self)
                result[field_id] = field

                pos_x += width + 10

            pos_y += height + 10
            pos_x = 20

        return result

    def __init__(self, screen:pygame.Surface, clock:pygame.time.Clock):
        super().__init__(screen, clock)

        self.fields = self.create_fields()
        self.rounds_played = 0

    def setup(self):
        super().setup()

        self.current_player = PLAYER_X
        self.game_state = GAME_ACTIVE
        self.after_game_lock = True

        self.moves_played = 0
        self.rounds_played += 1
        self.general_timer = 0

        self.round_timer = MAX_ROUND_DURATION
        self.move_timer = MAX_MOVE_DURATION

        for field in self.fields.values():
            field.state = None

    def draw(self, scr):
        for field in self.fields.values():
            field.draw()

        if self.game_state == GAME_ACTIVE:
            self.show_txt(f"PLAYING MATCH {self.rounds_played}", (600, 20))
            self.show_txt(f"{self.moves_played} MOVES PLAYED", (600, 50))

            self.show_txt(f"Current Player: {self.current_player}", (600, 90))

            self.show_txt(f"GAME TIME LEFT:", (600, 130))
            self.show_txt(f"{int(self.round_timer)} sec.", (600, 150))
            self.show_txt(f"Move Timer:", (600, 180))
            self.show_txt(f"-- {int(self.move_timer)} sec. --", (600, 200))

        elif self.game_state == GAME_WON:
            self.show_txt(f"PLAYER {self.current_player} HAS WON", (600, 20))
        elif self.game_state == GAME_DRAW:
            self.show_txt(f"NO WINNER EXISTS...", (600, 20))
        elif self.game_state == GAME_TIMEOUT:
            self.show_txt(f"TIMEOUT!!!!!", (600, 20))
            self.show_txt(f"TOO SLOW HAHA", (600, 50))

        if self.game_state != GAME_ACTIVE:
            self.show_txt("Please press any", (600, 90))
            self.show_txt("field to play again!", (600, 110))

    def switch_player(self):
        if self.current_player == PLAYER_O:
            self.current_player = PLAYER_X
        else:
            self.current_player = PLAYER_O

    def field_click_event(self, field:Field):
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
            self.after_game_lock = True
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
            self.after_game_lock = True

    def update_timer(self):
        self.general_timer += self.delta_time
        if self.general_timer < 1000:
            return

        self.general_timer = 0
        self.move_timer -= 1
        self.round_timer -= 1

        if self.move_timer < 0:
            self.switch_player()
            self.move_timer = MAX_MOVE_DURATION

        if self.round_timer < 0:
            self.game_state = GAME_TIMEOUT

    def update(self):
        if self.after_game_lock:
            if self.mouse_state_changed():
                self.after_game_lock = False
            else:
                return

        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        for field in self.fields.values():
            field.check(mouse_pressed, mouse_pos)

        if self.game_state != GAME_ACTIVE:
            return

        self.update_timer()
        self.check_game_winner()
        self.check_game_draw()

class MainView(View):
    def __init__(self, screen:pygame.Surface, clock:pygame.time.Clock):
        super().__init__(screen, clock)

    def draw(self, screen: pygame.Surface):
        self.show_txt("CLICK ANYWHERE IN THE WINDOW TO START", (150, 300))

    def update(self):
        if self.mouse_state_changed():
            self.change_menu = "game"

class Window:
    def __init__(self):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("TicTacToe")

        self.menus = {"main": MainView, "game": GameView}
        self.start_with = "main"

    def run(self):
        view_class:View = self.menus[self.start_with]

        while True:
            view_object:View = view_class(self.screen, self.clock)
            view_object.setup()
            next_view = view_object.run()
            view_class = self.menus[next_view]

def main():
    window = Window()
    window.run()

if __name__ == "__main__":
    main()
