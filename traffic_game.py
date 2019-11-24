from __future__ import division
import sys,datetime,time,pygal,os
from random import random
from hashlib import md5

def try_float(x):
    try:
        return float(x)
    except:
        return x

def now():
    return datetime.datetime.today()

def new_id():hasher = md5(); hasher.update(str(now())); return hasher.hexdigest()

SIM_TIME, SIM_NODES, SIM_TITLE = map(try_float,sys.argv[1:])

global ROUTES, VALVES, CARS, HERE

ROUTES = []; VALVES = []; CARS = []

HERE = os.getcwd()
if "\\" in HERE:
    HERE+="\\"
else:
    HERE+="/"

def divider(t,nodes):
    div = t/nodes; return [node*div for node in xrange(int(nodes))]

def compute_nodes(route):
    # a route is a quartic curve
    return [{"x":t,"y":route.a*(t**4)+route.b*(t**3)+route.c*(t**2)+route.d*t+route.e} for t in divider(SIM_TIME,SIM_NODES)]

def from_collection(collection,id):return [x for x in collection if x.id == id][0]

def UPDATE_ROUTES(id,curr_obj):
    global ROUTES
    ROUTES[[ROUTES.index(route) for route in ROUTES if route.id == id][0]] = curr_obj
    return None

def UPDATE_VALVES(id,curr_obj):
    global VALVES
    VALVES[[VALVES.index(valve) for valve in VALVES if valve.id == id][0]] = curr_obj
    return None

def UPDATE_CARS(id,curr_obj):
    global CARS
    CARS[[CARS.index(car) for car in CARS if car.id == id][0]] = curr_obj
    return None

def toggle_valve(id):
    valve = from_collection(VALVES,id)
    valve.open = not valve.open
    UPDATE_VALVES(id,valve)

def NewRouteChart(route_index,gen):
    xy_chart = pygal.XY()
    xy_chart.title = SIM_TITLE
    route = ROUTES[route_index]; car_positions = []
    for car_id in route.cars:
        car = from_collection(CARS,car_id)
        node = route.nodes[car.node]
        car_positions.append((node["x"],node["y"]))
    xy_chart.add('Route', car_positions)
    xy_chart.render_to_file(HERE+"%s.svg"%gen)

class Route:
    def __init__(self,a,b,c,d,e):
        global ROUTES
        self.a = a; self.b = b; self.c = c; self.d = d; self.e = e
        self.id = new_id()
        self.nodes = compute_nodes(self)
        self.valves = []
        self.valve_nodes = []
        self.cars = []
        ROUTES.append(self)

# Add Routes to the Environment
Route(0.008,0.002,0.029,-0.05,-0.012) # Route 1
Route(0.028,0.002,-0.029,-0.05,0.012) # Route 2
Route(0.108,-0.052,-0.129,-0.035,-0.012) # Route 3

def random_selection(array):return array[int(random()*len(array))]

def select_route():return random_selection(ROUTES)

class Valve:
    def __init__(self,node):
        global VALVES
        self.node = node
        self.id = new_id()
        success = False
        # bind valve to route
        while not success:
            self.route = select_route()
            if self.id not in self.route.valves and self.node not in self.route.valve_nodes:
                self.route.valves.append(self.id)
                self.route.valve_nodes.append(self.node)
                success = True
            time.sleep(0.1)
        UPDATE_ROUTES(self.route.id,self.route)
        # valve open by default
        self.open = True
        VALVES.append(self)

# Add Valves to the Environment
for valve in xrange(10):
    Valve(random_selection(xrange(int(SIM_NODES))))

class Car:
    def __init__(self):
        global CARS
        time.sleep(0.1)
        self.id = new_id()
        # bind car to route
        self.route = select_route()
        self.route.cars.append(self.id); UPDATE_ROUTES(self.route.id,self.route)
        # enter route at node 0
        self.node = 0
        CARS.append(self)
    def move(self):
        # CAR MOVEMENT FRAMEWORK
        # Search for cars at your intended next position on your route
        if [car for car in CARS if car.route.id == self.route.id and self.node+1 == car.node]:
            # do not advance
            pass
        else:
            # check if my next position is a traffic stop
            if self.node+1 in self.route.valve_nodes:
                # check if valve open
                valve_index = self.route.valve_nodes.index(self.node+1)
                valve_id = self.route.valves[valve_index]
                valve = from_collection(VALVES,valve_id)
                if valve.open:
                    # skip over traffic node
                    self.node+=2
                else:
                    # stop at traffic light
                    pass
            else:
                # move to next node
                self.node+=1

# Add cars to the Environment
for car in xrange(100):
    Car()

def MoveCar(car):
    car.move(); UPDATE_CARS(car.id,car)

# Simulation Framework
for time_step in xrange(int(SIM_NODES)):
    # toggle valves every 20 time_steps
    if time_step>0 and time_step%20 == 0:
        process = map(toggle_valve,[valve.id for valve in VALVES])
    # for every time step, attempt to move cars
    process = map(MoveCar,CARS)
    # plot route chart
    NewRouteChart(0,time_step)
