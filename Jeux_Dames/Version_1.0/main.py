import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 700, 700
ROWS, COLS = 10, 10  # 10x10 for international checkers
SQUARE_SIZE = WIDTH // COLS
MENU_HEIGHT = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
BEIGE = (245, 222, 179)
DARK_BROWN = (101, 67, 33)
LIGHT_WOOD = (222, 184, 135)
DARK_WOOD = (139, 90, 43)

# Board color theme (black and white only)
BOARD_THEME = {"light": WHITE, "dark": BLACK}

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Images are in the parent directory's image folder
IMAGE_DIR = os.path.join(os.path.dirname(BASE_DIR), "image")


class ImageLoader:
    """Handles loading and scaling of game images"""
    
    def __init__(self):
        self.images = {}
        self.load_images()
    
    def load_images(self):
        try:
            # Load piece images
            self.images['pion_bleu'] = pygame.image.load(os.path.join(IMAGE_DIR, "pion bleu.png"))
            self.images['pion_gris'] = pygame.image.load(os.path.join(IMAGE_DIR, "pion gris.png"))
            self.images['reine_bleu'] = pygame.image.load(os.path.join(IMAGE_DIR, "reine bleu.png"))
            self.images['reine_gris'] = pygame.image.load(os.path.join(IMAGE_DIR, "reine gris.png"))
            
            # Scale images to fit squares
            piece_size = int(SQUARE_SIZE * 0.8)
            for key in self.images:
                self.images[key] = pygame.transform.smoothscale(self.images[key], (piece_size, piece_size))
                
            self.images_loaded = True
        except Exception as e:
            print(f"Warning: Could not load images: {e}")
            self.images_loaded = False
    
    def get_image(self, piece_type, is_king):
        if not self.images_loaded:
            return None
        
        if piece_type == 'blue':
            return self.images['reine_bleu'] if is_king else self.images['pion_bleu']
        else:  # grey
            return self.images['reine_gris'] if is_king else self.images['pion_gris']


