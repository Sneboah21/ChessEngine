# """
# This class is responsible for storing all the information about the current state of a chess.
# It will also be responsible for determining the valid moves at the current state. It will also keep a move lag.
# """
#
#
# class GameState():
#     # Board is an 8X8 2D list, each element of the list has 2 characters.
#     def __init__(self):  # Constructor (fixed from _init_ to __init__)
#         self.board = [
#             ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
#             ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
#             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
#
#         # It's going to map every letter to the given function that should be called.
#         self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
#                               'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
#         self.whiteToMove = True
#         self.moveLog = []
#         self.whiteKingLocation = (7, 4)  # Might help in castling later
#         self.blackKingLocation = (0, 4)
#         self.checkmate = False
#         self.stalemate = False
#         self.enpassantPossible = () #Coordinates for the square where enpassant capture is possible
#         self.inCheck = False
#         self.pins = []
#         self.checks = []
#         self.currentCastlingRights = CastleRights(True, True, True, True)  # object
#         self.castleRightsLog = [
#             CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs,
#                          self.currentCastlingRights.bqs)]
#
#     """
#     Takes a move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant)
#     """
#
#     def makeMove(self, move):
#         # After moving, the place is left empty
#         self.board[move.startRow][move.startCol] = "--"
#         self.board[move.endRow][move.endCol] = move.pieceMoved
#         self.moveLog.append(move)  # log the move so we can undo it later
#         self.whiteToMove = not self.whiteToMove  # swap players
#         # Update the king's location if moved
#         if move.pieceMoved == 'wK':
#             self.whiteKingLocation = (move.endRow, move.endCol)
#         elif move.pieceMoved == 'bK':
#             self.blackKingLocation = (move.endRow, move.endCol)
#
#         # pawn promotion
#         if move.isPawnPromotion:
#             self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
#
#         #enpassant move
#         if move.isEnpassantMove:
#             self.board[move.startRow][move.endCol] = '--'   #capturing the pawn
#
#         #update enPassantPossible variable
#         if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:     #only on 2 square pawn advances
#             self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
#         else:
#             self.enpassantPossible = ()
#
#
#
#         # Castle Move
#         if move.isCastleMove:
#             if move.endCol - move.startCol == 2:  # Kingside Castle move
#                 self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves the rook
#                 self.board[move.endRow][move.endCol + 1] = '--'  # Erase old Rook
#             else:  # Queenside Castle Move
#                 self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves the rook
#                 self.board[move.endRow][move.endCol - 2] = '--'  # Erase old Rook
#
#         # Update the Castling Rights - whenever it is a rook or a king move
#         self.updateCastleRights(move)
#         self.castleRightsLog.append(
#             CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs,
#                          self.currentCastlingRights.bqs))
#
#     """Undo the last move made"""
#
#     def undoMove(self):
#         if len(self.moveLog) != 0:  # making sure that there is a move to undo
#             move = self.moveLog.pop()  # returns the element and removes it
#             self.board[move.startRow][move.startCol] = move.pieceMoved
#             self.board[move.endRow][move.endCol] = move.pieceCaptured
#             self.whiteToMove = not self.whiteToMove  # Switch turns back
#             # update the King's position if needed
#             if move.pieceMoved == 'wK':
#                 self.whiteKingLocation = (move.startRow, move.startCol)
#             elif move.pieceMoved == 'bK':
#                 self.blackKingLocation = (move.startRow, move.startCol)
#             # Undo Castling rights
#             self.castleRightsLog.pop()  # Get rid of new castle rights from the move we are undoing
#             self.currentCastlingRights = self.castleRightsLog[
#                 -1]  # Set the current castle rights to the last one in the list
#             # Undo the castle move
#             if move.isCastleMove:
#                 if move.endCol - move.startCol == 2:  # king side
#                     self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
#                     self.board[move.endRow][move.endCol - 1] = '--'
#                 else:  # queenside
#                     self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
#                     self.board[move.endRow][move.endCol + 1] = '--'
#             self.checkmate = False
#             self.stalemate = False
#             #undo enpassant
#             if move.isEnpassantMove:
#                 self.board[move.endRow][move.endCol] = '--'     #leave landing square blank
#                 self.board[move.startRow][move.endCol] = move.pieceCaptured
#                 self.enpassantPossible = (move.endRow,move.endCol)
#             #undo a 2 square pawn advance
#             if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
#                 self.enpassantPossible = ()
#
#     """
#     All moves considering checks
#     """
#
#     def getValidMoves(self):
#         tempEnpassantPossible = self.enpassantPossible
#         moves = []
#         self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
#         if self.whiteToMove:
#             kingRow = self.whiteKingLocation[0]
#             kingCol = self.whiteKingLocation[1]
#         else:
#             kingRow = self.blackKingLocation[0]
#             kingCol = self.blackKingLocation[1]
#
#         if self.inCheck:
#             if len(self.checks) == 1:  # Only 1 check, block check or move king
#                 moves = self.getAllPossibleMoves()
#                 # To block a check you must move a piece into one of the squares between the enemy piece and king
#                 check = self.checks[0]  # check information
#                 checkRow = check[0]
#                 checkCol = check[1]
#                 pieceChecking = self.board[checkRow][checkCol]  # Enemy piece causing the check
#                 validSquares = []  # Squares that pieces can move to
#                 # If knight, must capture knight or move king, other pieces can be blocked
#                 if pieceChecking[1] == 'N':
#                     validSquares = [(checkRow, checkCol)]
#                 else:
#                     for i in range(1, 8):
#                         validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
#                         validSquares.append(validSquare)
#                         if validSquare[0] == checkRow and validSquare[1] == checkCol:
#                             break
#                 # Get rid of any moves that don't block check or move king
#                 for i in range(len(moves) - 1, -1, -1):
#                     if moves[i].pieceMoved[1] != 'K':
#                         if (moves[i].endRow, moves[i].endCol) not in validSquares:
#                             moves.remove(moves[i])
#             else:  # double check, king has to move
#                 self.getKingMoves(kingRow, kingCol, moves)
#         else:  # Not in check so all moves are fine
#             moves = self.getAllPossibleMoves()
#
#         # Get castling moves (separate from other moves to avoid recursion)
#         if not self.inCheck:
#             if self.whiteToMove:
#                 self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, allyColor='w')
#             else:
#                 self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves, allyColor='b')
#         self.enpassantPossible = tempEnpassantPossible
#         return moves
#
#     def checkForPinsAndChecks(self):
#         pins = []  # Square where the allied piece is and direction pinned from
#         checks = []  # Squares where  enemy is applying a check
#         inCheck = False
#         if self.whiteToMove:
#             enemyColor = "b"
#             allyColor = "w"
#             startRow = self.whiteKingLocation[0]
#             startCol = self.whiteKingLocation[1]
#         else:
#             enemyColor = "w"
#             allyColor = "b"
#             startRow = self.blackKingLocation[0]
#             startCol = self.blackKingLocation[1]
#         # Check outwards from King for pins and checks, keep track of pins
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
#         for j in range(len(directions)):
#             d = directions[j]
#             possiblePin = ()  # Reset possible Pins
#             for i in range(1, 8):
#                 endRow = startRow + d[0] * i
#                 endCol = startCol + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] == allyColor and endPiece[1] != 'K':
#                         if possiblePin == ():
#                             possiblePin = (endRow, endCol, d[0], d[1])
#                         else:
#                             break
#                     elif endPiece[0] == enemyColor:
#                         type = endPiece[1]
#                         if (0 <= j <= 3 and type == 'R') or \
#                                 (4 <= j <= 7 and type == 'B') or \
#                                 (i == 1 and type == 'p' and (
#                                         (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
#                                 (type == 'Q') or (i == 1 and type == 'K'):
#                             if possiblePin == ():
#                                 inCheck = True
#                                 checks.append((endRow, endCol, d[0], d[1]))
#                                 break
#                             else:
#                                 pins.append(possiblePin)
#                                 break
#                         else:
#                             break
#                 else:
#                     break
#
#         # Check for Knight checks
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         for m in knightMoves:
#             endRow = startRow + m[0]
#             endCol = startCol + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] == enemyColor and endPiece[1] == 'N':
#                     inCheck = True
#                     checks.append((endRow, endCol, m[0], m[1]))
#         return inCheck, pins, checks
#
#     """
#     All moves without considering checks.
#     """
#
#     def getAllPossibleMoves(self):
#         moves = []
#         for r in range(len(self.board)):
#             for c in range(len(self.board[r])):
#                 turn = self.board[r][c][0]
#                 if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
#                     piece = self.board[r][c][1]
#                     self.moveFunctions[piece](r, c, moves)
#         return moves
#
#     """
#     Get all the pawn moves for the pawn located at row, col and add these moves to the list
#     """
#
#     def getPawnMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 self.pins.remove(self.pins[i])
#                 break
#         if self.whiteToMove:
#             if self.board[r - 1][c] == "--":
#                 if not piecePinned or pinDirection == (-1, 0):
#                     moves.append(Move((r, c), (r - 1, c), self.board))
#                     if r == 6 and self.board[r - 2][c] == "--":
#                         moves.append(Move((r, c), (r - 2, c), self.board))
#             # captures
#             if c - 1 >= 0:      #captures to the left
#                 if not piecePinned or pinDirection == (-1, -1):
#                     if self.board[r - 1][c - 1][0] == 'b':
#                         moves.append(Move((r, c), (r - 1, c - 1), self.board))
#                     elif (r-1,c-1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassantPossible=True))
#             if c + 1 <= 7:      #captures to the right
#                 if not piecePinned or pinDirection == (-1, 1):
#                     if self.board[r - 1][c + 1][0] == 'b':
#                         moves.append(Move((r, c), (r - 1, c + 1), self.board))
#                     elif (r-1,c+1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassantPossible=True))
#         else:
#             if self.board[r + 1][c] == "--":
#                 if not piecePinned or pinDirection == (1, 0):
#                     moves.append(Move((r, c), (r + 1, c), self.board))
#                     if r == 1 and self.board[r + 2][c] == "--":
#                         moves.append(Move((r, c), (r + 2, c), self.board))
#             # captures
#             if c - 1 >= 0:
#                 if not piecePinned or pinDirection == (1, -1):
#                     if self.board[r + 1][c - 1][0] == 'w':
#                         moves.append(Move((r, c), (r + 1, c - 1), self.board))
#                     elif (r+1,c-1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassantPossible=True))
#             if c + 1 <= 7:
#                 if not piecePinned or pinDirection == (1, 1):
#                     if self.board[r + 1][c + 1][0] == 'w':
#                         moves.append(Move((r, c), (r + 1, c + 1), self.board))
#                     elif (r+1,c+1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassantPossible=True))
#
#     """Get all the Rook moves:-"""
#
#     def getRookMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 if self.board[r][c][1] != 'Q':
#                     self.pins.remove(self.pins[i])
#                 break
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
#         enemyColor = "b" if self.whiteToMove else "w"
#         for d in directions:
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
#                         endPiece = self.board[endRow][endCol]
#                         if endPiece == "--":
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                         elif endPiece[0] == enemyColor:
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                             break
#                         else:
#                             break
#                 else:
#                     break
#
#     """Get all the Bishop moves:-"""
#
#     def getBishopMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 self.pins.remove(self.pins[i])
#                 break
#         directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
#         enemyColor = "b" if self.whiteToMove else "w"
#         for d in directions:
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
#                         endPiece = self.board[endRow][endCol]
#                         if endPiece == "--":
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                         elif endPiece[0] == enemyColor:
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                             break
#                         else:
#                             break
#                 else:
#                     break
#
#     """Get all the Queen moves:-"""
#
#     def getQueenMoves(self, r, c, moves):
#         self.getRookMoves(r, c, moves)
#         self.getBishopMoves(r, c, moves)
#
#     """Get all the King moves:-"""
#
#     def getKingMoves(self, r, c, moves):
#         rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
#         colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
#         allyColor = "w" if self.whiteToMove else "b"
#         for i in range(8):
#             endRow = r + rowMoves[i]
#             endCol = c + colMoves[i]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] != allyColor:
#                     if allyColor == "w":
#                         self.whiteKingLocation = (endRow, endCol)
#                     else:
#                         self.blackKingLocation = (endRow, endCol)
#                     inCheck, pins, checks = self.checkForPinsAndChecks()
#                     if not inCheck:
#                         moves.append(Move((r, c), (endRow, endCol), self.board))
#                     # Place king back on original Location
#                     if allyColor == "w":
#                         self.whiteKingLocation = (r, c)
#                     else:
#                         self.blackKingLocation = (r, c)
#
#     def updateCastleRights(self, move):
#         if move.pieceMoved == 'wK':
#             self.currentCastlingRights.wks = False
#             self.currentCastlingRights.wqs = False
#         elif move.pieceMoved == 'bK':
#             self.currentCastlingRights.bks = False
#             self.currentCastlingRights.bqs = False
#         elif move.pieceMoved == 'wR':
#             if move.startRow == 7:
#                 if move.startCol == 0:  # Left rook
#                     self.currentCastlingRights.wqs = False
#                 elif move.startCol == 7:  # Right rook
#                     self.currentCastlingRights.wks = False
#         elif move.pieceMoved == 'bR':
#             if move.startRow == 0:
#                 if move.startCol == 0:  # Left rook
#                     self.currentCastlingRights.bqs = False
#                 elif move.startCol == 7:  # Right rook
#                     self.currentCastlingRights.bks = False
#     """Generate all valid Castle Moves for the king at (r,c) and add them to the list of moves"""
#
#     def getCastleMoves(self, r, c, moves, allyColor):
#         if self.inCheck:
#             return
#         if (self.whiteToMove and self.currentCastlingRights.wks) or (
#                 not self.whiteToMove and self.currentCastlingRights.bks):
#             self.getKingsideCastleMoves(r, c, moves, allyColor)
#         if (self.whiteToMove and self.currentCastlingRights.wqs) or (
#                 not self.whiteToMove and self.currentCastlingRights.bqs):
#             self.getQueensideCastleMoves(r, c, moves, allyColor)
#
#     def getKingsideCastleMoves(self, r, c, moves, allyColor):
#         if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
#             if not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor):
#                 moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))
#
#     def getQueensideCastleMoves(self, r, c, moves, allyColor):
#         if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
#             if not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor):
#                 moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
#
#     """Get all the Knight moves:-"""
#
#     def getKnightMoves(self, r, c, moves):
#         piecePinned = False
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 self.pins.remove(self.pins[i])
#                 break
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         allyColor = "w" if self.whiteToMove else "b"
#         for m in knightMoves:
#             endRow = r + m[0]
#             endCol = c + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 if not piecePinned:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] != allyColor:
#                         moves.append(Move((r, c), (endRow, endCol), self.board))
#
#     """Helper method to check if square is under attack without recursion"""
#
#     def squareUnderAttack(self, r, c, allyColor):
#         enemyColor = 'w' if allyColor == 'b' else 'b'
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
#         for j in range(len(directions)):
#             d = directions[j]
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] == allyColor:
#                         break
#                     elif endPiece[0] == enemyColor:
#                         type = endPiece[1]
#                         if (0 <= j <= 3 and type == 'R') or \
#                                 (4 <= j <= 7 and type == 'B') or \
#                                 (i == 1 and type == 'p' and (
#                                         (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
#                                 (type == 'Q') or (i == 1 and type == 'K'):
#                             return True
#                         else:
#                             break
#                 else:
#                     break
#         # Check for knight attacks
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         for m in knightMoves:
#             endRow = r + m[0]
#             endCol = c + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] == enemyColor and endPiece[1] == 'N':
#                     return True
#         return False
#
#
# class CastleRights():
#     def __init__(self, wks, bks, wqs, bqs):  # fixed from _init_ to __init__
#         self.wks = wks
#         self.bks = bks
#         self.wqs = wqs
#         self.bqs = bqs
#
#
# class Move():
#     ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
#     rowsToRanks = {v: k for k, v in ranksToRows.items()}
#     filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
#     colsToFiles = {v: k for k, v in filesToCols.items()}
#
#     def __init__(self, startSq, endSq, board, isCastleMove=False, isEnpassantMove = False):
#         self.startRow = startSq[0]
#         self.startCol = startSq[1]
#         self.endRow = endSq[0]
#         self.endCol = endSq[1]
#         self.pieceMoved = board[self.startRow][self.startCol]
#         self.pieceCaptured = board[self.endRow][self.endCol]
#         #pawn promotion
#         #self.isPawnPromotion = False
#         self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
#             #self.isPawnPromotion = True
#         #en passant
#         self.isEnpassantMove = isEnpassantMove
#         if self.isEnpassantMove:
#             self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
#         # self.isEnpassantMove = False
#         # if self.pieceMoved[1] == 'p' and (self.endRow, self.endCol) == enpassantPossible:
#         #     self.isEnpassantMove = True #--------------------------------------------------------------------------------------------------
#
#         self.isCastleMove = isCastleMove
#         self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
#
#     def __eq__(self, other):  # fixed from _eq_ to __eq__
#         if isinstance(other, Move):
#             return self.moveID == other.moveID
#         return False
#
#     def getChessNotation(self):
#         return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
#
#     def getRankFile(self, r, c):
#         return self.colsToFiles[c] + self.rowsToRanks[r]


