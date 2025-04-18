import pygame
import sys

from .utils import ChessImages, Color, Font, RED_SIDE, BLUE_SIDE, WIN_HEIGHT, WIN_WIDTH


class ControlPanel:
    MARGIN_RIGHT = 50

    def __init__(self, game):
        self.width = 250
        self.height = 600

        self.x = WIN_WIDTH - self.width - self.MARGIN_RIGHT
        self.y = 50

        self.game = game
        self.buttons = []

        self.makeIndicators()
        self.makeButton(self.x, self.y + 200, "Quit")
        self.makeButton(self.x + self.width - 100, self.y + 200, "Reset")
        self.makeButton(self.x, self.y + 300, "Rules")

    def makeIndicators(self):
        """
        Make indicators to guide players on whose turn to play
        """
        self.blueLord = pygame.transform.scale(ChessImages.BLUE_LORD, (70, 70))
        self.redLord = pygame.transform.scale(ChessImages.RED_LORD, (70, 70))

        self.indicatorRadius = 35
        self.indicators = [
            (self.blueLord, (self.x + 35, self.y + 35)),
            (self.redLord, (self.x + self.width - 35, self.y + 35)),
        ]

    def makeButton(self, x, y, text):
        """
        Make sure every button is the same size
        W = 100
        H = 30
        """
        width = 100
        height = 30
        coordinate = (x, y)

        self.buttons.append((coordinate, width, height, text))

    def runCommand(self, buttonText):
        FUNCTIONS = {
            "Undo": self.game.undo,
            "Reset": self.game.resetGame
        }

        if buttonText in FUNCTIONS:
            FUNCTIONS[buttonText]()
        elif buttonText == "Rules":
            self.openRulesWindow()

    def checkForClick(self, clickPos):
        """
        Run command if any button is clicked
        """
        clickX, clickY = clickPos

        for coordinate, width, height, text in self.buttons:
            btnX, btnY = coordinate

            if clickX < btnX or clickX > btnX + width:
                continue

            if clickY < btnY or clickY > btnY + height:
                continue

            self.runCommand(text)

    def draw(self, win):
        """
        Draw the control panel
        """
        for indicator, centrePoint in self.indicators:
            pygame.draw.circle(win, Color.WHITE, centrePoint, self.indicatorRadius)
            win.blit(
                indicator,
                (
                    centrePoint[0] - self.indicatorRadius,
                    centrePoint[1] - self.indicatorRadius,
                ),
            )

        for coordinate, width, height, text in self.buttons:
            textSurface = Font.WRITING_FONT.render(text, True, Color.BLACK)
            textWidth, textHeight = textSurface.get_size()

            pygame.draw.rect(
                win,
                Color.WHITE,
                pygame.Rect(*coordinate, width, height),
            )
            textX = coordinate[0] + (width - textWidth) // 2
            textY = coordinate[1] + (height - textHeight) // 2

            win.blit(textSurface, (textX, textY))

        if self.game.isOver:
            winnerTeam = "Blue" if self.game.turn == RED_SIDE else "Red"
            text = Font.NORMAL_FONT.render(f"{winnerTeam} won", True, Color.GREEN)
            textWidth, textHeight = text.get_size()

            textX = self.x + (self.width - textWidth) // 2
            textY = 150

            win.blit(text, (textX, textY))

    def openRulesWindow(self):
        """
        Mở một cửa sổ riêng hiển thị luật chơi
        """
        pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # Đảm bảo không ảnh hưởng main screen

        RULE_WIN_WIDTH = 1000
        RULE_WIN_HEIGHT = 1000
        ruleWin = pygame.display.set_mode((RULE_WIN_WIDTH, RULE_WIN_HEIGHT))
        pygame.display.set_caption("Luật chơi cờ tướng")

        rulesText = [
            "📘  XIANGQI RULES (Chinese Chess)",
            "",
            "1. OBJECTIVE:",
            "   ➤ Each player controls one side (Red or Blue).",
            "   ➤ The goal is to checkmate the opponent's General.",
            "",
            "2. GAMEPLAY:",
            "   ➤ Players take turns to move one piece per turn.",
            "   ➤ You must not leave your General in check.",
            "   ➤ If in check, you must resolve it immediately.",
            "   ➤ The game ends when a player is checkmated or has no legal move.",
            "",
            "3. PIECE MOVEMENT:",
            "   ➤ General: Moves one step horizontally or vertically in the Palace.",
            "   ➤ Advisor: Moves one step diagonally within the Palace.",
            "   ➤ Elephant: Moves two points diagonally, cannot cross the river.",
            "   ➤ Chariot: Moves horizontally or vertically any number of spaces.",
            "   ➤ Horse: Moves in an 'L' shape: 1 straight, then 1 diagonal.",
            "   ➤ Cannon: Moves like a Chariot, but captures by jumping over one piece.",
            "   ➤ Soldier: Moves forward 1 step. After crossing the river, can move sideways.",
            "",
            "4. OTHER RULES:",
            "   ➤ Repetitive checking (3 or more times) is forbidden.",
            "   ➤ The two Generals may not face each other directly.",
            "   ➤ A draw occurs when neither side can force a checkmate.",
            "",
            "⏎  Press ESC to return to the board."
        ]


        font = pygame.font.SysFont("arial", 20)
        running = True

        clock = pygame.time.Clock()

        while running:
            ruleWin.fill((240, 240, 240))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            for i, line in enumerate(rulesText):
                textSurface = font.render(line, True, (0, 0, 0))
                ruleWin.blit(textSurface, (20, 20 + i * 28))

            pygame.display.update()
            clock.tick(30)

        # Sau khi đóng rules window, mở lại game chính
        pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Cờ Tướng")