class Piece:
    """Represents a game piece (pawn or queen)"""
    
    def __init__(self, row, col, color, image_loader):
        self.row = row
        self.col = col
        self.color = color  # 'blue' or 'grey'
        self.king = False
        self.image_loader = image_loader
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        image = self.image_loader.get_image(self.color, self.king)
        if image:
            img_rect = image.get_rect(center=(self.x, self.y))
            win.blit(image, img_rect)
        else:
            # Fallback: draw circles if images not available
            radius = SQUARE_SIZE // 2 - 10
            color = (50, 50, 200) if self.color == 'blue' else (100, 100, 100)
            pygame.draw.circle(win, GREY, (self.x, self.y), radius + 3)
            pygame.draw.circle(win, color, (self.x, self.y), radius)
            if self.king:
                font = pygame.font.SysFont('arial', 20, bold=True)
                crown = font.render('R', True, WHITE)
                win.blit(crown, (self.x - crown.get_width() // 2, self.y - crown.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return f"Piece({self.row}, {self.col}, {self.color}, king={self.king})"


class Board:
    """Represents the game board"""
    
    def __init__(self, image_loader):
        self.board = []
        self.grey_left = self.blue_left = 20  # 20 pieces each for 10x10
        self.grey_kings = self.blue_kings = 0
        self.image_loader = image_loader
        self.create_board()

    def draw_squares(self, win):
        # Dessiner le plateau avec cases alternées noir/blanc
        # Les pièces jouent sur les cases NOIRES
        win.fill(BOARD_THEME["light"])  # Fond blanc
        for row in range(ROWS):
            for col in range(COLS):
                # Cases noires où (row + col) est impair
                if (row + col) % 2 == 1:
                    pygame.draw.rect(win, BOARD_THEME["dark"], 
                                   (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        self.board = []
        self.grey_left = self.blue_left = 20
        self.grey_kings = self.blue_kings = 0
        
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                # Pièces uniquement sur les cases noires (où row + col est impair)
                if (row + col) % 2 == 1:
                    if row < 4:  # 4 premières rangées pour les bleus
                        self.board[row].append(Piece(row, col, 'blue', self.image_loader))
                    elif row > 5:  # 4 dernières rangées pour les gris
                        self.board[row].append(Piece(row, col, 'grey', self.image_loader))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        # Swap positions
        self.board[piece.row][piece.col], self.board[row][col] = \
            self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        # Check for king promotion
        if row == ROWS - 1 and piece.color == 'blue' and not piece.king:
            piece.make_king()
            self.blue_kings += 1
        elif row == 0 and piece.color == 'grey' and not piece.king:
            piece.make_king()
            self.grey_kings += 1

    def get_piece(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return None

    def remove(self, pieces):
        for piece in pieces:
            if piece != 0:
                self.board[piece.row][piece.col] = 0
                if piece.color == 'grey':
                    self.grey_left -= 1
                else:
                    self.blue_left -= 1

    def winner(self):
        if self.grey_left <= 0:
            return "BLEU"
        elif self.blue_left <= 0:
            return "GRIS"
        return None

    def get_valid_moves(self, piece):
        """Get all valid moves for a piece, including captures"""
        moves = {}  # {(row, col): [skipped_pieces]}
        
        if piece.king:
            # Queens can move in all 4 diagonal directions, multiple squares
            moves.update(self._get_queen_moves(piece))
        else:
            # Regular pieces move forward only (direction depends on color)
            moves.update(self._get_pawn_moves(piece))
        
        return moves

    def _get_pawn_moves(self, piece):
        """
        Get valid moves for a regular pawn following international checkers rules.
        
        Movement rules:
        - Simple moves: Only forward diagonally, one square at a time
        - Cannot move backward in simple movement
        
        Capture rules:
        - Capture is mandatory
        - Can capture forward AND backward during capture jumps
        - Must continue capturing if multiple captures are possible
        """
        moves = {}
        row = piece.row
        col = piece.col
        
        # First, check for captures in ALL 4 directions (pawns can capture backward too!)
        capture_moves = {}
        for row_dir in [-1, 1]:  # Both up and down
            for col_dir in [-1, 1]:  # Both left and right
                capture_moves.update(self._pawn_find_captures(row, col, row_dir, col_dir, piece.color, []))
        
        # If captures are available, only return capture moves (capture is mandatory)
        if capture_moves:
            return capture_moves
        
        # No captures available - return simple forward moves only
        # Grey moves up (decreasing row), Blue moves down (increasing row)
        forward_dir = -1 if piece.color == 'grey' else 1
        
        for col_dir in [-1, 1]:
            new_row = row + forward_dir
            new_col = col + col_dir
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if self.board[new_row][new_col] == 0:
                    moves[(new_row, new_col)] = []
        
        return moves
    
    def _pawn_find_captures(self, start_row, start_col, row_dir, col_dir, color, already_captured):
        """
        Find captures for a pawn in a specific diagonal direction.
        
        Pawn capture rules:
        - Can capture by jumping over an adjacent enemy piece
        - Must land on the empty square immediately after the enemy
        - Can capture in all 4 diagonal directions (forward AND backward)
        - Must continue capturing if more captures are available (chain captures)
        
        Args:
            start_row, start_col: Current position
            row_dir, col_dir: Direction to check for capture
            color: Pawn's color
            already_captured: List of pieces already captured in this chain
        
        Returns:
            dict: {(landing_row, landing_col): [list of captured pieces]}
        """
        moves = {}
        
        # Check the adjacent square for an enemy piece
        enemy_row = start_row + row_dir
        enemy_col = start_col + col_dir
        
        if not (0 <= enemy_row < ROWS and 0 <= enemy_col < COLS):
            return moves
        
        enemy = self.board[enemy_row][enemy_col]
        
        # Must be an enemy piece (not empty, not our color, not already captured)
        if enemy == 0 or enemy.color == color or enemy in already_captured:
            return moves
        
        # Check the landing square (must be empty)
        landing_row = enemy_row + row_dir
        landing_col = enemy_col + col_dir
        
        if not (0 <= landing_row < ROWS and 0 <= landing_col < COLS):
            return moves
        
        if self.board[landing_row][landing_col] != 0:
            return moves
        
        # Valid capture found!
        captured_list = already_captured + [enemy]
        moves[(landing_row, landing_col)] = captured_list
        
        # Look for additional captures from the landing position (chain captures)
        # Check all 4 directions for more captures
        for new_row_dir in [-1, 1]:
            for new_col_dir in [-1, 1]:
                additional_captures = self._pawn_find_captures(
                    landing_row, landing_col, new_row_dir, new_col_dir, color, captured_list
                )
                # Merge captures, preferring longer chains
                for pos, caps in additional_captures.items():
                    if pos not in moves or len(caps) > len(moves[pos]):
                        moves[pos] = caps
        
        return moves

    def _get_queen_moves(self, piece):
        """
        Get valid moves for a queen following official international checkers rules.
        
        Official rules for queens:
        1. Can move diagonally in all 4 directions (forward and backward)
        2. Can move multiple empty squares in one direction
        3. Can capture by jumping over an enemy piece at any distance, 
           landing on any empty square after the captured piece
        4. Must perform multiple captures if possible (chain captures)
        5. Cannot jump over the same piece twice
        6. Cannot jump over own pieces
        """
        moves = {}
        
        # All 4 diagonal directions: (row_direction, col_direction)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        # First, check if there are any captures available
        capture_moves = {}
        for row_dir, col_dir in directions:
            capture_moves.update(self._queen_find_captures(
                piece.row, piece.col, row_dir, col_dir, piece.color, []
            ))
        
        # If captures are available, only return capture moves
        if capture_moves:
            return capture_moves
        
        # No captures available, return regular moves
        for row_dir, col_dir in directions:
            moves.update(self._queen_regular_moves(
                piece.row, piece.col, row_dir, col_dir, piece.color
            ))
        
        return moves

    def _queen_regular_moves(self, start_row, start_col, row_dir, col_dir, color):
        """
        Get regular (non-capture) moves for a queen in one diagonal direction.
        Queen can move any number of empty squares in a diagonal.
        """
        moves = {}
        r, c = start_row + row_dir, start_col + col_dir
        
        # Move along the diagonal until we hit a piece or board edge
        while 0 <= r < ROWS and 0 <= c < COLS:
            current = self.board[r][c]
            if current == 0:
                # Empty square - queen can move here
                moves[(r, c)] = []
            else:
                # Hit a piece (own or enemy) - stop
                break
            r += row_dir
            c += col_dir
        
        return moves

    def _queen_find_captures(self, start_row, start_col, row_dir, col_dir, color, already_captured):
        """
        Trouve toutes les captures possibles pour une reine dans une direction diagonale.
        
        Règles officielles des dames internationales pour la reine:
        - La reine peut capturer une pièce ennemie (pion ou reine) à n'importe quelle distance
        - La reine doit atterrir sur une case vide après la pièce capturée
        - La reine peut atterrir sur n'importe quelle case vide après la pièce capturée
        - Depuis chaque position d'atterrissage, vérifier les captures supplémentaires
        - Ne peut pas capturer la même pièce deux fois
        
        Args:
            start_row, start_col: Position de départ
            row_dir, col_dir: Direction de recherche
            color: Couleur de la reine ('grey' ou 'blue')
            already_captured: Liste des pièces déjà capturées dans cette chaîne
        
        Returns:
            dict: {(row_atterrissage, col_atterrissage): [liste des pièces capturées]}
        """
        moves = {}
        r, c = start_row + row_dir, start_col + col_dir
        enemy_to_capture = None
        
        # Parcourir la diagonale pour trouver un ennemi à capturer
        while 0 <= r < ROWS and 0 <= c < COLS:
            current = self.board[r][c]
            
            if current == 0:
                # Case vide
                if enemy_to_capture is not None:
                    # On a trouvé un ennemi avant, on peut atterrir ici après capture
                    captured_list = already_captured + [enemy_to_capture]
                    moves[(r, c)] = captured_list
                    
                    # Depuis cette position, chercher des captures supplémentaires
                    # Vérifier les 4 directions sauf retour en arrière
                    for new_row_dir, new_col_dir in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        # Ne pas revenir dans la direction opposée exacte
                        if new_row_dir == -row_dir and new_col_dir == -col_dir:
                            continue
                        
                        # Chercher récursivement plus de captures
                        additional_captures = self._queen_find_captures(
                            r, c, new_row_dir, new_col_dir, color, captured_list
                        )
                        
                        # Fusionner les captures (garder celles avec plus de captures)
                        for pos, caps in additional_captures.items():
                            if pos not in moves or len(caps) > len(moves[pos]):
                                moves[pos] = caps
                # Si pas encore d'ennemi trouvé, continuer la recherche
            
            elif current.color == color:
                # Pièce alliée - ne peut pas passer, arrêter la recherche
                break
            
            else:
                # Pièce ennemie trouvée (pion OU reine adverse)
                if enemy_to_capture is not None:
                    # Déjà trouvé un ennemi - ne peut pas sauter deux pièces d'affilée
                    break
                
                # Vérifier si cette pièce a déjà été capturée dans la chaîne
                if current in already_captured:
                    break
                
                # Marquer cet ennemi comme trouvé pour capture
                enemy_to_capture = current
            
            r += row_dir
            c += col_dir
        
        return moves



    def set_theme(self, theme_index):
        # Theme is fixed to black and white
        pass


class Game:
    """Main game controller"""
    
    def __init__(self, win, image_loader):
        self.win = win
        self.image_loader = image_loader
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board(self.image_loader)
        self.turn = 'grey'  # Grey starts
        self.valid_moves = {}
        self.must_capture = False

    def update(self):
        self.board.draw(self.win)
        self.draw_selected()
        self.draw_valid_moves(self.valid_moves)
        self.draw_turn_indicator()
        pygame.display.update()

    def draw_selected(self):
        """Highlight the selected piece"""
        if self.selected:
            pygame.draw.rect(self.win, (255, 255, 0), 
                           (self.selected.col * SQUARE_SIZE, self.selected.row * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE), 4)

    def draw_turn_indicator(self):
        font = pygame.font.SysFont('arial', 22, bold=True)
        turn_text = "Tour: GRIS" if self.turn == 'grey' else "Tour: BLEU"
        text = font.render(turn_text, True, WHITE)
        
        # Score
        score_text = f"Gris: {self.board.grey_left} | Bleu: {self.board.blue_left}"
        score = font.render(score_text, True, WHITE)
        
        pygame.draw.rect(self.win, BLACK, (5, 5, max(text.get_width(), score.get_width()) + 20, 55))
        self.win.blit(text, (15, 8))
        self.win.blit(score, (15, 32))

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece is not None and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and (piece == 0 or piece is None) and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        for move, skipped in moves.items():
            row, col = move
            color = (255, 100, 100) if skipped else GREEN  # Red tint for captures
            pygame.draw.circle(self.win, color, 
                             (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                              row * SQUARE_SIZE + SQUARE_SIZE // 2), 12)

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.turn = 'blue' if self.turn == 'grey' else 'grey'

    def change_theme(self):
        self.board.set_theme(self.board.theme_index + 1)


class Menu:
    """Main menu system"""
    
    def __init__(self, win):
        self.win = win
        self.font_title = pygame.font.SysFont('arial', 60, bold=True)
        self.font_button = pygame.font.SysFont('arial', 30)
        self.buttons = []
        self.theme_index = 0
        self.create_buttons()
    
    def create_buttons(self):
        button_width = 300
        button_height = 60
        start_y = 250
        spacing = 100
        
        self.buttons = [
            {
                "rect": pygame.Rect(WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
                "text": "Commencer la Partie",
                "action": "start"
            },
            {
                "rect": pygame.Rect(WIDTH // 2 - button_width // 2, start_y + spacing, button_width, button_height),
                "text": "Quitter",
                "action": "quit"
            }
        ]
    
    def draw(self):
        self.win.fill((40, 40, 60))
        
        # Title
        title = self.font_title.render("Jeu de Dames", True, WHITE)
        self.win.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        # Subtitle
        subtitle = pygame.font.SysFont('arial', 24).render("International (10x10)", True, GREY)
        self.win.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            color = (80, 80, 120) if button["rect"].collidepoint(mouse_pos) else (60, 60, 90)
            pygame.draw.rect(self.win, color, button["rect"], border_radius=10)
            pygame.draw.rect(self.win, WHITE, button["rect"], 2, border_radius=10)
            
            text = self.font_button.render(button["text"], True, WHITE)
            self.win.blit(text, (button["rect"].centerx - text.get_width() // 2,
                                 button["rect"].centery - text.get_height() // 2))
        
        # Instructions
        instructions = [
            "R - Recommencer la partie",
            "M - Retour au menu",
            "Q - Quitter"
        ]
        small_font = pygame.font.SysFont('arial', 18)
        for i, inst in enumerate(instructions):
            text = small_font.render(inst, True, GREY)
            self.win.blit(text, (WIDTH // 2 - text.get_width() // 2, 520 + i * 25))
        
        pygame.display.update()
    
    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button["action"]
        return None


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


def show_winner(win, winner):
    font = pygame.font.SysFont('arial', 50, bold=True)
    color = (50, 50, 200) if winner == "BLEU" else (100, 100, 100)
    text = font.render(f"{winner} GAGNE!", True, color)
    
    # Background rectangle
    rect = pygame.Rect(WIDTH // 2 - text.get_width() // 2 - 30, 
                       HEIGHT // 2 - text.get_height() // 2 - 30,
                       text.get_width() + 60, text.get_height() + 80)
    pygame.draw.rect(win, BLACK, rect, border_radius=15)
    pygame.draw.rect(win, WHITE, rect, 3, border_radius=15)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 10))
    
    # Restart instruction
    font_small = pygame.font.SysFont('arial', 20)
    restart_text = font_small.render("R: Recommencer | M: Menu | Q: Quitter", True, WHITE)
    win.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 25))
    
    pygame.display.update()


def main():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Jeu de Dames - International')
    
    clock = pygame.time.Clock()
    image_loader = ImageLoader()
    menu = Menu(WIN)
    game = None
    
    state = "menu"  # "menu" or "game"
    run = True
    game_over = False

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_r and state == "game":
                    game.reset()
                    game_over = False
                elif event.key == pygame.K_m and state == "game":
                    state = "menu"
                    game_over = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    action = menu.handle_click(event.pos)
                    if action == "start":
                        game = Game(WIN, image_loader)
                        state = "game"
                        game_over = False
                    elif action == "quit":
                        run = False
                elif state == "game" and not game_over:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        game.select(row, col)

        if state == "menu":
            menu.draw()
        elif state == "game":
            if not game_over:
                game.update()
                winner = game.winner()
                if winner:
                    game_over = True
                    show_winner(WIN, winner)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()