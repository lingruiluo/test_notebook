
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

def icon_size(x, y, size):
    return [x*(1+(size-1)/10), y*(1+(size-1)/10)]

def reset():
    global USUAL_SCREEN
    USUAL_SCREEN = None

class FakeScreen:

    def __repr__(self):
        print("FakeScreen init")
        return "FakeScreen"

    def __getattr__(self, attr):
        print("FakeScreen getattr")
        def dummy_function(*arguments):
            print("FakeScreen getattr call")
            return "not a real method, just a fake: " + repr(attr)
        return dummy_function


class Shape:

    def __init__(self, kind, data):
        self.kind = kind
        self.data = data

    def install(self, in_turtle):
        kind = self.kind
        if kind == "polygon":
            in_turtle.icon_points = [[x, y] for [y, x] in self.data]
            in_turtle.icon_points = [[x*in_turtle.lineWidth, y*in_turtle.lineWidth] for [x,y] in in_turtle.icon_points]
            in_turtle.forward(0)
            in_turtle.stamp_id -= 1
        else:
            raise ValueError("unknown kind " + repr(kind))


class Turtle:

    # initial default configurations
    _color = "black"
    lineWidth = 1
    direction_radians = 0
    direction_units = "degrees"
    position_icon = (0, 0)
    speed_move = "normal"
    stamp_id = 0
    draw_limit = None
    draw_count = 0
    _drawing = True

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
        self.frame_rect = frame.rect(x=-WIDTH/2-10, y=-HEIGHT/2-10, w=WIDTH, h=HEIGHT, color="rgb(0,0,0,0)", name=True)
        
        self.frame_rect.on("click",self.click_event)
        self.icon_points = [(-10,-10), (-10, 10), (17, 0)]
        self.icon = frame.polygon(points=self.icon_points, color=self._color, name=True)
        self.stampsItem = dict()
        self.stampsId = []
        self.icon_current_points = self.icon_points
        self.next_execution_time = time.time()
        #print("initially executing at", self.next_execution_time)

    def click_event(self, event):
        location = event["model_location"]
        def action(*ignored):
            self.goto(location['x'], location['y'])
        self.execute_when_ready(action)
        
    def draw_limit_exceeded(self):
        self.draw_count += 1
        if self.draw_count == self.draw_limit:
            print ("\n   DRAW LIMIT REACHED\n")
        return (self.draw_limit is not None) and (self.draw_count > self.draw_limit)

    def getscreen(self):
        "stubbed functionality for compatibility with standard Turtle module"
        # delay to allow javascript to catch up
        import time
        time.sleep(0.1)
        #self.screen.flush()
        return FakeScreen()

    def up(self):
        def action(*ignored):
            self._drawing = False
        self.execute_when_ready(action)

    def down(self):
        def action(*ignored):
            self._drawing = True
        self.execute_when_ready(action)

    def heading(self):
        return self.direction_radians * 180 / math.pi

    def setheading(self, degrees):
        """
        0 - east
        90 - north
        180 - west
        270 - south
        """
        angle = self.direction_radians = degrees * math.pi / 180
        (x2, y2) = self.position_icon
        
        size_points = [icon_size(x,y,self.lineWidth) for (x,y) in self.icon_points] 
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in size_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.icon.transition(points=points, cx=x2, cy=y2, seconds_duration=delay)
            self.icon_current_points = points
        self.defer_later_executions(delay)
        self.execute_when_ready(action)

    def home(self):
        self.goto((0,0))
    
    def goto(self, x, y = None):
        if self.draw_limit_exceeded():
            return
        (x1, y1) = self.position_icon
        (x2, y2) = (x1, y1)
        if y is None:
            try:
                (x2, y2) = x
            except TypeError:
                print("argument should be a tuple of coordinate or give x and y values")
                raise
        else:
            (x2, y2) = (x, y)
        radians = math.atan2(y2-y1,x2-x1)
        angle = self.direction_radians = radians
        size_points = [icon_size(x,y,self.lineWidth) for (x,y) in self.icon_points]
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in size_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.screen.fit()
            if self._drawing:
                line = self.frame.line(
                    x1=x1, y1=y1,
                    x2=x1, y2=y1,
                    color=self._color,
                    lineWidth=self.lineWidth,
                    name=True,
                )
                line.transition(x2=x2, y2=y2, seconds_duration=delay)
            self.icon.transition(points=points, cx=x2, cy=y2, seconds_duration=delay)
            self.icon_current_points = points
            self.stamp_id += 1
        self.defer_later_executions(delay)
        self.position_icon = (x2, y2)
        self.execute_when_ready(action)

    def shape(self, name):
