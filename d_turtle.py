
"""
A version of turle graphics using jp_doodle
"""

from jp_doodle import dual_canvas
from IPython.display import display
import math
import time

# The "usual" screen -- this gets initialized when needed
USUAL_SCREEN = None

WIDTH = HEIGHT = 400
debugging = True

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

def rotate_translate(x, y, radians, xt, yt):
    s = math.sin(radians)
    c = math.cos(radians)
    xr = x * c - y * s
    yr = x * s + y * c
    return [xr + xt, yr + yt]


class Shape:

    def __init__(self, kind, data):
        self.kind = kind
        self.data = data

    def install(self, in_turtle):
        kind = self.kind
        if kind == "polygon":
            in_turtle.icon_points = [[x, y] for [y, x] in self.data]
            in_turtle.forward(0)
        else:
            raise ValueError("unknown kind " + repr(kind))


class Turtle:

    # initial default configurations
    color = "black"
    lineWidth = 1
    direction_radians = 0
    direction_units = "degrees"
    position = (0, 0)
    speed = "normal"

    # stolen from turtle.py
    _shapes = {
        "arrow" : Shape("polygon", ((-10,0), (10,0), (0,10))),
        "turtle" : Shape("polygon", ((0,16), (-2,14), (-1,10), (-4,7),
                    (-7,9), (-9,8), (-6,5), (-7,1), (-5,-3), (-8,-6),
                    (-6,-8), (-4,-5), (0,-7), (4,-5), (6,-8), (8,-6),
                    (5,-3), (7,1), (6,5), (9,8), (7,9), (4,7), (1,10),
                    (2,14))),
        "circle" : Shape("polygon", ((10,0), (9.51,3.09), (8.09,5.88),
                    (5.88,8.09), (3.09,9.51), (0,10), (-3.09,9.51),
                    (-5.88,8.09), (-8.09,5.88), (-9.51,3.09), (-10,0),
                    (-9.51,-3.09), (-8.09,-5.88), (-5.88,-8.09),
                    (-3.09,-9.51), (-0.00,-10.00), (3.09,-9.51),
                    (5.88,-8.09), (8.09,-5.88), (9.51,-3.09))),
        "square" : Shape("polygon", ((10,-10), (10,10), (-10,10),
                    (-10,-10))),
        "triangle" : Shape("polygon", ((10,-5.77), (0,11.55),
                    (-10,-5.77))),
        "classic": Shape("polygon", ((0,0),(-5,-9),(0,-7),(5,-9))),
        #"blank" : Shape("image", self._blankimage())
    }

    def __init__(self):
        screen = self.screen = get_usual_screen()
        frame = self.frame = screen.frame_region(
            minx=10, miny=10, maxx=WIDTH-10, maxy=HEIGHT-10,
            frame_minx=-WIDTH/2, frame_miny=-HEIGHT/2, frame_maxx=WIDTH/2, frame_maxy=HEIGHT/2,
        )
        self.icon_points = [(-10,-10), (-10, 10), (17, 0)]
        self.icon = frame.polygon(points=self.icon_points, color=self.color, name=True)
        self.next_execution_time = time.time()
        #print("initially executing at", self.next_execution_time)

    def shape(self, name):
        choice = self._shapes[name]
        choice.install(self)

    def forward(self, distance):
        angle = self.direction_radians
        (x1, y1) = self.position
        x2 = x1 + math.cos(angle) * distance
        y2 = y1 + math.sin(angle) * distance
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in self.icon_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.screen.fit()
            line = self.frame.line(
                x1=x1, y1=y1,   # One end point of the line
                x2=x1, y2=y1,  # The other end point of the line
                color=self.color,   # Optional color (default: "black")
                lineWidth=self.lineWidth,    # Optional line width
                name=True,
            )
            line.transition(x2=x2, y2=y2, seconds_duration=delay)
            self.icon.transition(points=points, cx=x2, cy=y2, seconds_duration=delay)
        self.defer_later_executions(delay)
        self.position = (x2, y2)
        self.execute_when_ready(action)
        
    def backward(self, distance):
        self.forward(-distance)

    def left(self, degrees):
        radians = degrees * math.pi / 180.0
        (x2, y2) = self.position
        angle = self.direction_radians = self.direction_radians + radians
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in self.icon_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.screen.fit()
            self.icon.transition(points=points, seconds_duration=delay)
        self.defer_later_executions(delay)
        self.execute_when_ready(action)
    
    def right(self, degrees):
        self.left(-degrees)

    def defer_later_executions(self, seconds):
        old = self.next_execution_time
        self.next_execution_time = old + seconds
        #print ("advanced execution from", old, "to", self.next_execution_time)

    def execute_when_ready(self, action):
        if not self.speed:
            # execute immediately
            return action()
        now = time.time()
        ms_interval = (self.next_execution_time - now) * 1000
        self.execute_from_javascript(action, ms_interval)

    def execute_from_javascript(self, action, interval=1):
        def act_then_reset():
            action()
            now = time.time()
            #print ("   resetting execution time to", now)
            if now > self.next_execution_time:
                self.next_execution_time = now
        interval = max(interval, 1)
        self.screen.setTimeout(act_then_reset, interval)

    def delay_seconds(self, distance=0):
        "Eventually this should return different values based on different speeds and distances"
        if self.speed:
            return 1.0
        else:
            return 0

