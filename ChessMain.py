"""
This is our main driver file. It would be responsible for handling user inputs and the current game state.
"""
import pygame as p
import ChessEngine, SmartMoveFinder
import math
import time

WIDTH = HEIGHT = 512  # 400 is another option
DIMENSION = 8  # dimensions of a chess board are 8X8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations
IMAGES = {}

# Extended width for UI elements - INCREASED SIZE TO FIX OVERLAPPING
PANEL_WIDTH = 300  # INCREASED from 200 to 300
WINDOW_HEIGHT = 612  # INCREASED from 512 to 612
TOTAL_WIDTH = WIDTH + PANEL_WIDTH

# NEW: Bottom board section height
BOARD_BOTTOM_HEIGHT = 100  # Height for the new section below chessboard

"""
Initialize a global dictionary of Images. This will be called exactly once in the main.
"""


def load_Images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load("ChessImages/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            print(f"Warning: Could not load image for {piece}. Creating fallback.")
            # Create a colored rectangle as fallback
            surf = p.Surface((SQ_SIZE, SQ_SIZE))
            color = p.Color('red') if piece[0] == 'w' else p.Color('blue')
            surf.fill(color)
            IMAGES[piece] = surf


def draw_gradient_rect(surface, color1, color2, rect, vertical=True):
    """Draw a gradient rectangle"""
    if vertical:
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            p.draw.line(surface, (r, g, b),
                        (rect.x, rect.y + y),
                        (rect.x + rect.width, rect.y + y))


def draw_rounded_rect(surface, color, rect, radius=15):
    """Draw a rectangle with rounded corners"""
    try:
        # Use pygame's built-in rounded rectangle if available
        p.draw.rect(surface, color, rect, border_radius=radius)
    except:
        # Fallback for older pygame versions
        # Main rectangle
        p.draw.rect(surface, color, (rect.x + radius, rect.y, rect.width - 2 * radius, rect.height))
        p.draw.rect(surface, color, (rect.x, rect.y + radius, rect.width, rect.height - 2 * radius))

        # Corner circles
        p.draw.circle(surface, color, (rect.x + radius, rect.y + radius), radius)
        p.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + radius), radius)
        p.draw.circle(surface, color, (rect.x + radius, rect.y + rect.height - radius), radius)
        p.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + rect.height - radius), radius)


# ENHANCED: Chess Move Analyzer Class with better move quality detection
class ChessMoveAnalyzer:
    def __init__(self):
        self.last_move = None
        self.move_quality = "Unknown"
        self.move_type = "Normal"
        self.analysis_visible = True
        self.quick_stats = {
            "captures": 0,
            "checks": 0,
            "castles": 0,
            "promotions": 0,
            "blunders": 0
        }
        # Piece values for material assessment
        self.piece_values = {
            'p': 1,  # pawn
            'N': 3,  # knight
            'B': 3,  # bishop
            'R': 5,  # rook
            'Q': 9,  # queen
            'K': 0  # king (invaluable)
        }

    def calculate_material_value(self, board, color_prefix):
        """Calculate total material value for a color"""
        total_value = 0
        for row in board:
            for square in row:
                if square.startswith(color_prefix) and square != "--":
                    piece_type = square[1]  # Get piece type (p, N, B, R, Q, K)
                    total_value += self.piece_values.get(piece_type, 0)
        return total_value

    def analyze_move_quality(self, move, board_before, board_after, color_moved):
        """ENHANCED: Analyze move quality based on material change and move type"""
        try:
            self.last_move = move

            # Calculate material before and after move
            material_before = self.calculate_material_value(board_before, color_moved)
            material_after = self.calculate_material_value(board_after, color_moved)
            material_change = material_after - material_before

            # Special moves are generally excellent
            if hasattr(move, 'isCastleMove') and move.isCastleMove:
                self.move_type = "Castle"
                self.move_quality = "Excellent"
                self.quick_stats["castles"] += 1
                return

            if hasattr(move, 'isPawnPromotion') and move.isPawnPromotion:
                self.move_type = "Promotion"
                self.move_quality = "Excellent"
                self.quick_stats["promotions"] += 1
                return

            # Check if material was lost (indicating a blunder)
            if material_change < -2:  # Lost significant material
                self.move_type = "Blunder"
                self.move_quality = "Blunder"
                self.quick_stats["blunders"] += 1
                return
            elif material_change < 0:  # Lost some material
                self.move_type = "Mistake"
                self.move_quality = "Mistake"
                return

            # Analyze captures
            captured_piece_value = 0
            if move.pieceCaptured != '--':
                captured_piece_type = move.pieceCaptured[1].lower()
                captured_piece_value = self.piece_values.get(captured_piece_type, 0)

                # Good captures vs bad captures
                if captured_piece_value >= 5:  # Captured rook or queen
                    self.move_type = "Excellent Capture"
                    self.move_quality = "Excellent"
                elif captured_piece_value >= 3:  # Captured bishop or knight
                    self.move_type = "Good Capture"
                    self.move_quality = "Good"
                elif captured_piece_value >= 1:  # Captured pawn
                    self.move_type = "Capture"
                    self.move_quality = "OK"
                else:
                    self.move_type = "Capture"
                    self.move_quality = "OK"

                self.quick_stats["captures"] += 1
                return

            # Non-capturing moves - generally less impressive
            moved_piece = move.pieceMoved[1] if len(move.pieceMoved) > 1 else 'p'

            # Development moves (early game piece movement)
            if moved_piece in ['N', 'B'] and self._is_early_game(board_after):
                self.move_type = "Development"
                self.move_quality = "Good"
            else:
                # Regular moves
                self.move_type = "Normal"
                self.move_quality = "Okay"  # Changed from "OK" to be more neutral

        except Exception as e:
            print(f"Enhanced move analysis error: {e}")
            self.move_type = "Normal"
            self.move_quality = "Unknown"

    def _is_early_game(self, board):
        """Simple check if we're still in early game (many pieces on board)"""
        piece_count = sum(1 for row in board for square in row if square != "--")
        return piece_count > 24  # Early game if more than 24 pieces on board

    def get_move_evaluation(self):
        """Get a textual evaluation of the move with better descriptions"""
        if not self.last_move:
            return "Make a move to see analysis"

        evaluations = {
            "Excellent": "🌟 Excellent move!",
            "Good": "✅ Good move!",
            "OK": "👍 Decent move",
            "Okay": "😐 Okay move",  # NEW: Less enthusiastic
            "Mistake": "⚠️ Questionable move",  # NEW
            "Blunder": "💥 Bad move!",  # NEW
            "Unknown": "🤔 Analyzing..."
        }
        return evaluations.get(self.move_quality, "🤔 Analyzing...")

    def toggle_visibility(self):
        """Toggle the visibility of the analysis"""
        self.analysis_visible = not self.analysis_visible

    def get_rank_file(self, row, col):
        """Convert row, col to chess notation (e.g., e4, d5)"""
        try:
            files = "abcdefgh"
            ranks = "87654321"
            return files[col] + ranks[row]
        except:
            return f"({row},{col})"