#         print ("shape")
        choice = self._shapes[name]
        choice.install(self)

    def forward(self, distance):
        #print ("forward", distance)
        if self.draw_limit_exceeded():
            return # silently do nothing
        angle = self.direction_radians
        (x1, y1) = self.position_icon
        x2 = x1 + math.cos(angle) * distance
        y2 = y1 + math.sin(angle) * distance
        size_points = [icon_size(x,y,self.lineWidth) for (x,y) in self.icon_points]
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in size_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.screen.fit()
            if self._drawing:
                line = self.frame.line(
                    x1=x1, y1=y1,   # One end point of the line
                    x2=x1, y2=y1,  # The other end point of the line
                    color=self._color,   # Optional color (default: "black")
                    lineWidth=self.lineWidth,    # Optional line width
                    name=True,
                )
                line.transition(x2=x2, y2=y2, seconds_duration=delay)
            self.icon.transition(points=points, cx=x2, cy=y2, seconds_duration=delay)
            self.icon_current_points = points
            self.stamp_id += 1
        self.defer_later_executions(delay)
        self.position_icon = (x2, y2)
        self.execute_when_ready(action)
        
    def backward(self, distance):
        self.forward(-distance)

    def left(self, degrees):
        if self.draw_limit_exceeded():
            return # silently do nothing
        radians = degrees * math.pi / 180.0
        (x2, y2) = self.position_icon
        angle = self.direction_radians = self.direction_radians + radians
        size_points = [icon_size(x,y,self.lineWidth) for (x,y) in self.icon_points]
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in size_points]
        delay = self.delay_seconds()
        def action(*ignored):
            self.screen.fit()
            self.icon.transition(points=points, seconds_duration=delay)
            self.icon_current_points = points
        self.defer_later_executions(delay)
        self.execute_when_ready(action)
    
    def right(self, degrees):
        self.left(-degrees)
        
    def stamp(self):
        if self.draw_limit_exceeded():
            return # silently do nothing
        def action(*ignored):
            stamp = self.frame.polygon(points=self.icon_current_points, color=self.color, name=True)
            if self.stamp_id not in self.stampsId:
                self.stampsId.append(self.stamp_id)
            self.stampsItem[self.stamp_id] = stamp
        self.execute_when_ready(action)
        return self.stamp_id
    
    def clearstamp(self, stampid = None):
        if self.draw_limit_exceeded():
            return # silently do nothing
        #print("clearstamp")
        def action(*ignored):
            try:
#                 self.stampsItem[stampid].visible(False)
                self.stampsItem[stampid].forget()
                print("removed the stamp ", stampid)
                self.stampsItem.pop(stampid)
                self.stampsId.remove(stampid)
            except KeyError:
                print("No such stamp")
                raise
        if stampid is None:
            stampid = self.stampsId[-1]
        self.execute_when_ready(action)

    def clearstamps(self, n = None):
        #print ("clearstamps")
        names = self.stampsId
        if n is None:
            print("removed all stamps")
        elif abs(n) > len(self.stamps):
            print("There are only ",len(self.stampsId), " stamps")
            return "There are only "+str(len(self.stampsId))+" stamps"
        elif n >= 0:
            names = self.stampsId[:n]
            print("removed stamps ", names)
        else:
            names = self.stampsId[n:]
            print("removed stamps ", names)
        for i in names:
            self.clearstamp(stampid=i)
    
    def dot(self,size=None,*color):
        if self.draw_limit_exceeded():
            return
        (x1, y1) = self.position_icon
        delay = self.delay_seconds()
        if size is None:
            size = 5
        if not color:
            color = self._color
        def action(*ignored):
            self.screen.fit()
            dot = self.frame.circle(
                    x=x1, y=y1,r=size,
                    color=color,   # Optional color (default: "black")
                    fill=True,
                    name=True,
                )
        self.defer_later_executions(0.5)
        self.execute_when_ready(action)
    
    def color(self, color_name):
        def action(*ignored):
            self._color = color_name
            self.icon.change(color=color_name)
        self.execute_when_ready(action)
        
    def speed(self, val):
        speeds = {'fastest':0.1, 'fast':0.5, 'normal':1.0, 'slow':1.5, 'slowest':2.0 }
        self.speed_move = val
        if isinstance(val, str):
            if val in speeds:
                self.speed_move = speeds[val]
            else:
                print("Please enter the correct speed value")
                raise ValueError
#         delay = self.delay_seconds()
#         def action(*ignored):
#             self.speed_move = val
#         self.defer_later_executions(delay)
#         self.execute_when_ready(action)
    
    def position(self):
        return self.position_icon
    
    def hideturtle(self):
        def action(*ignored):
            self.icon.visible(False)
        self.execute_when_ready(action)
    
    def showturtle(self):
        def action(*ignored):
            self.icon.visible(True)
        self.execute_when_ready(action)
    
    def pensize(self, size):
        size_points = [icon_size(x,y,size) for (x,y) in self.icon_points]
        (x2, y2) = self.position_icon
        angle = self.direction_radians
        points = [rotate_translate(x,y,angle,x2,y2) for [x,y] in size_points]
        def action(*ignored):
            self.screen.fit()
            self.icon.transition(points=points)
            self.icon_current_points = points
            self.lineWidth = size
        self.execute_when_ready(action)

    def defer_later_executions(self, seconds):
        old = self.next_execution_time
        self.next_execution_time = old + seconds
        #print ("advanced execution from", old, "to", self.next_execution_time)

    def execute_when_ready(self, action):
        if not self.speed_move:
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
        speed = self.speed_move
        if isinstance(speed,str):
            if speed == 'normal':
                speed = 1.0
            elif speed == 'slow':
                speed = 2.0
            else:
                speed = 0.2
        return speed
#         if self.speed_move:
#             return 1.0
#         else:
#             return 0

