from settings import *
from chess import GameState, Move
import player_IA
import pygame as pg

#  Preguntar promoción de peón. Problema: al validar movimientos pregunta infinitas veces
#  a que se quiere promocionar antes de que se haga el movimiento
# Arreglar animación en-passant


class Game:
    def __init__(self):
        self.human_turn = None
        self.images = {}
        self.move_options = ""
        self.move_capture = ""
        self.title = TITLE
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen.fill("White")
        self.clock = pg.time.Clock()
        self.game_state = GameState()
        self.valid_moves = self.game_state.get_valid_moves()
        self.move_made = False
        self.animate = False
        self.running = True
        self.game_over = False
        self.player_one = True  # True: human white, False: human black
        self.player_two = False  # True: IA white, False: IA black
        self.selected = ()
        self.clicks = []

    def load_images(self):
        """
        Carga imágenes necesarias para el juego
        """
        pieces = ["bP", "bR", "bB", "bN", "bQ", "bK", "wP", "wR", "wB", "wN", "wQ", "wK"]
        for piece in pieces:
            self.images[piece] = pg.image.load(DIR+piece+".png")
        self.move_options = pg.image.load(DIR+"option.png")
        self.move_options.set_alpha(120)
        self.move_capture = pg.image.load(DIR+"capture.png")
        self.move_capture.set_alpha(120)

    def check_events(self):
        """
        Verifica eventos del teclado/mouse
        """
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False
            elif e.type == pg.MOUSEBUTTONDOWN:  # Pasar a un método
                if not self.game_over and self.human_turn:
                    loc = pg.mouse.get_pos()
                    col = loc[0] // SQ_SIZE
                    row = loc[1] // SQ_SIZE
                    if self.selected == (row, col):
                        self.selected = ()
                        self.clicks = []
                    else:
                        self.selected = (row, col)
                        self.clicks.append(self.selected)
                    if len(self.clicks) == 2:
                        move = Move((self.clicks[0]), (self.clicks[1]), self.game_state.board)
                        for i in range(len(self.valid_moves)):
                            if move == self.valid_moves[i]:
                                self.game_state.make_move(self.valid_moves[i])
                                self.move_made = True
                                self.animate = True
                                print(f"{move.get_notation()} - {move.move_id}")
                                self.selected = ()
                                self.clicks = []
                        if not self.move_made:
                            self.clicks = [self.selected]
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_LCTRL:
                    self.game_state.undo_move()
                    self.move_made = True
                    self.animate = False
                if e.key == pg.K_r:
                    self.game_state = GameState()
                    self.valid_moves = self.game_state.get_valid_moves()
                    self.selected = ()
                    self.clicks = []
                    self.move_made = False
                    self.animate = False
                    self.game_over = False

        # AI move finder logic
        if not self.game_over and not self.human_turn:
            ai_move = player_IA.random_move(self.valid_moves)
            self.game_state.make_move(ai_move)
            self.move_made = True
            self.animate = True

        if self.move_made:
            if self.animate:
                self.animate_move(self.game_state.move_log[-1])
            self.valid_moves = self.game_state.get_valid_moves()
            self.move_made = False
            self.animate = False

        if self.game_state.check_mate:
            self.game_over = True
            if self.game_state.white_turn:
                self.draw_text("Black wins by checkmate")
            else:
                self.draw_text("White wins by checkmate")
        elif self.game_state.stale_mate:
            self.game_over = True
            self.draw_text("Stalemate")

        self.clock.tick(FPS)
        pg.display.flip()

    def draw_board(self):
        """
        Dibuja tablero
        """
        colors = [pg.Color(DARK), pg.Color(LIGHT)]
        for r in range(DIMS):
            for c in range(DIMS):
                color = colors[(r+c) % 2]
                cas = pg.Surface((SQ_SIZE, SQ_SIZE))
                cas.fill(color)
                self.screen.blit(cas, (r*SQ_SIZE, c*SQ_SIZE))

    def draw_pieces(self):
        """
        Dibuja las piezas según el estado del tablero actual
        """
        for r in range(DIMS):
            for c in range(DIMS):
                piece = self.game_state.board[r][c]
                if piece != "--":
                    self.screen.blit(self.images[piece],
                                     pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def draw_highlight(self):
        """
        Marca la pieza seleccionada y sus movimientos válidos
        """
        s = pg.Surface((SQ_SIZE, SQ_SIZE))
        s.fill("yellow")
        s.set_alpha(120)
        if self.selected != ():
            r, c = self.selected[0], self.selected[1]
            if self.game_state.board[r][c][0] == ("w" if self.game_state.white_turn else "b"):
                self.screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
                for move in self.valid_moves:
                    if move.start_r == r and move.start_c == c:
                        color = "b" if self.game_state.white_turn else "w"
                        if self.game_state.board[move.end_r][move.end_c][0] == color:
                            self.screen.blit(self.move_capture, (move.end_c*SQ_SIZE, move.end_r*SQ_SIZE))
                        else:
                            self.screen.blit(self.move_options, (move.end_c*SQ_SIZE, move.end_r*SQ_SIZE))
        if len(self.game_state.move_log) != 0:
            move = self.game_state.move_log[-1]
            self.screen.blit(s, (move.start_c*SQ_SIZE, move.start_r*SQ_SIZE))
            self.screen.blit(s, (move.end_c * SQ_SIZE, move.end_r * SQ_SIZE))

    def draw_text(self, text):
        font = pg.font.SysFont("Arial", 32, True, False)
        text_object = font.render(text, False, pg.Color("grey"))
        text_loc = pg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2,
                                                     HEIGHT/2 - text_object.get_height()/2)  # center text
        self.screen.blit(text_object, text_loc)
        text_object = font.render(text, False, pg.Color("black"))
        self.screen.blit(text_object, text_loc.move(2, 2))

    def draw_game_state(self):
        """
        Dibuja el estado del juego actual
        """
        self.draw_board()
        self.draw_highlight()
        self.draw_pieces()

    def animate_move(self, move):  # Reescribir código para no redibujar el tablero siempre
        """
        Anima los movimientos de las piezas
        """
        colors = [pg.Color(DARK), pg.Color(LIGHT)]
        delta_r = move.end_r - move.start_r
        delta_c = move.end_c - move.start_c
        frames_per_square = 6
        frame_count = (abs(delta_r) + abs(delta_c)) * frames_per_square
        for frame in range(frame_count+1):
            r, c = (move.start_r + delta_r*frame/frame_count, move.start_c + delta_c*frame/frame_count)
            self.draw_board()
            self.draw_pieces()
            color = colors[(move.end_r + move.end_c) % 2]
            end = pg.Rect(move.end_c*SQ_SIZE, move.end_r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pg.draw.rect(self.screen, color, end)
            if move.piece_capture != "--":
                self.screen.blit(self.images[move.piece_capture], end)
            self.screen.blit(self.images[move.piece_moved], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            pg.display.flip()
            self.clock.tick(FPS)

    def main(self):
        """
        Función principal del juego
        """
        pg.init()
        self.load_images()

        pg.display.set_caption(f"{self.title}-{self.clock.get_fps() :.1f}")

        while self.running:
            self.human_turn = (self.game_state.white_turn and self.player_one) or \
                              (not self.game_state.white_turn and self.player_two)
            self.check_events()
            if not self.game_over:
                self.draw_game_state()
            self.clock.tick(FPS)
            pg.display.flip()
