from copy import deepcopy
from pprint import pprint

from .utils import RED_TURN, BLUE_TURN
from .board import BoardGame
import random

class Game:
    def __init__(self, win):
        self.win = win
        self._init()

    def updateGame(self):
        self.board.drawGrid(self.win)
        if self.turn == BLUE_TURN and not self.gameover:
            import pygame
            pygame.time.wait(500)  # Đợi 0.5 giây
            self.bot_move()

    def _init(self):
        """
        Initilize new board
        """
        self.board = BoardGame()
        self.tempBoard = self.board
        self.gameover = False
        self.turn = RED_TURN
        self.selectedPiece = None
        self.enemyPieces = []

    @property
    def isOver(self):
        return self.gameover

    def resetGame(self):
        """
        Reset the game
        """
        self._init()

    def undo(self):
        """
        Undo a move
        """
        if not self.isOver:
            self.board.deselectPiece(self.selectedPiece.position)
            self.board = self.tempBoard
            self.turn = self.board.turn

    def switchTurn(self):
        """
        Switching side
        """
        self.turn = RED_TURN if self.turn == BLUE_TURN else BLUE_TURN
        self.enemyPieces = [
            piece for piece in self.board.activePices if piece.side != self.turn
        ]

    def checkForMove(self, clickedPos):
        """
        Check for click event to move pieces around in the game
        """
        if self.board.isClicked(clickedPos):
            postion = self.board.getPositionFromCoordinate(clickedPos)
            piece = self.board.getPiece(postion)

            if not self.selectedPiece:
                if piece is not None and piece.side == self.board.turn:
                    self.selectedPiece = piece
                    self.selectedPiece.makeSelected()
                    self.board.movables = self.selectedPiece.possibleMoves

            else:
                if piece == self.selectedPiece:
                    self.board.deselectPiece(postion)
                    self.selectedPiece = None
                else:
                    moved = self.move(postion)

                    if not moved:
                        self.board.deselectPiece(self.selectedPiece.getPosition())
                        self.selectedPiece = None

        else:  # If something else other than the board is not clicked, deselect any selected piece
            if self.selectedPiece is not None:
                self.board.deselectPiece(self.selectedPiece.getPosition())
                self.selectedPiece = None

    def move(self, postion):
        if postion in self.board.movables:
            self.tempBoard = deepcopy(self.board)
            captured_piece = self.board.getPiece(postion)  # Lấy quân sắp bị ăn nếu có
            self.board.movePiece(self.selectedPiece.position, postion)
            if captured_piece:
                self.checkGameOverByCapture(captured_piece)
            self.selectedPiece = None
            if not self.gameover:  # Nếu chưa hết thì tiếp tục
                self.switchTurn()
                self.checkForMated()
                if self.calculateNextMoves() == 0:
                    self.gameover = True  # Đánh dấu game kết thúc nếu không còn nước đi
            return True
        else:
            print(f"Cant move there {postion}")
            return False

    def checkForMated(self):
        """
        Check if the lord is under attack
        """
        lordPiece = self.board.getLord(self.turn)
        enemyMoves = []
        for p in self.enemyPieces:
            enemyMoves += p.checkPossibleMove(self.board.grid)

        lordPiece.mated = True if tuple(lordPiece.position) in enemyMoves else False

    def calculateNextMoves(self):
        """
        Calculate the next moves for every piece
        """
        piecesInTurn = [
            piece for piece in self.board.activePices if piece.side == self.turn
        ]  # get all pieces that in the turn to move

        nextMoves = 0

        totalPiecesCheck = 0

        for piece in piecesInTurn:
            moves = piece.checkPossibleMove(self.board.grid)
            validMoves = []

            for move in moves:
                tempBoard = deepcopy(self.board)
                tempPiece = tempBoard.getPiece(piece.getPosition())

                tempBoard.movePiece(tempPiece.position, move)
                lordPiece = tempBoard.getLord(self.turn)

                enemyMoves = []
                for p in tempBoard.activePices:
                    if p.getSide() != self.turn and p.attackingPiece:
                        enemyMoves += p.checkPossibleMove(tempBoard.grid)
                        totalPiecesCheck += 1

                if tuple(lordPiece.position) in enemyMoves or tempBoard.lordTolord():
                    continue

                validMoves.append(move)

            nextMoves += len(validMoves)
            piece.possibleMoves = validMoves

        return nextMoves

    def bot_move(self):
        pieces = [piece for piece in self.board.activePices if piece.side == BLUE_TURN]
        if not pieces:
            return False
        # Ưu tiên nước đi ăn quân
        capture_moves = []
        for piece in pieces:
            moves = piece.checkPossibleMove(self.board.grid)
            for move in moves:
                if self.board.getPiece(move) and self.board.getPiece(move).side == RED_TURN:
                    capture_moves.append((piece, move))
        if capture_moves:
            piece, move = random.choice(capture_moves)
        else:
            # Chọn ngẫu nhiên nếu không có nước đi ăn quân
            valid_moves = []
            for piece in pieces:
                moves = piece.checkPossibleMove(self.board.grid)
                for move in moves:
                    valid_moves.append((piece, move))
            if not valid_moves:
                self.gameover = True  # Đánh dấu game kết thúc nếu không còn nước đi
                print("Không còn nước đi hợp lệ cho bot, game kết thúc.")
                return False
            piece, move = random.choice(valid_moves)

        # Thực hiện nước đi
        self.tempBoard = deepcopy(self.board)

        captured_piece = self.board.getPiece(move)
        self.board.movePiece(piece.position, move)
        if captured_piece:
            self.checkGameOverByCapture(captured_piece)

        self.switchTurn()
        self.checkForMated()
        if self.calculateNextMoves() == 0:
            self.gameover = True
        return True

    def checkGameOverByCapture(self, capturedPiece):
        if capturedPiece.__class__.__name__ == "Lord":
            self.gameover = True
            winner = "Đỏ" if capturedPiece.side == BLUE_TURN else "Xanh"
            print(f"Tướng {capturedPiece.side} bị ăn! {winner} thắng ván cờ.")
            # Cập nhật thêm tình trạng thắng thua
