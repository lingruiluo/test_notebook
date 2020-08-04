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
    # use a counter to distinguish turtles
    screen.turtle_count = 0
    # store info about turtles in the javascript element container
    screen.js_init("""
        element.turtle_info = { };

        element.get_turtle_info = function(id) {
            return element.turtle_info[id];
        };
    """);
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
        return "FakeScreen"

    def __getattr__(self, attr):
        print("FakeScreen getattr")
        def dummy_function(*arguments):
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
    
    primary_js = """
        // Store information about this turtle separately from other turtles.
        debugger;
        var info = { };
        info._lines = [];
        info._dots = [];
        info._stamps = [];
        info.frame = element.frame_region(
            10, 10, WIDTH-10, HEIGHT-10,
            -WIDTH/2, -HEIGHT/2, WIDTH/2, HEIGHT/2,
        );
        info.icon = info.frame.polygon({
            points:icon_points, color:color, name:true
            });
        info.frame_rect = info.frame.rect({
            x:-WIDTH/2-10, 
            y:-HEIGHT/2-10, 
            w:WIDTH, 
            h:HEIGHT, 
            color:"rgb(0,0,0,0)", 
            name:true,
        });
        info.delayed_execution = function(action, delay) {
            if (delay > 0) {
                setTimeout(action, delay);
            } else {
                action();
            }
        }
        element.turtle_info[turtle_id] = info;
    """

    def __init__(self):
        screen = self.screen = get_usual_screen()
        screen.turtle_count += 1
        self.turtle_id = screen.turtle_count
        self.icon_points = [(-10,-10), (-10, 10), (17, 0)]
        self.all_js = (
            self.primary_js
            + self.icon_visible_js
            + self.icon_color_change_js
            + self.left_js
            + self.forward_js
            + self.clear_js
            + self.dot_js
            + self.icon_size_js
            + self.stamp_js
        )
        screen.js_init(
            self.all_js,
            turtle_id=self.turtle_id,
            WIDTH=WIDTH,
            HEIGHT=HEIGHT,
            color=self._color,
            icon_points=self.icon_points,
        )
        self.js_info = screen.element.get_turtle_info(self.turtle_id)
        
        self.js_info.frame_rect.on("click",self.click_event)
        
        self.stampsItem = dict()
        self.stampsId = []
        self.icon_current_points = self.icon_points
        self.next_execution_time = time.time()
        #print("initially executing at", self.next_execution_time)
        
    def draw_limit_exceeded(self):
        self.draw_count += 1
        if self.draw_count == self.draw_limit:
            print ("\n   DRAW LIMIT REACHED\n")
            raise ValueError("Draw limit")
        return (self.draw_limit is not None) and (self.draw_count > self.draw_limit)

    flushes = None

    def getscreen(self):
        "stubbed functionality for compatibility with standard Turtle module"
        # delay to allow javascript to catch up
        self.flushes = self.flushes or []
        self.flushes.append(self.draw_count)
        from jp_doodle.auto_capture import javascript_eval
        print ("FLUSH AND SYNC", self.draw_count)
        self.screen.flush()
        self.screen.element.redraw()
        self.screen.auto_flush = True
        two = javascript_eval(self.screen, "1+1")
        assert two == 2
        self.screen.auto_flush = False
        return FakeScreen()
 
    def click_event(self, event):
        location = event["model_location"]
        def action(*ignored):
            self.goto(location['x'], location['y'])
        self.execute_when_ready(action)
    
    def up(self):
        # def action(*ignored):
        #     self._drawing = False
        # self.execute_when_ready(action)
        self._drawing = False

    def down(self):
        # def action(*ignored):
        #     self._drawing = True
        # self.execute_when_ready(action)
        self._drawing = True

    def heading(self):
        return self.direction_radians * 180 / math.pi

    def setheading(self, degrees):
        """
        0 - east
        90 - north
        180 - west
        270 - south
        """
        degrees_change = degrees - (self.direction_radians * 180 / math.pi)
        return self.left(degrees_change)

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
        self.icon_current_points = points
        self.position_icon = (x2, y2)
        self.defer_later_executions(delay)
        return self.js_info.forward(points, x1, y1, x2, y2, self._color, self.lineWidth, self._drawing,delay, self.action_delay())
        
    def distance(self, x, y=None):
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
        return round(math.sqrt((x2 - x1)**2 + (y2 - y1)**2),2)

    def shape(self, name):
