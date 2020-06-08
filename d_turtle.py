
"""
A version of turle graphics using jp_doodle
"""

from jp_doodle import dual_canvas
from IPython.display import display
import math

# The "usual" screen -- this gets initialized when needed
USUAL_SCREEN = None

WIDTH = HEIGHT = 400
debugging = False

def get_usual_screen(width=WIDTH, height=HEIGHT):
    global USUAL_SCREEN
    if USUAL_SCREEN is not None:
        return USUAL_SCREEN
    screen = dual_canvas.DualCanvasWidget(width=width, height=height)
    if not debugging:
        display(screen)
        screen.in_dialog()
        screen.element.dialog(dict(width=width+100, height=height+100))
    else:
         display(screen.debugging_display())
    screen.rect(0, 0, 400, 400, "#eea")
    screen.fit()
    USUAL_SCREEN = screen
    return screen


class Turtle:

    # initial default configurations
    color = "black"
    lineWidth = 1
    direction_radians = 0
    direction_units = "degrees"
    position = (0, 0)

    def __init__(self):
        screen = self.screen = get_usual_screen()
        frame = self.frame = screen.frame_region(
            minx=10, miny=10, maxx=WIDTH-10, maxy=HEIGHT-10,
            frame_minx=-WIDTH/2, frame_miny=-HEIGHT/2, frame_maxx=WIDTH/2, frame_maxy=HEIGHT/2,
        )
        self.icon_points = [(-10,-10), (-10, 10), (17, 0)]
        self.icon = frame.polygon(points=self.icon_points, color=self.color, name=True)

    def forward(self, distance):
        angle = self.direction_radians
        (x1, y1) = self.position
        x2 = x1 + math.cos(angle) * distance
        y2 = y1 + math.sin(angle) * distance
        self.frame.line(
            x1=x1, y1=y1,   # One end point of the line
            x2=x2, y2=y2,  # The other end point of the line
            color=self.color,   # Optional color (default: "black")
            lineWidth=self.lineWidth,    # Optional line width
        )
        points = [[x + x2, y + y2] for (x,y) in self.icon_points]
        self.icon.change(points=points, cx=x2, cy=y2)
        self.position = (x2, y2)
    