def show_enhanced_mode_selection_screen(screen, clock):
    """Show an enhanced mode selection screen with arrow key navigation"""

    # Enhanced fonts
    font_title = p.font.SysFont("Arial", 48, True, False)
    font_subtitle = p.font.SysFont("Arial", 24, False, False)
    font_option = p.font.SysFont("Arial", 28, True, False)
    font_desc = p.font.SysFont("Arial", 18, False, True)  # Italic
    font_instruction = p.font.SysFont("Arial", 16, False, False)

    # Color scheme
    bg_color1 = (45, 55, 72)  # Dark blue-gray
    bg_color2 = (26, 32, 44)  # Darker blue-gray
    title_color = (247, 250, 252)  # Almost white
    subtitle_color = (203, 213, 224)  # Light gray
    option_bg = (255, 255, 255)  # White
    option_bg_selected = (66, 153, 225)  # Blue
    text_color = (26, 32, 44)  # Dark for contrast
    text_color_selected = (255, 255, 255)  # White when selected
    desc_color = (113, 128, 150)  # Medium gray
    desc_color_selected = (237, 242, 247)  # Light when selected

    # Mode options with enhanced descriptions
    mode_options = [
        {
            "title": "Player vs Player",
            "icon": "👥",
            "description": "Two human players compete head-to-head",
            "details": "Classic chess experience for two people"
        },
        {
            "title": "Player vs AI",
            "icon": "🤖",
            "description": "Challenge the computer AI opponent",
            "details": "Test your skills against artificial intelligence"
        },
        {
            "title": "AI vs AI",
            "icon": "⚔️",
            "description": "Watch two AI engines battle each other",
            "details": "Sit back and observe strategic gameplay"
        }
    ]

    selected_index = 1  # Default to Player vs AI
    animation_time = 0
    selection_done = False

    while not selection_done:
        dt = clock.tick(60)
        animation_time += dt

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                exit()
            elif event.type == p.KEYDOWN:
                if event.key == p.K_UP:
                    selected_index = (selected_index - 1) % len(mode_options)
                elif event.key == p.K_DOWN:
                    selected_index = (selected_index + 1) % len(mode_options)
                elif event.key == p.K_1:
                    selected_index = 0
                elif event.key == p.K_2:
                    selected_index = 1
                elif event.key == p.K_3:
                    selected_index = 2
                elif event.key in (p.K_RETURN, p.K_SPACE):
                    selection_done = True
                elif event.key == p.K_ESCAPE:
                    p.quit()
                    exit()

        # Draw gradient background
        screen_rect = p.Rect(0, 0, TOTAL_WIDTH, WINDOW_HEIGHT)
        draw_gradient_rect(screen, bg_color1, bg_color2, screen_rect)

        # Add animated floating particles
        for i in range(15):
            time_offset = (animation_time / 1000.0 + i) * 0.5
            x = 50 + i * 45 + int(20 * math.sin(time_offset))
            y = 100 + (i % 3) * 150 + int(15 * math.cos(time_offset * 0.7))
            if 0 <= x <= TOTAL_WIDTH and 0 <= y <= WINDOW_HEIGHT:
                alpha = int(50 + 30 * math.sin(time_offset * 2))
                particle_surface = p.Surface((6, 6), p.SRCALPHA)
                p.draw.circle(particle_surface, (*subtitle_color, alpha), (3, 3), 3)
                screen.blit(particle_surface, (x - 3, y - 3))

        # Enhanced title with glow effect
        title_text = "🎯 Enhanced Chess Game"
        title_surface = font_title.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(TOTAL_WIDTH // 2, 80))

        # Title glow effect
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]:
            glow_surface = font_title.render(title_text, True, (66, 153, 225))
            screen.blit(glow_surface, (title_rect.x + offset[0], title_rect.y + offset[1]))
        screen.blit(title_surface, title_rect)

        # Animated subtitle
        pulse = 0.8 + 0.2 * math.sin(animation_time / 400)
        subtitle_text = "Select Your Game Mode"
        subtitle_surface = font_subtitle.render(subtitle_text, True, subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(TOTAL_WIDTH // 2, 130))

        # Scale subtitle with pulse
        scaled_subtitle = p.transform.scale(subtitle_surface,
                                            (int(subtitle_surface.get_width() * pulse),
                                             int(subtitle_surface.get_height() * pulse)))
        scaled_rect = scaled_subtitle.get_rect(center=subtitle_rect.center)
        screen.blit(scaled_subtitle, scaled_rect)

        # Mode selection cards
        card_width = TOTAL_WIDTH - 120
        card_height = 90
        start_y = 180
        card_spacing = 100

        for i, option in enumerate(mode_options):
            y_pos = start_y + i * card_spacing
            card_rect = p.Rect((TOTAL_WIDTH - card_width) // 2, y_pos, card_width, card_height)

            # Animation for selected card
            if i == selected_index:
                # Pulsing glow effect
                glow_intensity = 0.7 + 0.3 * math.sin(animation_time / 300)
                glow_size = int(8 * glow_intensity)

                # Draw glow
                glow_rect = p.Rect(card_rect.x - glow_size, card_rect.y - glow_size,
                                   card_width + 2 * glow_size, card_height + 2 * glow_size)
                glow_surface = p.Surface((glow_rect.width, glow_rect.height), p.SRCALPHA)
                draw_rounded_rect(glow_surface, (*option_bg_selected, 60),
                                  p.Rect(0, 0, glow_rect.width, glow_rect.height), 20)
                screen.blit(glow_surface, glow_rect)

                # Selected card background
                draw_rounded_rect(screen, option_bg_selected, card_rect, 15)

                # Selection indicator arrow
                arrow_points = [
                    (card_rect.x - 25, card_rect.y + card_height // 2),
                    (card_rect.x - 10, card_rect.y + card_height // 2 - 10),
                    (card_rect.x - 10, card_rect.y + card_height // 2 + 10)
                ]
                p.draw.polygon(screen, option_bg_selected, arrow_points)

                text_color_current = text_color_selected
                desc_color_current = desc_color_selected

            else:
                # Non-selected card
                draw_rounded_rect(screen, option_bg, card_rect, 15)
                # Subtle border
                try:
                    p.draw.rect(screen, (226, 232, 240), card_rect, 2, border_radius=15)
                except:
                    p.draw.rect(screen, (226, 232, 240), card_rect, 2)

                text_color_current = text_color
                desc_color_current = desc_color

            # Card content
            icon_surface = font_option.render(option["icon"], True, text_color_current)
            screen.blit(icon_surface, (card_rect.x + 20, card_rect.y + 15))

            # Option number
            number_surface = font_option.render(f"{i + 1}.", True, text_color_current)
            screen.blit(number_surface, (card_rect.x + 70, card_rect.y + 15))

            # Title
            title_surface = font_option.render(option["title"], True, text_color_current)
            screen.blit(title_surface, (card_rect.x + 110, card_rect.y + 15))

            # Description
            desc_surface = font_desc.render(option["description"], True, desc_color_current)
            screen.blit(desc_surface, (card_rect.x + 110, card_rect.y + 45))

            # Details
            details_surface = font_instruction.render(option["details"], True, desc_color_current)
            screen.blit(details_surface, (card_rect.x + 110, card_rect.y + 65))

        # Enhanced instructions at bottom
        instruction_y = WINDOW_HEIGHT - 120

        # Instructions background
        instr_rect = p.Rect(60, instruction_y, TOTAL_WIDTH - 120, 100)
        instr_surface = p.Surface((instr_rect.width, instr_rect.height), p.SRCALPHA)
        draw_rounded_rect(instr_surface, (*bg_color1, 180),
                          p.Rect(0, 0, instr_rect.width, instr_rect.height), 10)
        screen.blit(instr_surface, instr_rect)

        # Instruction text with pulsing effect
        pulse_alpha = int(200 + 55 * math.sin(animation_time / 600))

        instructions = [
            "Use ↑↓ Arrow Keys or 1/2/3 to Select Mode",
            "Press ENTER or SPACE to Start Game",
            "Press ESC to Exit"
        ]

        for i, instruction in enumerate(instructions):
            if i == 1:  # Make "Start Game" instruction pulse
                color = (*title_color, pulse_alpha)
                instr_text = font_instruction.render(instruction, True, color[:3])
            else:
                instr_text = font_instruction.render(instruction, True, subtitle_color)

            instr_text_rect = instr_text.get_rect(center=(TOTAL_WIDTH // 2, instruction_y + 25 + i * 25))
            screen.blit(instr_text, instr_text_rect)

        # Version info
        version_text = "Enhanced Chess v2.0"
        version_surface = p.font.SysFont("Arial", 12, False, True).render(version_text, True, (74, 85, 104))
        version_rect = version_surface.get_rect(bottomright=(TOTAL_WIDTH - 15, WINDOW_HEIGHT - 10))
        screen.blit(version_surface, version_rect)

        p.display.flip()

    # Return the selected mode configuration
    if selected_index == 0:
        return True, True  # Player vs Player
    elif selected_index == 1:
        return True, False  # Player vs AI
    else:
        return False, False  # AI vs AI


def get_current_game_mode(playerOne, playerTwo):
    """Get current game mode as a string"""
    if playerOne and playerTwo:
        return "Player vs Player", "👥"
    elif playerOne and not playerTwo:
        return "Player vs AI", "🤖"
    else:
        return "AI vs AI", "⚔️"


"""
The main driver for our code. This will handle user input and updating the graphics.
"""


def main():
    p.init()  # Initializing our pygame
    screen = p.display.set_mode((TOTAL_WIDTH, WINDOW_HEIGHT))
    p.display.set_caption("Enhanced Chess Game with AI")
    clock = p.time.Clock()

    print("Starting Enhanced Chess Game...")

    # Show enhanced mode selection screen first
    try:
        playerOne, playerTwo = show_enhanced_mode_selection_screen(screen, clock)
        print(f"Mode selected: PlayerOne={playerOne}, PlayerTwo={playerTwo}")
    except Exception as e:
        print(f"Error in mode selection: {e}")
        return

    # Initialize game state with error handling
    try:
        gs = ChessEngine.GameState()
        print("ChessEngine initialized successfully")
    except Exception as e:
        print(f"Error initializing ChessEngine: {e}")
        return

    try:
        validMoves = gs.getValidMoves()
        print(f"Valid moves loaded: {len(validMoves)} moves")
    except Exception as e:
        print(f"Error getting valid moves: {e}")
        return

    try:
        load_Images()
        print("Images loaded successfully")
    except Exception as e:
        print(f"Error loading images: {e}")

    # Game variables
    moveMade = False
    animate = False
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    showHints = True
    boardTheme = "classic"
    moveHistory = []
    aiThinking = False

    # ENHANCED: Initialize Move Analyzer for bottom of board
    move_analyzer = ChessMoveAnalyzer()

    print("Entering main game loop...")

    while running:
        try:
            humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                # Mouse handling events
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()

                    # Check if click is on bottom board section
                    bottom_board_y = HEIGHT
                    if (location[0] < WIDTH and
                            bottom_board_y < location[1] < bottom_board_y + BOARD_BOTTOM_HEIGHT):
                        # Toggle analysis visibility on click
                        move_analyzer.toggle_visibility()

                    # Check if click is on the game board
                    elif location[0] < WIDTH and location[1] < HEIGHT:
                        if not gameOver and humanTurn and not aiThinking:
                            col = location[0] // SQ_SIZE
                            row = location[1] // SQ_SIZE
                            if sqSelected == (row, col):
                                sqSelected = ()
                                playerClicks = []
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)
                            if len(playerClicks) == 2:
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                print(f"Attempting move: {move.getChessNotation()}")
                                if move in validMoves:
                                    # ENHANCED: Capture board state before move
                                    board_before = [row[:] for row in gs.board]  # Deep copy

                                    # Make the move
                                    gs.makeMove(move)

                                    # ENHANCED: Capture board state after move
                                    board_after = [row[:] for row in gs.board]  # Deep copy

                                    # ENHANCED: Analyze with before/after board states
                                    color_moved = 'w' if not gs.whiteToMove else 'b'  # Color that just moved
                                    try:
                                        move_analyzer.analyze_move_quality(move, board_before, board_after, color_moved)
                                        print("Enhanced move analysis completed")
                                    except Exception as e:
                                        print(f"Enhanced move analysis error: {e}")

                                    moveMade = True
                                    animate = True
                                    sqSelected = ()
                                    playerClicks = []
                                    moveHistory.append(move.getChessNotation())
                                    print("Move processing completed")
                                else:
                                    playerClicks = [sqSelected]

                # Key handlers
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:  # undo when 'z' is pressed
                        if not aiThinking and len(gs.moveLog) > 0:
                            gs.undoMove()
                            if moveHistory:
                                moveHistory.pop()
                            moveMade = True
                            animate = False
                            gameOver = False
                    elif e.key == p.K_r:  # Reset the board when 'r' is pressed
                        if not aiThinking:
                            gs = ChessEngine.GameState()
                            validMoves = gs.getValidMoves()
                            sqSelected = ()
                            playerClicks = []
                            moveMade = False
                            animate = False
                            gameOver = False
                            moveHistory = []
                            # Reset move analyzer
                            move_analyzer = ChessMoveAnalyzer()
                    elif e.key == p.K_h:  # Toggle hints when 'h' is pressed
                        showHints = not showHints
                    elif e.key == p.K_t:  # Change theme when 't' is pressed
                        themes = ["classic", "green", "blue", "purple"]
                        current_index = themes.index(boardTheme)
                        boardTheme = themes[(current_index + 1) % len(themes)]
                    elif e.key == p.K_1:  # Switch to Player vs Player
                        playerOne = True
                        playerTwo = True
                        print("Mode changed to: Player vs Player")
                    elif e.key == p.K_2:  # Switch to Player vs AI
                        playerOne = True
                        playerTwo = False
                        print("Mode changed to: Player vs AI")
                    elif e.key == p.K_3:  # Switch to AI vs AI
                        playerOne = False
                        playerTwo = False
                        print("Mode changed to: AI vs AI")
                    elif e.key == p.K_m:  # Show mode selection screen again
                        playerOne, playerTwo = show_enhanced_mode_selection_screen(screen, clock)
                    # Toggle analysis visibility
                    elif e.key == p.K_a:  # Toggle analysis with 'a' key
                        move_analyzer.toggle_visibility()

            # AI Move Finder with enhanced error handling
            if not gameOver and not humanTurn and not aiThinking:
                aiThinking = True
                print("AI is thinking...")

                try:
                    if len(validMoves) > 0:
                        AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
                        if AIMove is None:
                            AIMove = SmartMoveFinder.findRandomMoves(validMoves)

                        if AIMove and AIMove in validMoves:
                            # ENHANCED: Capture board state before AI move
                            board_before = [row[:] for row in gs.board]  # Deep copy

                            # Make AI move
                            gs.makeMove(AIMove)

                            # ENHANCED: Capture board state after AI move
                            board_after = [row[:] for row in gs.board]  # Deep copy

                            # ENHANCED: Analyze AI move with before/after board states
                            color_moved = 'w' if not gs.whiteToMove else 'b'  # Color that just moved
                            try:
                                move_analyzer.analyze_move_quality(AIMove, board_before, board_after, color_moved)
                            except Exception as e:
                                print(f"AI move analysis error: {e}")

                            moveHistory.append(AIMove.getChessNotation())
                            moveMade = True
                            animate = True
                            print(f"AI played: {AIMove.getChessNotation()}")
                        else:
                            print("AI couldn't find a valid move")
                    else:
                        print("No valid moves available")
                except Exception as e:
                    print(f"AI Error: {e}")
                    # Fallback to random move if AI fails
                    if len(validMoves) > 0:
                        try:
                            AIMove = SmartMoveFinder.findRandomMoves(validMoves)
                            board_before = [row[:] for row in gs.board]
                            gs.makeMove(AIMove)
                            board_after = [row[:] for row in gs.board]
                            color_moved = 'w' if not gs.whiteToMove else 'b'
                            move_analyzer.analyze_move_quality(AIMove, board_before, board_after, color_moved)
                            moveHistory.append(AIMove.getChessNotation())
                            moveMade = True
                            animate = True
                        except Exception as e2:
                            print(f"Random move fallback failed: {e2}")

                aiThinking = False

            # If a move was made then a new set of valid moves need to be generated
            if moveMade:
                print("Processing move made...")
                if animate:
                    try:
                        animateMove(gs.moveLog[-1], screen, gs.board, clock, boardTheme)
                    except Exception as e:
                        print(f"Animation error: {e}")
                try:
                    validMoves = gs.getValidMoves()
                    print(f"Valid moves updated: {len(validMoves)} moves available")
                except Exception as e:
                    print(f"Error updating valid moves: {e}")
                    validMoves = []
                moveMade = False
                animate = False
                print("Move processing completed")

            # Clear screen with original background
            screen.fill(p.Color("#2C3E50"))

            # Draw the chess board first
            try:
                drawGameState(screen, gs, validMoves, sqSelected, showHints, boardTheme)
            except Exception as e:
                print(f"Error drawing game state: {e}")

            # Draw the bottom board analysis section
            try:
                drawBottomBoardSection(screen, move_analyzer, gs)
            except Exception as e:
                print(f"Error drawing bottom board section: {e}")

            # Draw the enhanced right panel
            try:
                drawRightPanel(screen, gs, moveHistory, playerOne, playerTwo, aiThinking, boardTheme, showHints)
            except Exception as e:
                print(f"Error drawing right panel: {e}")

            # Check for game over conditions
            try:
                if hasattr(gs, 'checkmate') and gs.checkmate:
                    gameOver = True
                    if gs.whiteToMove:
                        drawText(screen, 'Black Wins By Checkmate')
                    else:
                        drawText(screen, 'White Wins By Checkmate')
                elif hasattr(gs, 'stalemate') and gs.stalemate:
                    gameOver = True
                    drawText(screen, 'Stalemate')
            except Exception as e:
                print(f"Error checking game over conditions: {e}")

            clock.tick(MAX_FPS)
            p.display.flip()

        except Exception as e:
            print(f"Main loop error: {e}")
            # Continue running even if there's an error
            clock.tick(MAX_FPS)


def drawBottomBoardSection(screen, move_analyzer, gs):
    """ENHANCED: Draw the interactive analysis section below the chessboard with better move evaluation"""
    try:
        if not move_analyzer.analysis_visible:
            return

        # Define the bottom section area
        bottom_rect = p.Rect(0, HEIGHT, WIDTH, BOARD_BOTTOM_HEIGHT)

        # Gradient background
        color1 = (240, 248, 255)  # Light blue
        color2 = (230, 240, 250)  # Slightly darker blue
        draw_gradient_rect(screen, color1, color2, bottom_rect, vertical=True)

        # Border
        p.draw.rect(screen, p.Color("#34495E"), bottom_rect, 2)

        # Fonts
        font_title = p.font.SysFont("Arial", 16, True, False)
        font_text = p.font.SysFont("Arial", 12, False, False)
        font_small = p.font.SysFont("Arial", 10, False, False)

        text_color = p.Color("#2C3E50")
        accent_color = p.Color("#3498DB")

        # Title
        title_text = "🔍 Enhanced Move Analysis & Stats"
        title_surface = font_title.render(title_text, True, accent_color)
        screen.blit(title_surface, (10, HEIGHT + 8))

        # Last move analysis
        if move_analyzer.last_move:
            # Move evaluation with enhanced feedback
            evaluation = move_analyzer.get_move_evaluation()
            eval_surface = font_text.render(f"Last Move: {evaluation}", True, text_color)
            screen.blit(eval_surface, (10, HEIGHT + 30))

            # Move details with quality assessment
            try:
                move_details = f"Type: {move_analyzer.move_type} | Quality Assessment Complete"
            except Exception as e:
                move_details = f"Type: {move_analyzer.move_type} | Move analyzed"

            details_surface = font_small.render(move_details, True, text_color)
            screen.blit(details_surface, (10, HEIGHT + 48))

            # Enhanced stats with blunder tracking
            stats_y = HEIGHT + 65
            col_width = WIDTH // 5  # Changed to 5 columns

            stats = [
                ("🎯 Captures", move_analyzer.quick_stats["captures"]),
                ("🏰 Castles", move_analyzer.quick_stats["castles"]),
                ("♕ Promotions", move_analyzer.quick_stats["promotions"]),
                ("💥 Blunders", move_analyzer.quick_stats["blunders"]),
                ("📊 Total", len(gs.moveLog) if hasattr(gs, 'moveLog') else 0)
            ]

            for i, (stat_name, stat_value) in enumerate(stats):
                if i < 5:  # Show all 5 stats
                    x_pos = 10 + i * col_width
                    stat_text = f"{stat_name}: {stat_value}"
                    # Highlight blunders in red
                    stat_color = p.Color("#E74C3C") if "Blunders" in stat_name and stat_value > 0 else text_color
                    stat_surface = font_small.render(stat_text, True, stat_color)
                    screen.blit(stat_surface, (x_pos, stats_y))

        else:
            # No moves yet
            no_move_text = "Make your first move to see enhanced analysis!"
            no_move_surface = font_text.render(no_move_text, True, text_color)
            screen.blit(no_move_surface, (10, HEIGHT + 40))

        # Interactive hint
        hint_text = "💡 Now detects blunders and mistakes! | Press 'A' to toggle"
        hint_surface = font_small.render(hint_text, True, p.Color("#7F8C8D"))
        screen.blit(hint_surface, (WIDTH - 380, HEIGHT + BOARD_BOTTOM_HEIGHT - 15))

    except Exception as e:
        print(f"Bottom section drawing error: {e}")


def drawRightPanel(screen, gs, moveHistory, playerOne, playerTwo, aiThinking, boardTheme, showHints):
    """Draw the right panel with FIXED move overflow and meaningful bottom content"""

    # Fill the entire right panel with a lighter gradient background for better text visibility
    panel_rect = p.Rect(WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)

    # Much lighter gradient for better text visibility
    for i in range(PANEL_WIDTH):
        shade = 250 - (i * 0.15)  # Very light gradient
        color = p.Color(int(shade), int(shade), int(shade + 3))
        p.draw.line(screen, color, (WIDTH + i, 0), (WIDTH + i, WINDOW_HEIGHT))

    # Add a subtle border
    p.draw.line(screen, p.Color("#1ABC9C"), (WIDTH, 0), (WIDTH, WINDOW_HEIGHT), 3)

    # Define fonts with better sizes for visibility
    font_title = p.font.SysFont("Arial", 16, True, False)
    font_text = p.font.SysFont("Arial", 13, False, False)
    font_small = p.font.SysFont("Arial", 11, False, False)
    font_tiny = p.font.SysFont("Arial", 10, False, False)

    y_pos = 20
    section_height = 85
    margin = 15

    # Better color scheme with much darker text for visibility
    section_bg = p.Color("#FFFFFF")
    header_bg = p.Color("#3498DB")
    text_color = p.Color("#000000")
    accent_color = p.Color("#E74C3C")
    success_color = p.Color("#27AE60")
    info_color = p.Color("#8B4513")

    # 1. Game Status Section
    status_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, section_height)
    p.draw.rect(screen, section_bg, status_rect)
    p.draw.rect(screen, header_bg, status_rect, 2)

    header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
    p.draw.rect(screen, header_bg, header_rect)

    title = font_title.render("⚔️ Game Status", True, p.Color('white'))
    screen.blit(title, (WIDTH + margin + 8, y_pos + 5))

    move_num = len(gs.moveLog) + 1 if hasattr(gs, 'moveLog') else 1
    current_player = "White" if gs.whiteToMove else "Black"

    status_lines = [
        f"Move: {move_num}",
        f"Turn: {current_player}",
        f"Theme: {boardTheme.title()}"
    ]

    for i, line in enumerate(status_lines):
        color = p.Color('#1565C0') if i == 1 else text_color
        text = font_text.render(line, True, color)
        screen.blit(text, (WIDTH + margin + 12, y_pos + 35 + i * 16))

    y_pos += section_height + 12

    # 2. Game Mode Section
    mode_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, section_height)
    p.draw.rect(screen, section_bg, mode_rect)
    p.draw.rect(screen, p.Color("#9B59B6"), mode_rect, 2)

    header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
    p.draw.rect(screen, p.Color("#9B59B6"), header_rect)

    mode_title = font_title.render("🎮 Game Mode", True, p.Color('white'))
    screen.blit(mode_title, (WIDTH + margin + 8, y_pos + 5))

    mode_name, mode_icon = get_current_game_mode(playerOne, playerTwo)
    mode_text = font_text.render(f"{mode_icon} {mode_name}", True, text_color)
    screen.blit(mode_text, (WIDTH + margin + 12, y_pos + 35))

    if aiThinking:
        thinking_text = font_text.render("🧠 AI is thinking...", True, accent_color)
        screen.blit(thinking_text, (WIDTH + margin + 12, y_pos + 52))
    else:
        ready_text = font_text.render("✅ Ready for move", True, success_color)
        screen.blit(ready_text, (WIDTH + margin + 12, y_pos + 52))

    shortcut_text = font_small.render("Keys: 1=PvP  2=PvAI  3=AIvAI  M=Menu", True, p.Color("#333333"))
    screen.blit(shortcut_text, (WIDTH + margin + 12, y_pos + 69))

    y_pos += section_height + 12

    # 3. FIXED Move History Section - No More Overflow!
    history_height = 120
    history_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, history_height)
    p.draw.rect(screen, section_bg, history_rect)
    p.draw.rect(screen, p.Color("#E67E22"), history_rect, 2)

    header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
    p.draw.rect(screen, p.Color("#E67E22"), header_rect)

    history_title = font_title.render("📜 Recent Moves", True, p.Color('white'))
    screen.blit(history_title, (WIDTH + margin + 8, y_pos + 5))

    # FIXED: Calculate exactly how many moves can fit without overflow
    available_height = history_height - 35
    line_height = 13
    max_moves_that_fit = available_height // line_height

    # Show only the last N moves that can fit in the available space
    recent_moves = moveHistory[-max_moves_that_fit:] if len(moveHistory) > max_moves_that_fit else moveHistory

    if recent_moves:
        for i, move in enumerate(recent_moves):
            move_number = len(moveHistory) - len(recent_moves) + i + 1
            move_text = f"{move_number:2d}. {move}"
            move_color = text_color if i % 2 == 0 else p.Color("#444444")
            text = font_small.render(move_text, True, move_color)
            screen.blit(text, (WIDTH + margin + 12, y_pos + 30 + i * line_height))

        # Show scroll indicator if there are more moves
        if len(moveHistory) > max_moves_that_fit:
            more_moves = len(moveHistory) - max_moves_that_fit
            scroll_text = font_tiny.render(f"... +{more_moves} more moves", True, p.Color("#666666"))
            screen.blit(scroll_text, (WIDTH + margin + 12, y_pos + history_height - 15))
    else:
        no_moves = font_small.render("No moves yet", True, p.Color("#666666"))
        screen.blit(no_moves, (WIDTH + margin + 12, y_pos + 35))

    y_pos += history_height + 12

    # 4. Material Balance Section
    material_height = 75
    material_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, material_height)
    p.draw.rect(screen, section_bg, material_rect)
    p.draw.rect(screen, p.Color("#27AE60"), material_rect, 2)

    header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
    p.draw.rect(screen, p.Color("#27AE60"), header_rect)

    material_title = font_title.render("⚖️ Material", True, p.Color('white'))
    screen.blit(material_title, (WIDTH + margin + 8, y_pos + 5))

    try:
        white_pieces = sum(1 for row in gs.board for square in row if square != "--" and square[0] == 'w')
        black_pieces = sum(1 for row in gs.board for square in row if square != "--" and square[0] == 'b')
    except:
        white_pieces = 16
        black_pieces = 16

    white_text = font_text.render(f"⚪ White: {white_pieces}", True, text_color)
    black_text = font_text.render(f"⚫ Black: {black_pieces}", True, text_color)

    screen.blit(white_text, (WIDTH + margin + 12, y_pos + 32))
    screen.blit(black_text, (WIDTH + margin + 12, y_pos + 50))

    y_pos += material_height + 12

    # 5. Controls Section
    controls_height = 80
    controls_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, controls_height)
    p.draw.rect(screen, section_bg, controls_rect)
    p.draw.rect(screen, p.Color("#E74C3C"), controls_rect, 2)

    header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
    p.draw.rect(screen, p.Color("#E74C3C"), header_rect)

    controls_title = font_title.render("⌨️ Controls", True, p.Color('white'))
    screen.blit(controls_title, (WIDTH + margin + 8, y_pos + 5))

    control_lines = [
        "Z - Undo    R - Reset",
        "H - Hints   T - Theme",
        "A - Toggle Analysis"
    ]

    for i, line in enumerate(control_lines):
        text = font_small.render(line, True, text_color)
        screen.blit(text, (WIDTH + margin + 12, y_pos + 32 + i * 16))

    y_pos += controls_height + 12

    # 6. Game Information Section - FILLING THE REMAINING SPACE
    remaining_height = WINDOW_HEIGHT - y_pos - 15
    if remaining_height > 50:
        info_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, remaining_height)
        p.draw.rect(screen, section_bg, info_rect)
        p.draw.rect(screen, info_color, info_rect, 2)

        header_rect = p.Rect(WIDTH + margin, y_pos, PANEL_WIDTH - 2 * margin, 25)
        p.draw.rect(screen, info_color, header_rect)

        info_title = font_title.render("📊 Game Stats", True, p.Color('white'))
        screen.blit(info_title, (WIDTH + margin + 8, y_pos + 5))

        # Game statistics
        total_moves = len(moveHistory)
        hints_status = "ON" if showHints else "OFF"

        # Calculate game progress
        game_phase = "Opening" if total_moves < 20 else "Middlegame" if total_moves < 40 else "Endgame"

        info_lines = [
            f"Total Moves: {total_moves}",
            f"Game Phase: {game_phase}",
            f"Status: Active",
            f"Hints: {hints_status}",
            f"Enhanced Analysis: ON"
        ]

        # Display info lines that fit in available space
        line_y = y_pos + 32
        for i, line in enumerate(info_lines):
            if line_y + 14 < WINDOW_HEIGHT - 10:
                text = font_tiny.render(line, True, text_color)
                screen.blit(text, (WIDTH + margin + 12, line_y))
                line_y += 14

        # Chess tip at the bottom if space permits
        if line_y + 25 < WINDOW_HEIGHT - 10:
            tip_text = font_tiny.render("💡 Now detecting blunders and mistakes!", True, p.Color("#4A5568"))
            screen.blit(tip_text, (WIDTH + margin + 12, line_y + 10))


def getThemeColors(theme):
    """Get theme colors for the board"""
    themes = {
        "classic": [p.Color("#F0D9B5"), p.Color("#B58863")],
        "green": [p.Color("#EEEED2"), p.Color("#769656")],
        "blue": [p.Color("#DEE3E6"), p.Color("#8CA2AD")],
        "purple": [p.Color("#F7F0FF"), p.Color("#9F90C7")]
    }
    return themes.get(theme, themes["classic"])


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if len(gs.board[r][c]) > 0 and gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # Blue highlight for selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))


def drawMoveHints(screen, gs, validMoves, sqSelected):
    """Draw GREEN DOTS for move hints"""
    if sqSelected != ():
        r, c = sqSelected
        if len(gs.board[r][c]) > 0 and gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    center = (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)
                    if gs.board[move.endRow][move.endCol] != '--':
                        # Capture move - red ring
                        p.draw.circle(screen, p.Color('#E74C3C'), center, SQ_SIZE // 3, 4)
                        p.draw.circle(screen, p.Color('#C0392B'), center, SQ_SIZE // 3 - 8, 2)
                    else:
                        # Normal move - GREEN DOTS
                        p.draw.circle(screen, p.Color('#27AE60'), center, 10)
                        p.draw.circle(screen, p.Color('#2ECC71'), center, 6)


def drawGameState(screen, gs, validMoves, sqSelected, showHints=True, theme="classic"):
    drawBoard(screen, theme)
    highlightSquares(screen, gs, validMoves, sqSelected)
    if showHints:
        drawMoveHints(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen, theme="classic"):
    global colors
    colors = getThemeColors(theme)

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # Add subtle border for better definition
            p.draw.rect(screen, p.Color("#34495E"), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 1)


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--" and piece in IMAGES:
                # Add subtle shadow effect
                shadow_rect = p.Rect(c * SQ_SIZE + 2, r * SQ_SIZE + 2, SQ_SIZE, SQ_SIZE)
                shadow_surf = p.Surface((SQ_SIZE, SQ_SIZE))
                shadow_surf.set_alpha(50)
                shadow_surf.fill(p.Color('black'))
                screen.blit(shadow_surf, shadow_rect)

                # Draw the piece
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock, theme="classic"):
    global colors
    colors = getThemeColors(theme)
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FramesPerSquare = 10
    FrameCount = (abs(dR) + abs(dC)) * FramesPerSquare
    for frame in range(FrameCount + 1):
        r, c = (move.startRow + dR * frame / FrameCount, move.startCol + dC * frame / FrameCount)
        drawBoard(screen, theme)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw the captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.pieceCaptured in IMAGES:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece with original glow effect
        piece_rect = p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        glow_surf = p.Surface((SQ_SIZE + 10, SQ_SIZE + 10))
        glow_surf.set_alpha(100)
        glow_surf.fill(p.Color('#F39C12'))
        screen.blit(glow_surf, (c * SQ_SIZE - 5, r * SQ_SIZE - 5))
        if move.pieceMoved in IMAGES:
            screen.blit(IMAGES[move.pieceMoved], piece_rect)
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    overlay = p.Surface((TOTAL_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(p.Color('#2C3E50'))
    screen.blit(overlay, (0, 0))

    font = p.font.SysFont("Arial", 28, True, False)
    textObject = font.render(text, True, p.Color('#ECF0F1'))

    text_rect = textObject.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT // 2)

    box_rect = text_rect.inflate(40, 20)
    p.draw.rect(screen, p.Color('#34495E'), box_rect)
    p.draw.rect(screen, p.Color('#3498DB'), box_rect, 3)

    shadow_rect = text_rect.copy()
    shadow_rect.x += 2
    shadow_rect.y += 2
    shadow_text = font.render(text, True, p.Color('#2C3E50'))
    screen.blit(shadow_text, shadow_rect)
    screen.blit(textObject, text_rect)


if __name__ == "__main__":
    main()
