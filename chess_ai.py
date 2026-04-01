import pygame
import os
import sys
import chess
import chess.engine

BOARD_WIDTH, HEIGHT = 640, 640
RIGHT_PANEL = 260
WIDTH = BOARD_WIDTH + RIGHT_PANEL
SQ_SIZE = BOARD_WIDTH // 8
PIECES = ['K', 'Q', 'R', 'B', 'N', 'P']

PIECE_SYMBOLS = {
    'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
    'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Game')

# Load piece images
piece_images = {}
for color in ['w', 'b']:
    for piece in PIECES:
        name = f"{color}{piece}"
        path = os.path.join(os.path.dirname(__file__), f"{name}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            img = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))
            piece_images[name] = img

def draw_board():
    colors = [(235, 235, 208), (119, 148, 85)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    # Draw right panel background
    # Top half for black's captured, bottom half for white's captured
    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(BOARD_WIDTH, 0, RIGHT_PANEL, HEIGHT//2))
    pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(BOARD_WIDTH, HEIGHT//2, RIGHT_PANEL, HEIGHT//2))

def draw_pieces(board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            img_name = PIECE_SYMBOLS[piece.symbol()]
            screen.blit(piece_images[img_name], (col*SQ_SIZE, row*SQ_SIZE))

def get_square_under_mouse(pos):
    x, y = pos
    if x >= BOARD_WIDTH or y >= HEIGHT:
        return None
    col = x // SQ_SIZE
    row = 7 - (y // SQ_SIZE)
    return chess.square(col, row)

def show_message(text):
    font = pygame.font.SysFont(None, 48)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    msg = font.render(text, True, (255, 255, 255))
    rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(msg, rect)
    pygame.display.flip()

def highlight_squares(squares, color=(0, 255, 0, 100)):
    highlight = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    highlight.fill(color)
    for square in squares:
        row = 7 - (square // 8)
        col = square % 8
        screen.blit(highlight, (col*SQ_SIZE, row*SQ_SIZE))

def animate_move(board, move, piece_images, delay=0.02):
    from_square = move.from_square
    to_square = move.to_square
    piece = board.piece_at(from_square)
    if not piece:
        return

    img_name = PIECE_SYMBOLS[piece.symbol()]
    img = piece_images[img_name]

    from_row, from_col = 7 - (from_square // 8), from_square % 8
    to_row, to_col = 7 - (to_square // 8), to_square % 8

    frames = 20
    for i in range(1, frames + 1):
        draw_board()
        draw_pieces(board)
        # Interpolate position
        x = from_col * SQ_SIZE + (to_col - from_col) * SQ_SIZE * i / frames
        y = from_row * SQ_SIZE + (to_row - from_row) * SQ_SIZE * i / frames
        screen.blit(img, (x, y))
        pygame.display.flip()
        pygame.time.wait(int(delay * 1000))

def draw_captured_pieces(white_captured, black_captured):
    # Order for display: Queen, Rook, Bishop, Knight, Pawn
    order = ['Q', 'R', 'B', 'N', 'P']
    order_black = [s.lower() for s in order]
    order_white = order

    # Count and order captured pieces
    def ordered_list(captured, order_list):
        result = []
        for piece in order_list:
            result.extend([piece] * captured.count(piece))
        return result

    white_ordered = ordered_list([s.upper() for s in white_captured], order_white)
    black_ordered = ordered_list([s.lower() for s in black_captured], order_black)

    x_start = BOARD_WIDTH + 20
    y_black = 30
    y_white = HEIGHT//2 + 30
    spacing = SQ_SIZE // 2
    per_row = 4

    # Draw black's captured (white's captures)
    for i, symbol in enumerate(black_ordered):
        img_name = PIECE_SYMBOLS[symbol]
        x = x_start + (i % per_row) * spacing
        y = y_black + (i // per_row) * spacing
        screen.blit(piece_images[img_name], (x, y))

    # Draw white's captured (black's captures)
    for i, symbol in enumerate(white_ordered):
        img_name = PIECE_SYMBOLS[symbol]
        x = x_start + (i % per_row) * spacing
        y = y_white + (i // per_row) * spacing
        screen.blit(piece_images[img_name], (x, y))

    # Add labels
    font = pygame.font.SysFont(None, 32)
    black_label = font.render("Black's Captured", True, (255, 255, 255))
    white_label = font.render("White's Captured", True, (0, 0, 0))
    screen.blit(black_label, (BOARD_WIDTH + 20, 5))
    screen.blit(white_label, (BOARD_WIDTH + 20, HEIGHT//2 + 5))

def main():
    board = chess.Board()
    selected_square = None
    running = True
    possible_moves = []
    white_captured = []
    black_captured = []

    # Path to Stockfish executable
    stockfish_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")
    if not os.path.exists(stockfish_path):
        show_message("Stockfish not found!")
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    game_over = False
    game_over_message = ""

    while running:
        draw_board()
        if selected_square is not None:
            highlight_squares([selected_square], color=(0, 0, 255, 80))
            highlight_squares(possible_moves, color=(0, 255, 0, 80))
        draw_pieces(board)
        draw_captured_pieces(white_captured, black_captured)
        if game_over:
            show_message(game_over_message)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                # Human (White) move
                if board.turn == chess.WHITE:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        square = get_square_under_mouse(pygame.mouse.get_pos())
                        if square is None:
                            continue
                        if selected_square is None:
                            piece = board.piece_at(square)
                            if piece and piece.color == chess.WHITE:
                                selected_square = square
                                # Show possible moves for this piece
                                possible_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                            else:
                                selected_square = None
                                possible_moves = []
                        else:
                            move = chess.Move(selected_square, square)
                            if move in board.legal_moves:
                                # Check for capture
                                captured_piece = board.piece_at(square)
                                if captured_piece:
                                    if captured_piece.color == chess.WHITE:
                                        white_captured.append(captured_piece.symbol())
                                    else:
                                        black_captured.append(captured_piece.symbol())
                                board.push(move)
                                selected_square = None
                                possible_moves = []
                            else:
                                # If clicked another own piece, select it
                                piece = board.piece_at(square)
                                if piece and piece.color == chess.WHITE:
                                    selected_square = square
                                    possible_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                                else:
                                    selected_square = None
                                    possible_moves = []
                # Engine (Black) move
                elif board.turn == chess.BLACK:
                    result = engine.play(board, chess.engine.Limit(time=0.1))
                    move = result.move
                    # Check for capture
                    captured_piece = board.piece_at(move.to_square)
                    if captured_piece:
                        if captured_piece.color == chess.WHITE:
                            white_captured.append(captured_piece.symbol())
                        else:
                            black_captured.append(captured_piece.symbol())
                    animate_move(board, move, piece_images, delay=0.03)
                    board.push(move)
                    selected_square = None
                    possible_moves = []

            # Game over detection
            if not game_over and board.is_game_over():
                if board.is_checkmate():
                    winner = "Black" if board.turn == chess.WHITE else "White"
                    game_over_message = f"{winner} wins by checkmate!"
                elif board.is_stalemate():
                    game_over_message = "Draw by stalemate!"
                elif board.is_insufficient_material():
                    game_over_message = "Draw by insufficient material!"
                elif board.is_seventyfive_moves():
                    game_over_message = "Draw by 75-move rule!"
                elif board.is_fivefold_repetition():
                    game_over_message = "Draw by 5-fold repetition!"
                else:
                    game_over_message = "Game over!"
                game_over = True

    engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
