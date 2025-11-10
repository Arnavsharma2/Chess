"""
Chess 
"""

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants for the game
WINDOW_SIZE = 800
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_SIZE // BOARD_SIZE

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
SELECTED_COLOR = (246, 246, 130)

# Piece Unicode symbols
PIECE_SYMBOLS = {
    'white': {
        'king': '♔', 'queen': '♕', 'rook': '♖',
        'bishop': '♗', 'knight': '♘', 'pawn': '♙'
    },
    'black': {
        'king': '♚', 'queen': '♛', 'rook': '♜',
        'bishop': '♝', 'knight': '♞', 'pawn': '♟'
    }
}

# Fallback text symbols if Unicode doesn't render properly
PIECE_LETTERS = {
    'white': {
        'king': 'K', 'queen': 'Q', 'rook': 'R',
        'bishop': 'B', 'knight': 'N', 'pawn': 'P'
    },
    'black': {
        'king': 'k', 'queen': 'q', 'rook': 'r',
        'bishop': 'b', 'knight': 'n', 'pawn': 'p'
    }
}


class Piece:
    """Base class for all chess pieces"""

    def __init__(self, color, position):
        """
        Initialize a chess piece

        Args:
            color (str): 'white' or 'black'
            position (tuple): (row, col) position on the board
        """
        self.color = color
        self.position = position
        self.has_moved = False  # Track if piece has moved (for castling and pawn double move)

    def get_possible_moves(self, board):
        """
        Get all possible moves for this piece (to be overridden by subclasses)

        Args:
            board (Board): The current game board

        Returns:
            list: List of valid positions [(row, col), ...]
        """
        return []

    def is_valid_position(self, row, col):
        """Check if a position is within the board boundaries"""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


class Pawn(Piece):
    """Pawn piece - moves forward, captures diagonally"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['pawn']
        self.letter = PIECE_LETTERS[color]['pawn']

    def get_possible_moves(self, board):
        """Get all valid pawn moves including forward moves and captures"""
        moves = []
        row, col = self.position
        direction = -1 if self.color == 'white' else 1  # White moves up, black moves down

        # Forward move (one square)
        new_row = row + direction
        if self.is_valid_position(new_row, col):
            if board.get_piece(new_row, col) is None:
                moves.append((new_row, col))

                # Forward move (two squares from starting position)
                if not self.has_moved:
                    new_row2 = row + 2 * direction
                    if board.get_piece(new_row2, col) is None:
                        moves.append((new_row2, col))

        # Diagonal captures
        for dc in [-1, 1]:
            new_row = row + direction
            new_col = col + dc
            if self.is_valid_position(new_row, new_col):
                target_piece = board.get_piece(new_row, new_col)
                if target_piece and target_piece.color != self.color:
                    moves.append((new_row, new_col))

        # En passant capture
        en_passant_moves = board.get_en_passant_moves(self)
        moves.extend(en_passant_moves)

        return moves


class Rook(Piece):
    """Rook piece - moves horizontally and vertically"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['rook']
        self.letter = PIECE_LETTERS[color]['rook']

    def get_possible_moves(self, board):
        """Get all valid rook moves (horizontal and vertical lines)"""
        moves = []
        row, col = self.position

        # Define directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Check each direction
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row = row + dr * i
                new_col = col + dc * i

                if not self.is_valid_position(new_row, new_col):
                    break

                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None:
                    moves.append((new_row, new_col))
                else:
                    if target_piece.color != self.color:
                        moves.append((new_row, new_col))
                    break

        return moves


class Knight(Piece):
    """Knight piece - moves in L-shape"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['knight']
        self.letter = PIECE_LETTERS[color]['knight']

    def get_possible_moves(self, board):
        """Get all valid knight moves (L-shaped jumps)"""
        moves = []
        row, col = self.position

        # All possible L-shaped moves for a knight
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_moves:
            new_row = row + dr
            new_col = col + dc

            if self.is_valid_position(new_row, new_col):
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.color != self.color:
                    moves.append((new_row, new_col))

        return moves


class Bishop(Piece):
    """Bishop piece - moves diagonally"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['bishop']
        self.letter = PIECE_LETTERS[color]['bishop']

    def get_possible_moves(self, board):
        """Get all valid bishop moves (diagonal lines)"""
        moves = []
        row, col = self.position

        # Define diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Check each diagonal direction
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row = row + dr * i
                new_col = col + dc * i

                if not self.is_valid_position(new_row, new_col):
                    break

                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None:
                    moves.append((new_row, new_col))
                else:
                    if target_piece.color != self.color:
                        moves.append((new_row, new_col))
                    break

        return moves