# """
# This class is responsible for storing all the information about the current state of a chess.
# It will also be responsible for determining the valid moves at the current state. It will also keep a move lag.
# """
#
#
# class GameState():
#     def __init__(self):
#         # Board is an 8X8 2D list, each element of the list has 2 characters.
#         self.board = [
#             ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
#             ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
#             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
#
#         self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
#                               'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
#         self.whiteToMove = True
#         self.moveLog = []
#         self.whiteKingLocation = (7, 4)
#         self.blackKingLocation = (0, 4)
#         self.checkmate = False
#         self.stalemate = False
#         self.enpassantPossible = ()
#         self.inCheck = False
#         self.pins = []
#         self.checks = []
#         self.currentCastlingRights = CastleRights(True, True, True, True)
#         self.castleRightsLog = [
#             CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
#                          self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
#
#     def makeMove(self, move):
#         self.board[move.startRow][move.startCol] = "--"
#         self.board[move.endRow][move.endCol] = move.pieceMoved
#         self.moveLog.append(move)
#         self.whiteToMove = not self.whiteToMove
#
#         # Update the king's location if moved
#         if move.pieceMoved == 'wK':
#             self.whiteKingLocation = (move.endRow, move.endCol)
#         elif move.pieceMoved == 'bK':
#             self.blackKingLocation = (move.endRow, move.endCol)
#
#         # Pawn promotion
#         if move.isPawnPromotion:
#             self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
#
#         # En passant move
#         if move.isEnpassantMove:
#             self.board[move.startRow][move.endCol] = '--'
#
#         # Update enPassantPossible variable
#         if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
#             self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
#         else:
#             self.enpassantPossible = ()
#
#         # Castle Move
#         if move.isCastleMove:
#             if move.endCol - move.startCol == 2:  # Kingside Castle move
#                 self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
#                 self.board[move.endRow][move.endCol + 1] = '--'
#             else:  # Queenside Castle Move
#                 self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
#                 self.board[move.endRow][move.endCol - 2] = '--'
#
#         # Update the Castling Rights
#         self.updateCastleRights(move)
#         self.castleRightsLog.append(
#             CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
#                          self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
#
#     def undoMove(self):
#         if len(self.moveLog) != 0:
#             move = self.moveLog.pop()
#             self.board[move.startRow][move.startCol] = move.pieceMoved
#             self.board[move.endRow][move.endCol] = move.pieceCaptured
#             self.whiteToMove = not self.whiteToMove
#
#             # Update the King's position if needed
#             if move.pieceMoved == 'wK':
#                 self.whiteKingLocation = (move.startRow, move.startCol)
#             elif move.pieceMoved == 'bK':
#                 self.blackKingLocation = (move.startRow, move.startCol)
#
#             # Undo Castling rights
#             self.castleRightsLog.pop()
#             self.currentCastlingRights = self.castleRightsLog[-1]
#
#             # Undo the castle move
#             if move.isCastleMove:
#                 if move.endCol - move.startCol == 2:  # king side
#                     self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
#                     self.board[move.endRow][move.endCol - 1] = '--'
#                 else:  # queenside
#                     self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
#                     self.board[move.endRow][move.endCol + 1] = '--'
#
#             # Undo enpassant
#             if move.isEnpassantMove:
#                 self.board[move.endRow][move.endCol] = '--'
#                 self.board[move.startRow][move.endCol] = move.pieceCaptured
#                 self.enpassantPossible = (move.endRow, move.endCol)
#
#             # Undo a 2 square pawn advance
#             if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
#                 self.enpassantPossible = ()
#
#     def getValidMoves(self):
#         tempEnpassantPossible = self.enpassantPossible
#         tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
#                                         self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
#
#         moves = []
#         self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
#
#         if self.whiteToMove:
#             kingRow = self.whiteKingLocation[0]
#             kingCol = self.whiteKingLocation[1]
#         else:
#             kingRow = self.blackKingLocation[0]
#             kingCol = self.blackKingLocation[1]
#
#         if self.inCheck:
#             if len(self.checks) == 1:
#                 moves = self.getAllPossibleMoves()
#                 check = self.checks[0]
#                 checkRow = check[0]
#                 checkCol = check[1]
#                 pieceChecking = self.board[checkRow][checkCol]
#                 validSquares = []
#
#                 if pieceChecking[1] == 'N':
#                     validSquares = [(checkRow, checkCol)]
#                 else:
#                     for i in range(1, 8):
#                         validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
#                         validSquares.append(validSquare)
#                         if validSquare[0] == checkRow and validSquare[1] == checkCol:
#                             break
#
#                 for i in range(len(moves) - 1, -1, -1):
#                     if moves[i].pieceMoved[1] != 'K':
#                         if (moves[i].endRow, moves[i].endCol) not in validSquares:
#                             moves.remove(moves[i])
#             else:
#                 self.getKingMoves(kingRow, kingCol, moves)
#         else:
#             moves = self.getAllPossibleMoves()
#             if self.whiteToMove:
#                 self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
#             else:
#                 self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
#
#         # Check for checkmate and stalemate
#         if len(moves) == 0:
#             if self.inCheck:
#                 self.checkmate = True
#             else:
#                 self.stalemate = True
#         else:
#             self.checkmate = False
#             self.stalemate = False
#
#         self.enpassantPossible = tempEnpassantPossible
#         self.currentCastlingRights = tempCastleRights
#         return moves
#
#     def checkForPinsAndChecks(self):
#         pins = []
#         checks = []
#         inCheck = False
#
#         if self.whiteToMove:
#             enemyColor = "b"
#             allyColor = "w"
#             startRow = self.whiteKingLocation[0]
#             startCol = self.whiteKingLocation[1]
#         else:
#             enemyColor = "w"
#             allyColor = "b"
#             startRow = self.blackKingLocation[0]
#             startCol = self.blackKingLocation[1]
#
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
#         for j in range(len(directions)):
#             d = directions[j]
#             possiblePin = ()
#             for i in range(1, 8):
#                 endRow = startRow + d[0] * i
#                 endCol = startCol + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] == allyColor and endPiece[1] != 'K':
#                         if possiblePin == ():
#                             possiblePin = (endRow, endCol, d[0], d[1])
#                         else:
#                             break
#                     elif endPiece[0] == enemyColor:
#                         type = endPiece[1]
#                         if (0 <= j <= 3 and type == 'R') or \
#                                 (4 <= j <= 7 and type == 'B') or \
#                                 (i == 1 and type == 'p' and (
#                                         (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
#                                 (type == 'Q') or (i == 1 and type == 'K'):
#                             if possiblePin == ():
#                                 inCheck = True
#                                 checks.append((endRow, endCol, d[0], d[1]))
#                                 break
#                             else:
#                                 pins.append(possiblePin)
#                                 break
#                         else:
#                             break
#                 else:
#                     break
#
#         # Check for Knight checks
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         for m in knightMoves:
#             endRow = startRow + m[0]
#             endCol = startCol + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] == enemyColor and endPiece[1] == 'N':
#                     inCheck = True
#                     checks.append((endRow, endCol, m[0], m[1]))
#         return inCheck, pins, checks
#
#     def getAllPossibleMoves(self):
#         moves = []
#         for r in range(len(self.board)):
#             for c in range(len(self.board[r])):
#                 turn = self.board[r][c][0]
#                 if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
#                     piece = self.board[r][c][1]
#                     self.moveFunctions[piece](r, c, moves)
#         return moves
#
#     def getPawnMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 self.pins.remove(self.pins[i])
#                 break
#
#         if self.whiteToMove:
#             if self.board[r - 1][c] == "--":
#                 if not piecePinned or pinDirection == (-1, 0):
#                     moves.append(Move((r, c), (r - 1, c), self.board))
#                     if r == 6 and self.board[r - 2][c] == "--":
#                         moves.append(Move((r, c), (r - 2, c), self.board))
#             # captures
#             if c - 1 >= 0:
#                 if not piecePinned or pinDirection == (-1, -1):
#                     if self.board[r - 1][c - 1][0] == 'b':
#                         moves.append(Move((r, c), (r - 1, c - 1), self.board))
#                     elif (r - 1, c - 1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
#             if c + 1 <= 7:
#                 if not piecePinned or pinDirection == (-1, 1):
#                     if self.board[r - 1][c + 1][0] == 'b':
#                         moves.append(Move((r, c), (r - 1, c + 1), self.board))
#                     elif (r - 1, c + 1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
#         else:
#             if self.board[r + 1][c] == "--":
#                 if not piecePinned or pinDirection == (1, 0):
#                     moves.append(Move((r, c), (r + 1, c), self.board))
#                     if r == 1 and self.board[r + 2][c] == "--":
#                         moves.append(Move((r, c), (r + 2, c), self.board))
#             # captures
#             if c - 1 >= 0:
#                 if not piecePinned or pinDirection == (1, -1):
#                     if self.board[r + 1][c - 1][0] == 'w':
#                         moves.append(Move((r, c), (r + 1, c - 1), self.board))
#                     elif (r + 1, c - 1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
#             if c + 1 <= 7:
#                 if not piecePinned or pinDirection == (1, 1):
#                     if self.board[r + 1][c + 1][0] == 'w':
#                         moves.append(Move((r, c), (r + 1, c + 1), self.board))
#                     elif (r + 1, c + 1) == self.enpassantPossible:
#                         moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
#
#     def getRookMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 if self.board[r][c][1] != 'Q':
#                     self.pins.remove(self.pins[i])
#                 break
#
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
#         enemyColor = "b" if self.whiteToMove else "w"
#         for d in directions:
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
#                         endPiece = self.board[endRow][endCol]
#                         if endPiece == "--":
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                         elif endPiece[0] == enemyColor:
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                             break
#                         else:
#                             break
#                 else:
#                     break
#
#     def getBishopMoves(self, r, c, moves):
#         piecePinned = False
#         pinDirection = ()
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 self.pins.remove(self.pins[i])
#                 break
#
#         directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
#         enemyColor = "b" if self.whiteToMove else "w"
#         for d in directions:
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
#                         endPiece = self.board[endRow][endCol]
#                         if endPiece == "--":
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                         elif endPiece[0] == enemyColor:
#                             moves.append(Move((r, c), (endRow, endCol), self.board))
#                             break
#                         else:
#                             break
#                 else:
#                     break
#
#     def getQueenMoves(self, r, c, moves):
#         self.getRookMoves(r, c, moves)
#         self.getBishopMoves(r, c, moves)
#
#     def getKingMoves(self, r, c, moves):
#         rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
#         colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
#         allyColor = "w" if self.whiteToMove else "b"
#         for i in range(8):
#             endRow = r + rowMoves[i]
#             endCol = c + colMoves[i]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] != allyColor:
#                     if allyColor == "w":
#                         self.whiteKingLocation = (endRow, endCol)
#                     else:
#                         self.blackKingLocation = (endRow, endCol)
#                     inCheck, pins, checks = self.checkForPinsAndChecks()
#                     if not inCheck:
#                         moves.append(Move((r, c), (endRow, endCol), self.board))
#                     if allyColor == "w":
#                         self.whiteKingLocation = (r, c)
#                     else:
#                         self.blackKingLocation = (r, c)
#
#     def getKnightMoves(self, r, c, moves):
#         piecePinned = False
#         for i in range(len(self.pins) - 1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piecePinned = True
#                 self.pins.remove(self.pins[i])
#                 break
#
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         allyColor = "w" if self.whiteToMove else "b"
#         for m in knightMoves:
#             endRow = r + m[0]
#             endCol = c + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 if not piecePinned:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] != allyColor:
#                         moves.append(Move((r, c), (endRow, endCol), self.board))
#
#     def updateCastleRights(self, move):
#         if move.pieceMoved == 'wK':
#             self.currentCastlingRights.wks = False
#             self.currentCastlingRights.wqs = False
#         elif move.pieceMoved == 'bK':
#             self.currentCastlingRights.bks = False
#             self.currentCastlingRights.bqs = False
#         elif move.pieceMoved == 'wR':
#             if move.startRow == 7:
#                 if move.startCol == 0:
#                     self.currentCastlingRights.wqs = False
#                 elif move.startCol == 7:
#                     self.currentCastlingRights.wks = False
#         elif move.pieceMoved == 'bR':
#             if move.startRow == 0:
#                 if move.startCol == 0:
#                     self.currentCastlingRights.bqs = False
#                 elif move.startCol == 7:
#                     self.currentCastlingRights.bks = False
#
#     def getCastleMoves(self, r, c, moves):
#         if self.inCheck:
#             return
#         if (self.whiteToMove and self.currentCastlingRights.wks) or (
#                 not self.whiteToMove and self.currentCastlingRights.bks):
#             self.getKingsideCastleMoves(r, c, moves)
#         if (self.whiteToMove and self.currentCastlingRights.wqs) or (
#                 not self.whiteToMove and self.currentCastlingRights.bqs):
#             self.getQueensideCastleMoves(r, c, moves)
#
#     def getKingsideCastleMoves(self, r, c, moves):
#         if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
#             if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
#                 moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))
#
#     def getQueensideCastleMoves(self, r, c, moves):
#         if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
#             if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
#                 moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
#
#     def squareUnderAttack(self, r, c):
#         allyColor = 'w' if self.whiteToMove else 'b'
#         enemyColor = 'w' if allyColor == 'b' else 'b'
#         directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
#         for j in range(len(directions)):
#             d = directions[j]
#             for i in range(1, 8):
#                 endRow = r + d[0] * i
#                 endCol = c + d[1] * i
#                 if 0 <= endRow < 8 and 0 <= endCol < 8:
#                     endPiece = self.board[endRow][endCol]
#                     if endPiece[0] == allyColor:
#                         break
#                     elif endPiece[0] == enemyColor:
#                         type = endPiece[1]
#                         if (0 <= j <= 3 and type == 'R') or \
#                                 (4 <= j <= 7 and type == 'B') or \
#                                 (i == 1 and type == 'p' and (
#                                         (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
#                                 (type == 'Q') or (i == 1 and type == 'K'):
#                             return True
#                         else:
#                             break
#                 else:
#                     break
#         # Check for knight attacks
#         knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
#         for m in knightMoves:
#             endRow = r + m[0]
#             endCol = c + m[1]
#             if 0 <= endRow < 8 and 0 <= endCol < 8:
#                 endPiece = self.board[endRow][endCol]
#                 if endPiece[0] == enemyColor and endPiece[1] == 'N':
#                     return True
#         return False
#
#
# class CastleRights():
#     def __init__(self, wks, bks, wqs, bqs):
#         self.wks = wks
#         self.bks = bks
#         self.wqs = wqs
#         self.bqs = bqs
#
#
# class Move():
#     ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
#     rowsToRanks = {v: k for k, v in ranksToRows.items()}
#     filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
#     colsToFiles = {v: k for k, v in filesToCols.items()}
#
#     def __init__(self, startSq, endSq, board, isCastleMove=False, isEnpassantMove=False):
#         self.startRow = startSq[0]
#         self.startCol = startSq[1]
#         self.endRow = endSq[0]
#         self.endCol = endSq[1]
#         self.pieceMoved = board[self.startRow][self.startCol]
#         self.pieceCaptured = board[self.endRow][self.endCol]
#
#         # Pawn promotion
#         self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
#                     self.pieceMoved == 'bp' and self.endRow == 7)
#
#         # En passant
#         self.isEnpassantMove = isEnpassantMove
#         if self.isEnpassantMove:
#             self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
#
#         self.isCastleMove = isCastleMove
#         self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
#
#     def __eq__(self, other):
#         if isinstance(other, Move):
#             return self.moveID == other.moveID
#         return False
#
#     def getChessNotation(self):
#         return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
#
#     def getRankFile(self, r, c):
#         return self.colsToFiles[c] + self.rowsToRanks[r]

