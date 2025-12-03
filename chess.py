import pygame
import sys
import os

pygame.init()

# Permanent Constants
WINDOW = 800
B_SIZE = 8
SQ_SIZE = WINDOW // B_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
L_COL = (240, 217, 181)
D_COL = (181, 136, 99)
HIGH = (186, 202, 68)
SEL = (246, 246, 130)

class Piece:
    def __init__(self, color, type, pos):
        self.color = color
        self.type = type
        self.pos = pos
        self.moved = False
        
    def get_moves(self, board):
        moves = []
        r, c = self.pos
        
        if self.type == 'pawn':
            if self.color == 'white':
                d = -1
            else:
                d = 1
            
            # move 1
            if 0 <= r + d < 8 and board.grid[r+d][c] is None:
                moves.append((r+d, c))
                # move 2
                if not self.moved and 0 <= r + 2*d < 8 and board.grid[r+2*d][c] is None:
                    moves.append((r+2*d, c))
            
            # capture
            for x in [-1, 1]:
                if 0 <= r + d < 8 and 0 <= c + x < 8:
                    p = board.grid[r+d][c+x]
                    if p and p.color != self.color:
                        moves.append((r+d, c+x))
                        
            # en passant
            if board.last_move:
                lf, lt, lp = board.last_move
                if lp.type == 'pawn' and abs(lf[0] - lt[0]) == 2:
                    if r == lt[0] and abs(c - lt[1]) == 1:
                        if self.color != lp.color:
                            moves.append((r+d, lt[1]))

        elif self.type == 'rook':
            dirs = [(0,1), (0,-1), (1,0), (-1,0)]
            for dr, dc in dirs:
                for i in range(1, 8):
                    nr, nc = r + dr*i, c + dc*i
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        p = board.grid[nr][nc]
                        if p is None:
                            moves.append((nr, nc))
                        elif p.color != self.color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break

        elif self.type == 'knight':
            km = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dr, dc in km:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    p = board.grid[nr][nc]
                    if p is None or p.color != self.color:
                        moves.append((nr, nc))

        elif self.type == 'bishop':
            dirs = [(1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in dirs:
                for i in range(1, 8):
                    nr, nc = r + dr*i, c + dc*i
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        p = board.grid[nr][nc]
                        if p is None:
                            moves.append((nr, nc))
                        elif p.color != self.color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break

        elif self.type == 'queen':
            dirs = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in dirs:
                for i in range(1, 8):
                    nr, nc = r + dr*i, c + dc*i
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        p = board.grid[nr][nc]
                        if p is None:
                            moves.append((nr, nc))
                        elif p.color != self.color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break

        elif self.type == 'king':
            dirs = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    p = board.grid[nr][nc]
                    if p is None or p.color != self.color:
                        moves.append((nr, nc))
            
            # castling
            if not self.moved:
                # kingside
                if isinstance(board.grid[r][7], Piece) and board.grid[r][7].type == 'rook' and not board.grid[r][7].moved:
                    if board.grid[r][5] is None and board.grid[r][6] is None:
                        if not board.is_attacked(r, c, self.color) and \
                           not board.is_attacked(r, 5, self.color) and \
                           not board.is_attacked(r, 6, self.color):
                            moves.append((r, 6))
                # queenside
                if isinstance(board.grid[r][0], Piece) and board.grid[r][0].type == 'rook' and not board.grid[r][0].moved:
                    if board.grid[r][1] is None and board.grid[r][2] is None and board.grid[r][3] is None:
                        if not board.is_attacked(r, c, self.color) and \
                           not board.is_attacked(r, 3, self.color) and \
                           not board.is_attacked(r, 2, self.color):
                            moves.append((r, 2))

        return moves

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.setup()
        
    def setup(self):
        # pawns
        for i in range(8):
            self.grid[1][i] = Piece('black', 'pawn', (1, i))
            self.grid[6][i] = Piece('white', 'pawn', (6, i))
            
        # others
        layout = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i, t in enumerate(layout):
            self.grid[0][i] = Piece('black', t, (0, i))
            self.grid[7][i] = Piece('white', t, (7, i))

    def move(self, start, end):
        sr, sc = start
        er, ec = end
        p = self.grid[sr][sc]
        
        if not p: return False
        
        # en passant capture
        if p.type == 'pawn' and sc != ec and self.grid[er][ec] is None:
            self.grid[sr][ec] = None
            
        # castling
        if p.type == 'king' and abs(sc - ec) == 2:
            if ec > sc: # kingside
                r = self.grid[sr][7]
                self.grid[sr][7] = None
                self.grid[sr][5] = r
                r.pos = (sr, 5)
                r.moved = True
            else: # queenside
                r = self.grid[sr][0]
                self.grid[sr][0] = None
                self.grid[sr][3] = r
                r.pos = (sr, 3)
                r.moved = True
                
        self.grid[er][ec] = p
        self.grid[sr][sc] = None
        p.pos = end
        p.moved = True
        self.last_move = (start, end, p)
        return True

    def is_attacked(self, r, c, color):
        opp = 'black' if color == 'white' else 'white'
        for i in range(8):
            for j in range(8):
                p = self.grid[i][j]
                if p and p.color == opp:
                    #  check for king to avoid recursion
                    if p.type == 'king':
                        if abs(r-i) <= 1 and abs(c-j) <= 1:
                            return True
                    else:
                        # temporarily disable recursion checks if we had them
                        # we  call get_moves which doesn't check for check
                        moves = p.get_moves(self)
                        if (r, c) in moves:
                            return True
        return False

    def is_check(self, color):
        kp = None
        for i in range(8):
            for j in range(8):
                p = self.grid[i][j]
                if p and p.type == 'king' and p.color == color:
                    kp = (i, j)
                    break
        if not kp: return False
        return self.is_attacked(kp[0], kp[1], color)

    def get_valid_moves(self, color):
        valid = {}
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color:
                    pm = p.get_moves(self)
                    vm = []
                    for m in pm:
                        # try move
                        tr, tc = m
                        cap = self.grid[tr][tc]
                        old_pos = p.pos
                        
                        # handle en passant temp
                        ep_cap = None
                        if p.type == 'pawn' and c != tc and cap is None:
                            ep_cap = self.grid[r][tc]
                            self.grid[r][tc] = None
                            
                        self.grid[tr][tc] = p
                        self.grid[r][c] = None
                        p.pos = m
                        
                        if not self.is_check(color):
                            vm.append(m)
                            
                        # undo
                        self.grid[r][c] = p
                        self.grid[tr][tc] = cap
                        p.pos = old_pos
                        if ep_cap:
                            self.grid[r][tc] = ep_cap
                            
                    if vm:
                        valid[p.pos] = vm
        return valid

def main():
    screen = pygame.display.set_mode((WINDOW, WINDOW))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    board = Board()
    
    # load images
    imgs = {}
    try:
        for c in ['white', 'black']:
            for t in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
                # Using the hyphenated names as fixed previously
                path = f'pieces/{c}-{t}.png'
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (int(SQ_SIZE*0.8), int(SQ_SIZE*0.8)))
                imgs[f'{c}_{t}'] = img
    except Exception as e:
        print("Error loading images:", e)
        
    sel = None
    valid = []
    turn = 'white'
    game_over = False
    winner = None
    
    font = pygame.font.SysFont('arial', 32, bold=True)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                c, r = pos[0] // SQ_SIZE, pos[1] // SQ_SIZE
                
                if sel:
                    if (r, c) in valid:
                        board.move(sel, (r, c))
                        turn = 'black' if turn == 'white' else 'white'
                        sel = None
                        valid = []
                        
                        # check game over
                        if not board.get_valid_moves(turn):
                            game_over = True
                            if board.is_check(turn):
                                winner = 'Black' if turn == 'white' else 'White'
                            else:
                                winner = 'Draw'
                    else:
                        sel = None
                        valid = []
                
                p = board.grid[r][c]
                if p and p.color == turn:
                    sel = (r, c)
                    valid_moves_dict = board.get_valid_moves(turn)
                    valid = valid_moves_dict.get(sel, [])

        # Draw
        for r in range(8):
            for c in range(8):
                color = L_COL if (r+c)%2 == 0 else D_COL
                if sel == (r, c): color = SEL
                elif (r, c) in valid: color = HIGH
                
                pygame.draw.rect(screen, color, (c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
                p = board.grid[r][c]
                if p:
                    img = imgs.get(f'{p.color}_{p.type}')
                    if img:
                        rect = img.get_rect(center=(c*SQ_SIZE + SQ_SIZE//2, r*SQ_SIZE + SQ_SIZE//2))
                        screen.blit(img, rect)
        
        if game_over:
            msg = f"{winner} wins!" if winner != 'Draw' else "Stalemate!"
            text = font.render(msg, True, BLACK)
            text_bg = font.render(msg, True, WHITE)
            
            # center
            rect = text.get_rect(center=(WINDOW//2, WINDOW//2))
            bg_rect = rect.inflate(20, 20)
            
            pygame.draw.rect(screen, WHITE, bg_rect)
            pygame.draw.rect(screen, BLACK, bg_rect, 3)
            screen.blit(text, rect)
                        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
