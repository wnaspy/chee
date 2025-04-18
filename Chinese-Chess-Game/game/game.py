from copy import deepcopy
import random
import pygame

from .utils import RED_TURN, BLUE_TURN
from .board import BoardGame


class Game:
    def __init__(self, win):
        self.win = win
        self._init()

    def updateGame(self):
        self.board.drawGrid(self.win)
        if self.turn == BLUE_TURN and not self.gameover:
            pygame.time.wait(500)
            self.bot_move()

    def _init(self):
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
        self._init()

    def undo(self):
        if not self.isOver:
            self.board.deselectPiece(self.selectedPiece.position)
            self.board = self.tempBoard
            self.turn = self.board.turn

    def switchTurn(self):
        self.turn = RED_TURN if self.turn == BLUE_TURN else BLUE_TURN
        self.enemyPieces = [
            piece for piece in self.board.activePices if piece.side != self.turn
        ]

    def checkForMove(self, clickedPos):
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
                        self.checkForMove(clickedPos)
        else:
            #hehe
            if self.selectedPiece is not None:
                self.board.deselectPiece(self.selectedPiece.getPosition())
                self.selectedPiece = None

    def move(self, postion):
        if postion in self.board.movables:
            capturedPiece = self.board.getPiece(postion)
            self.tempBoard = deepcopy(self.board)
            self.board.movePiece(self.selectedPiece.position, postion)
            self.selectedPiece = None
            if capturedPiece:
                self.checkGameOverByCapture(capturedPiece)
            self.switchTurn()
            self.checkForMated()
            if self.calculateNextMoves() == 0:
                self.gameover = True
            return True
        else:
            print(f"Cant move there {postion}")
            return False

    def checkForMated(self):
        lordPiece = self.board.getLord(self.turn)
        enemyMoves = []
        for p in self.enemyPieces:
            enemyMoves += p.checkPossibleMove(self.board.grid)

        lordPiece.mated = True if tuple(lordPiece.position) in enemyMoves else False

    def calculateNextMoves(self):
        piecesInTurn = [
            piece for piece in self.board.activePices if piece.side == self.turn
        ]
        nextMoves = 0

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

        capture_moves = []
        for piece in pieces:
            moves = piece.checkPossibleMove(self.board.grid)
            for move in moves:
                if self.board.getPiece(move) and self.board.getPiece(move).side == RED_TURN:
                    capture_moves.append((piece, move))
        if capture_moves:
            piece, move = random.choice(capture_moves)
        else:
            valid_moves = []
            for piece in pieces:
                moves = piece.checkPossibleMove(self.board.grid)
                for move in moves:
                    valid_moves.append((piece, move))
            if not valid_moves:
                return False
            piece, move = random.choice(valid_moves)

        capturedPiece = self.board.getPiece(move)
        self.tempBoard = deepcopy(self.board)
        self.board.movePiece(piece.position, move)
        if capturedPiece:
            self.checkGameOverByCapture(capturedPiece)
        self.switchTurn()
        self.checkForMated()
        if self.calculateNextMoves() == 0:
            self.gameover = True
        return True

    def checkGameOverByCapture(self, capturedPiece):
        if capturedPiece.__class__.__name__ == "Lord":
            self.gameover = True
            self.showEndGameMessage(capturedPiece.side)

    def showEndGameMessage(self, loser_side):
        winner = "RED" if loser_side == BLUE_TURN else "BLUE"
        font = pygame.font.SysFont("arial", 48)
        text = font.render(f"{winner} won!", True, (255, 255, 255))
        overlay = pygame.Surface((self.win.get_width(), self.win.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.win.blit(overlay, (0, 0))
        self.win.blit(
            text,
            ((self.win.get_width() - text.get_width()) // 2, self.win.get_height() // 2),
        )
        pygame.display.update()
        pygame.time.wait(3000)