"""
This class is responsible for storing all the information about the current state of a chess.
It will also be responsible for determining the valid moves at the current state. It will also keep a move lag.
"""

class GameState():
    def __init__(self):
        # Board is an 8X8 2D list, each element of the list has 2 characters.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                         self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # FIXED: En passant move - Remove the captured pawn from the correct location
        if move.isEnpassantMove:
            # Remove the captured pawn (not at the landing square, but at the passed square)
            if move.pieceMoved[0] == 'w':  # White pawn capturing
                self.board[move.endRow + 1][move.endCol] = '--'  # Remove black pawn behind
            else:  # Black pawn capturing
                self.board[move.endRow - 1][move.endCol] = '--'  # Remove white pawn behind

        # FIXED: Update enPassantPossible variable - only when pawn moves 2 squares
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside Castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # Queenside Castle Move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # Update the Castling Rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                         self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Update the King's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo Castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            # Undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            # FIXED: Undo enpassant - restore the captured pawn to correct location
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # Remove pawn from landing square
                if move.pieceMoved[0] == 'w':  # White pawn captured black pawn
                    self.board[move.endRow + 1][move.endCol] = move.pieceCaptured
                else:  # Black pawn captured white pawn
                    self.board[move.endRow - 1][move.endCol] = move.pieceCaptured

            # FIXED: Restore en passant possibility from previous move
            if len(self.moveLog) > 0:
                prevMove = self.moveLog[-1]
                if prevMove.pieceMoved[1] == 'p' and abs(prevMove.startRow - prevMove.endRow) == 2:
                    self.enpassantPossible = ((prevMove.startRow + prevMove.endRow) // 2, prevMove.startCol)
                else:
                    self.enpassantPossible = ()
            else:
                self.enpassantPossible = ()

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if (moves[i].endRow, moves[i].endCol) not in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # Check for checkmate and stalemate
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        # Check for Knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # captures
            if c - 1 >= 0:
                if not piecePinned or pinDirection == (-1, -1):
                    if self.board[r - 1][c - 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if not piecePinned or pinDirection == (-1, 1):
                    if self.board[r - 1][c + 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0:
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[r + 1][c - 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    # FIXED: Update castling rights when pieces move or are captured
    def updateCastleRights(self, move):
        # King moves - lose all castling rights
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        # Rook moves - lose castling rights for that side
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # Queenside rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # Kingside rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # Queenside rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # Kingside rook
                    self.currentCastlingRights.bks = False

        # FIXED: If rook is captured, lose castling rights
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        # FIXED: Check all three squares are empty for queenside castling
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def squareUnderAttack(self, r, c):
        allyColor = 'w' if self.whiteToMove else 'b'
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:
                            break
                else:
                    break
        # Check for knight attacks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    return True
        return False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isCastleMove=False, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                    self.pieceMoved == 'bp' and self.endRow == 7)

        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