class Queen(Piece):
    """Queen piece - moves horizontally, vertically, and diagonally"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['queen']
        self.letter = PIECE_LETTERS[color]['queen']

    def get_possible_moves(self, board):
        """Get all valid queen moves (combination of rook and bishop)"""
        moves = []
        row, col = self.position

        # Define all eight directions (rook + bishop)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook-like
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop-like
        ]

        # Check each direction
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row = row + dr * i
                new_col = col + dc * i

                if not self.is_valid_position(new_row, new_col):
                    break

                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None:
                    moves.append((new_row, new_col))
                else:
                    if target_piece.color != self.color:
                        moves.append((new_row, new_col))
                    break

        return moves


class King(Piece):
    """King piece - moves one square in any direction"""

    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = PIECE_SYMBOLS[color]['king']
        self.letter = PIECE_LETTERS[color]['king']

    def get_possible_moves(self, board):
        """Get all valid king moves (one square in any direction)"""
        moves = []
        row, col = self.position

        # All possible one-square moves
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if self.is_valid_position(new_row, new_col):
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.color != self.color:
                    moves.append((new_row, new_col))

        # Check for castling moves
        castling_moves = board.get_castling_moves(self)
        moves.extend(castling_moves)

        return moves


class Board:
    """Represents the chess board and manages game state"""

    def __init__(self):
        """Initialize the chess board with pieces in starting positions"""
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.last_move = None  # Track last move for en passant
        self.setup_pieces()

    def setup_pieces(self):
        """Set up all pieces in their initial positions"""
        # Set up pawns
        for col in range(BOARD_SIZE):
            self.grid[1][col] = Pawn('black', (1, col))
            self.grid[6][col] = Pawn('white', (6, col))

        # Set up other pieces (black)
        self.grid[0][0] = Rook('black', (0, 0))
        self.grid[0][7] = Rook('black', (0, 7))
        self.grid[0][1] = Knight('black', (0, 1))
        self.grid[0][6] = Knight('black', (0, 6))
        self.grid[0][2] = Bishop('black', (0, 2))
        self.grid[0][5] = Bishop('black', (0, 5))
        self.grid[0][3] = Queen('black', (0, 3))
        self.grid[0][4] = King('black', (0, 4))

        # Set up other pieces (white)
        self.grid[7][0] = Rook('white', (7, 0))
        self.grid[7][7] = Rook('white', (7, 7))
        self.grid[7][1] = Knight('white', (7, 1))
        self.grid[7][6] = Knight('white', (7, 6))
        self.grid[7][2] = Bishop('white', (7, 2))
        self.grid[7][5] = Bishop('white', (7, 5))
        self.grid[7][3] = Queen('white', (7, 3))
        self.grid[7][4] = King('white', (7, 4))

    def get_piece(self, row, col):
        """Get the piece at a specific position"""
        return self.grid[row][col]

    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from one position to another

        Args:
            from_pos (tuple): Starting position (row, col)
            to_pos (tuple): Ending position (row, col)

        Returns:
            bool: True if move was successful, False otherwise
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = self.grid[from_row][from_col]
        if piece is None:
            return False

        # Handle en passant capture
        if isinstance(piece, Pawn) and to_col != from_col and self.grid[to_row][to_col] is None:
            # This is an en passant capture
            captured_pawn_row = from_row
            self.grid[captured_pawn_row][to_col] = None

        # Handle castling
        if isinstance(piece, King) and abs(to_col - from_col) == 2:
            # King is castling
            if to_col > from_col:  # King-side castling
                rook = self.grid[from_row][7]
                self.grid[from_row][7] = None
                self.grid[from_row][5] = rook
                rook.position = (from_row, 5)
                rook.has_moved = True
            else:  # Queen-side castling
                rook = self.grid[from_row][0]
                self.grid[from_row][0] = None
                self.grid[from_row][3] = rook
                rook.position = (from_row, 3)
                rook.has_moved = True

        # Move the piece
        self.grid[to_row][to_col] = piece
        self.grid[from_row][from_col] = None

        # Update piece position and has_moved flag
        piece.position = to_pos
        piece.has_moved = True

        # Track the last move for en passant
        self.last_move = (from_pos, to_pos, piece)

        return True

    def get_en_passant_moves(self, pawn):
        """
        Get en passant moves for a pawn

        Args:
            pawn (Pawn): The pawn to check for en passant

        Returns:
            list: List of valid en passant positions
        """
        if not self.last_move:
            return []

        last_from, last_to, last_piece = self.last_move

        # Check if last move was a pawn moving two squares
        if not isinstance(last_piece, Pawn):
            return []

        if abs(last_from[0] - last_to[0]) != 2:
            return []

        # Check if pawns are adjacent
        row, col = pawn.position
        last_row, last_col = last_to

        if row != last_row or abs(col - last_col) != 1:
            return []

        # Check colors are opposite
        if pawn.color == last_piece.color:
            return []

        # En passant is valid
        direction = -1 if pawn.color == 'white' else 1
        return [(row + direction, last_col)]

    def get_castling_moves(self, king):
        """
        Get castling moves for the king

        Args:
            king (King): The king to check for castling

        Returns:
            list: List of valid castling positions
        """
        if king.has_moved:
            return []

        row, col = king.position
        castling_moves = []

        # Check king-side castling
        rook_kingside = self.grid[row][7]
        if isinstance(rook_kingside, Rook) and not rook_kingside.has_moved:
            # Check if squares between king and rook are empty
            if self.grid[row][5] is None and self.grid[row][6] is None:
                # Check if king is not in check and doesn't move through check
                if not self.is_position_under_attack(row, col, king.color):
                    if not self.is_position_under_attack(row, 5, king.color):
                        if not self.is_position_under_attack(row, 6, king.color):
                            castling_moves.append((row, 6))

        # Check queen-side castling
        rook_queenside = self.grid[row][0]
        if isinstance(rook_queenside, Rook) and not rook_queenside.has_moved:
            # Check if squares between king and rook are empty
            if self.grid[row][1] is None and self.grid[row][2] is None and self.grid[row][3] is None:
                # Check if king is not in check and doesn't move through check
                if not self.is_position_under_attack(row, col, king.color):
                    if not self.is_position_under_attack(row, 3, king.color):
                        if not self.is_position_under_attack(row, 2, king.color):
                            castling_moves.append((row, 2))

        return castling_moves

    def is_position_under_attack(self, row, col, color):
        """
        Check if a position is under attack by the opponent

        Args:
            row (int): Row of the position
            col (int): Column of the position
            color (str): Color of the piece we're checking for

        Returns:
            bool: True if position is under attack, False otherwise
        """
        opponent_color = 'black' if color == 'white' else 'white'

        # Check all opponent pieces
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece and piece.color == opponent_color:
                    # Get moves without checking for check (to avoid infinite recursion)
                    if isinstance(piece, King):
                        # For king, just check one square in each direction
                        king_moves = [
                            (r - 1, c - 1), (r - 1, c), (r - 1, c + 1),
                            (r, c - 1),                 (r, c + 1),
                            (r + 1, c - 1), (r + 1, c), (r + 1, c + 1)
                        ]
                        if (row, col) in king_moves:
                            return True
                    else:
                        moves = piece.get_possible_moves(self)
                        if (row, col) in moves:
                            return True

        return False

    def is_in_check(self, color):
        """
        Check if the king of a given color is in check

        Args:
            color (str): Color of the king to check

        Returns:
            bool: True if king is in check, False otherwise
        """
        # Find the king
        king_pos = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.grid[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        return self.is_position_under_attack(king_pos[0], king_pos[1], color)

    def get_all_valid_moves(self, color):
        """
        Get all valid moves for a color (moves that don't leave king in check)

        Args:
            color (str): Color to get moves for

        Returns:
            dict: Dictionary mapping piece positions to their valid moves
        """
        valid_moves = {}

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    piece_moves = piece.get_possible_moves(self)
                    filtered_moves = []

                    # Filter out moves that would leave king in check
                    for move in piece_moves:
                        if self.is_move_legal(piece.position, move):
                            filtered_moves.append(move)

                    if filtered_moves:
                        valid_moves[piece.position] = filtered_moves

        return valid_moves

    def is_move_legal(self, from_pos, to_pos):
        """
        Check if a move is legal (doesn't leave own king in check)

        Args:
            from_pos (tuple): Starting position
            to_pos (tuple): Ending position

        Returns:
            bool: True if move is legal, False otherwise
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Make the move temporarily
        piece = self.grid[from_row][from_col]
        captured_piece = self.grid[to_row][to_col]
        original_pos = piece.position

        # Handle en passant capture temporarily
        en_passant_captured = None
        if isinstance(piece, Pawn) and to_col != from_col and captured_piece is None:
            en_passant_captured = self.grid[from_row][to_col]
            self.grid[from_row][to_col] = None

        self.grid[to_row][to_col] = piece
        self.grid[from_row][from_col] = None
        piece.position = to_pos

        # Check if king is in check
        in_check = self.is_in_check(piece.color)

        # Undo the move
        self.grid[from_row][from_col] = piece
        self.grid[to_row][to_col] = captured_piece
        piece.position = original_pos

        if en_passant_captured:
            self.grid[from_row][to_col] = en_passant_captured

        return not in_check

    def is_checkmate(self, color):
        """
        Check if a color is in checkmate

        Args:
            color (str): Color to check

        Returns:
            bool: True if checkmate, False otherwise
        """
        if not self.is_in_check(color):
            return False

        # Check if there are any valid moves
        valid_moves = self.get_all_valid_moves(color)
        return len(valid_moves) == 0

    def is_stalemate(self, color):
        """
        Check if a color is in stalemate

        Args:
            color (str): Color to check

        Returns:
            bool: True if stalemate, False otherwise
        """
        if self.is_in_check(color):
            return False

        # Check if there are any valid moves
        valid_moves = self.get_all_valid_moves(color)
        return len(valid_moves) == 0


class Game:
    """Main game class that handles the game loop and rendering"""

    def __init__(self, use_images=True):
        """
        Initialize the game

        Args:
            use_images (bool): If True, use PNG images; if False, use Unicode/letters
        """
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Chess Game')
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = 'white'  # White starts
        self.game_over = False
        self.winner = None
        self.use_images = use_images
        self.piece_images = {}
        self.use_unicode = False

        # Try to load piece images
        if use_images:
            try:
                self.load_piece_images()
                print("Loaded piece images successfully!")
            except Exception as e:
                print(f"Could not load piece images: {e}")
                print("Falling back to Unicode/letter mode...")
                self.use_images = False

        # Set up fonts for text mode (fallback or letters)
        if not self.use_images:
            # Try multiple font options for cross-platform compatibility
            font_options = ['segoeuisymbol', 'notosansemoji', 'applesymbols', 'notosans', 'dejavusans', 'freesans', 'arial']
            self.piece_font = None
            for font_name in font_options:
                try:
                    test_font = pygame.font.SysFont(font_name, 70)
                    if test_font:
                        self.piece_font = test_font
                        self.use_unicode = True
                        break
                except:
                    continue

            # Fallback to letter mode if Unicode font not found
            if not self.piece_font:
                self.piece_font = pygame.font.SysFont('arial', 50, bold=True)
                self.use_unicode = False

        self.message_font = pygame.font.SysFont('arial', 40, bold=True)

    def load_piece_images(self):
        """Load all piece images from the pieces directory"""
        import os

        piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        colors = ['white', 'black']

        for color in colors:
            for piece_type in piece_types:
                filename = f'pieces/{color}_{piece_type}.png'
                if not os.path.exists(filename):
                    raise FileNotFoundError(f"Missing piece image: {filename}")

                # Load and scale the image to fit the square
                image = pygame.image.load(filename)
                # Scale to 80% of square size for some padding
                scaled_size = int(SQUARE_SIZE * 0.8)
                image = pygame.transform.scale(image, (scaled_size, scaled_size))
                self.piece_images[f'{color}_{piece_type}'] = image

    def draw_board(self):
        """Draw the chess board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Determine square color
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE

                # Highlight selected piece
                if self.selected_piece == (row, col):
                    color = SELECTED_COLOR

                # Highlight valid moves
                if (row, col) in self.valid_moves:
                    color = HIGHLIGHT_COLOR

                # Draw the square
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )

    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                    if self.use_images:
                        # Use PNG images
                        piece_type = piece.__class__.__name__.lower()
                        image_key = f'{piece.color}_{piece_type}'

                        if image_key in self.piece_images:
                            image = self.piece_images[image_key]
                            image_rect = image.get_rect(center=(center_x, center_y))
                            self.screen.blit(image, image_rect)
                    else:
                        # Use text rendering (Unicode or letters)
                        display_char = piece.symbol if self.use_unicode else piece.letter

                        # Render piece with better colors and outline for visibility
                        if piece.color == 'white':
                            # White pieces: light fill with dark outline
                            outline = self.piece_font.render(display_char, True, BLACK)
                            text = self.piece_font.render(display_char, True, (245, 245, 245))

                            # Draw outline (slightly offset in multiple directions)
                            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                                outline_rect = outline.get_rect(center=(center_x + dx, center_y + dy))
                                self.screen.blit(outline, outline_rect)

                            # Draw main piece
                            text_rect = text.get_rect(center=(center_x, center_y))
                            self.screen.blit(text, text_rect)
                        else:
                            # Black pieces: dark fill with light outline
                            outline = self.piece_font.render(display_char, True, (220, 220, 220))
                            text = self.piece_font.render(display_char, True, (30, 30, 30))

                            # Draw outline (slightly offset in multiple directions)
                            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
                                outline_rect = outline.get_rect(center=(center_x + dx, center_y + dy))
                                self.screen.blit(outline, outline_rect)

                            # Draw main piece
                            text_rect = text.get_rect(center=(center_x, center_y))
                            self.screen.blit(text, text_rect)

    def draw_game_over_message(self):
        """Draw game over message"""
        if self.winner:
            message = f"{self.winner.capitalize()} wins!"
        else:
            message = "Stalemate!"

        text = self.message_font.render(message, True, BLACK)
        text_bg = self.message_font.render(message, True, WHITE)

        # Draw background and text
        rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        bg_rect = rect.inflate(20, 20)
        pygame.draw.rect(self.screen, WHITE, bg_rect)
        pygame.draw.rect(self.screen, BLACK, bg_rect, 3)
        self.screen.blit(text, rect)

    def handle_click(self, pos):
        """
        Handle mouse click events

        Args:
            pos (tuple): Mouse position (x, y)
        """
        if self.game_over:
            return

        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE

        # If a piece is already selected
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                # Make the move
                self.make_move(self.selected_piece, (row, col))
                self.selected_piece = None
                self.valid_moves = []
            else:
                # Try to select a different piece
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.current_turn:
                    self.select_piece(row, col)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Try to select a piece
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.current_turn:
                self.select_piece(row, col)

    def select_piece(self, row, col):
        """
        Select a piece and show its valid moves

        Args:
            row (int): Row of the piece
            col (int): Column of the piece
        """
        self.selected_piece = (row, col)
        piece = self.board.get_piece(row, col)

        # Get valid moves and filter out illegal moves
        all_moves = piece.get_possible_moves(self.board)
        self.valid_moves = [
            move for move in all_moves
            if self.board.is_move_legal((row, col), move)
        ]

    def make_move(self, from_pos, to_pos):
        """
        Make a move and handle pawn promotion

        Args:
            from_pos (tuple): Starting position
            to_pos (tuple): Ending position
        """
        piece = self.board.get_piece(from_pos[0], from_pos[1])

        # Check for pawn promotion
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and to_pos[0] == 0) or (piece.color == 'black' and to_pos[0] == 7):
                # Promote to queen automatically
                self.board.move_piece(from_pos, to_pos)
                self.board.grid[to_pos[0]][to_pos[1]] = Queen(piece.color, to_pos)
                self.switch_turn()
                return

        # Make the move
        self.board.move_piece(from_pos, to_pos)
        self.switch_turn()

    def switch_turn(self):
        """Switch to the other player's turn"""
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Check for checkmate or stalemate
        if self.board.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = 'black' if self.current_turn == 'white' else 'white'
        elif self.board.is_stalemate(self.current_turn):
            self.game_over = True
            self.winner = None

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # Draw everything
            self.draw_board()
            self.draw_pieces()

            if self.game_over:
                self.draw_game_over_message()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Main entry point
if __name__ == '__main__':
    game = Game()
    game.run()