#         print ("shape")
        choice = self._shapes[name]
        choice.install(self)
        
    forward_js = """
        info.forward = function(points, x1, y1, x2, y2, color, lineWidth, drawing, delay, interval) {
            var action = function() {
                element.fit();
                info.icon.transition({ points:points, cx:x2, cy:y2 }, delay);
                if (drawing) {
                    var line = info.frame.line({
                        x1:x1, y1:y1,   // One end point of the line
                        x2:x1, y2:y1,  // The other end point of the line
                        color:color,   // Optional color (default: "black")
                        lineWidth:lineWidth,    // Optional line width
                        name:true,
                    });
                    line.transition({x2:x2, y2:y2}, delay)
                    info._lines.push(line)
                }
            };
            info.delayed_execution(action, interval);
        };
    """

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
        self.icon_current_points = points
        self.position_icon = (x2, y2)
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.forward(points, x1, y1, x2, y2, self._color, self.lineWidth, self._drawing, delay, interval)
        
    def backward(self, distance):
        self.forward(-distance)

    left_js = """
        info.left = function(points, delay, interval) {
            var action = function() {
                info.icon.transition({ points:points }, delay);
            };
            info.delayed_execution(action, interval);
        };
    """
    
    def left(self, degrees):
        if self.draw_limit_exceeded():
            return # silently do nothing
        radians = degrees * math.pi / 180.0
        (x2, y2) = self.position_icon
        angle = self.direction_radians = self.direction_radians + radians
        size_points = [icon_size(x,y,self.lineWidth) for (x,y) in self.icon_points]
        points = [rotate_translate(x,y,angle,x2,y2) for (x,y) in size_points]
        delay = self.delay_seconds()
        self.icon_current_points = points
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.left(points, delay, interval)
    
    def right(self, degrees):
        self.left(-degrees)
    
    stamp_js = """
        info.stamp = function(points, color, delay, id, interval) {
            var action = function() {
                var stamp = info.frame.polygon({
                    points:points,
                    color:color,
                    name:true,
                });
                info._stamps.push(stamp);
            };
            info.delayed_execution(action, interval);
        };
        info.clear_stamp = function(id, delay, interval) {
            var action = function() {
                info._stamps[id-1].forget();
                info._stamps.remove(id-1);
            };
            info.delayed_execution(action, interval);
        };
        info.clear_stamps = function(delay, interval){
            var action = function(){
                for (i = 0; i < info._stamps.length; i++) {
                      info._stamps[i].forget();
                 };
                info._stamps = [];
            };
            info.delayed_execution(action, interval);
        };
    """
    
    def stamp(self):
        if self.draw_limit_exceeded():
            return # silently do nothing
        self.stamp_id += 1
        self.stampsId.append(self.stamp_id)
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.stamp(self.icon_current_points, self._color, delay, self.stamp_id, interval)
    
    def clearstamp(self, stampid = None):
        if self.draw_limit_exceeded():
            return # silently do nothing
        if stampid is None:
            stampid = self.stamp_id
        delay = self.delay_seconds()
        self.stampsId.remove(stampid)
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.clear_stamp(stampid, delay, interval)

    def clearstamps(self, n = None):
        delay = self.delay_seconds()
        if n is None:
            self.stampsId = []
            self.defer_later_executions(delay)
            interval = self.action_delay()
            return self.js_info.clear_stamps(delay, interval)
        elif abs(n) > len(self.stampsId):
            print("There are only ",len(self.stampsId), " stamps")
            return "There are only "+str(len(self.stampsId))+" stamps"
        elif n >= 0:
            names = self.stampsId[:n]
        else:
            names = self.stampsId[n:]
            print("removed stamps ", names)
        for i in names:
            self.clearstamp(stampid=i)
    
    clear_js = """
        info.clear = function(interval) {
            var action = function() {
                 for (i = 0; i < info._lines.length; i++) {
                      info._lines[i].forget();
                 };
                 info._lines = [];
                 for (i = 0; i < info._dots.length; i++) {
                      info._dots[i].forget();
                 };
                 info._dots = [];
            };
            info.delayed_execution(action, interval);
        }
    """
    
    def clear(self):
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.clear(interval)
    
    dot_js = """
        info.dot = function(x, y, r, color, delay) {
            var action = function() {
                element.fit();
                var circle = info.frame.circle({
                    x:x, y:y, r:r,
                    color:color, fill:true, name: true
                });
                info._dots.push(circle);
            };
            info.delayed_execution(action, delay);
        };
        info.clear_dot = function(interval) {
            var action = function() {
                for (i = 0; i < info._dots.length; i++) {
                      info._dots[i].forget();
                 };
                 info._dots = [];
            };
            info.delayed_execution(action, interval);
        };
    """
    
    def dot(self,size=None,*color):
        if self.draw_limit_exceeded():
            return
        (x1, y1) = self.position_icon
        if size is None:
            size = 5
        if not color:
            color = self._color
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        return self.js_info.dot(x1,y1,size,color, self.action_delay())
    
    def clear_dot(self):
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        interval = self.action_delay()
        return self.js_info.clear_dot(interval)
    
    icon_color_change_js = """
        info.icon_color_change = function(value, delay) {
            var action = function() {
                info.icon.change({ color: value });
            };
            info.delayed_execution(action, delay);
        };
    """
    
    def color(self, color_name):
        self._color = color_name
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        return self.js_info.icon_color_change(color_name, self.action_delay())
        
    def speed(self, val):
        speeds = {'fastest':0.1, 'fast':0.5, 'normal':1.0, 'slow':1.5, 'slowest':2.0 }
        self.speed_move = val
        if isinstance(val, str):
            if val in speeds:
                self.speed_move = speeds[val]
            else:
                print("Please enter the correct speed value")
                raise ValueError
    
    def position(self):
        return self.position_icon
    
    icon_visible_js = """
        info.icon_visible = function(value, delay) {
            var action = function() {
                info.icon.visible(value);
            }
            info.delayed_execution(action, delay);
        };
    """
    
    def hideturtle(self):
        return self.js_info.icon_visible(False, self.action_delay())
    
    def showturtle(self):
        return self.js_info.icon_visible(True, self.action_delay())
    
    icon_size_js = """
        info.icon_pensize = function(points, delay, interval) {
            var action=function(){
                element.fit();
                info.icon.transition({ points:points }, delay);
            }
            info.delayed_execution(action, interval);
        };
    """
    
    def pensize(self, size):
        size_points = [icon_size(x,y,size) for (x,y) in self.icon_points]
        (x2, y2) = self.position_icon
        angle = self.direction_radians
        points = [rotate_translate(x,y,angle,x2,y2) for [x,y] in size_points]
        self.icon_current_points = points
        self.lineWidth = size
        delay = self.delay_seconds()
        self.defer_later_executions(delay)
        return self.js_info.icon_pensize(points, delay, self.action_delay())

    def current_delay(self):
        return max(0, self.next_execution_time - time.time())
    
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

    def action_delay(self):
        now = time.time()
        ms_interval = (self.next_execution_time - now) * 1000
        interval = max(ms_interval, 1)
        if now > self.next_execution_time:
            self.next_execution_time = now
        return interval

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