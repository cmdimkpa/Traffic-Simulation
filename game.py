from flask import Flask,request,render_template
from flask_cors import CORS
import datetime

def now(): return datetime.datetime.today()

global last_request

last_request = now()

app = Flask(__name__)
CORS(app)

@app.route("/assets/<path:asset>")
def serve_asset(asset):
    return app.send_static_file(asset)

def car_data(ns,ss):
    data = []
    for j in xrange(4):
        n_cars = ns[j]
        s = ss[j]
        for i in xrange(n_cars):
            if j == 0:
                data.append("{x:canvas.width*(0.0074+2*%s*0.0159),y:0.62157*canvas.height,speed:{x:%s, y:0},h:0.01828*canvas.width,w:0.0159*canvas.height,stroke:'black',fill:'yellow',lane:1,braking:0.38788*canvas.width,collision:false}" % (i,s))
            if j == 1:
                data.append("{x:canvas.width*(0.9968-2*%s*0.0159),y:0.36928*canvas.height,speed:{x:-1*%s, y:0},h:0.01828*canvas.width,w:0.0159*canvas.height,stroke:'black',fill:'yellow',lane:2,braking:0.608926*canvas.width,collision:false}" % (i,s))
            if j == 2:
                data.append("{y:canvas.width*(0.007312+2*%s*0.0159),x:0.434*canvas.width,speed:{x:0, y:%s},w:0.01828*canvas.width,h:0.0159*canvas.height,stroke:'black',fill:'yellow',lane:3,braking:0.28233*canvas.height,collision:false}" % (i,s))
            if j == 3:
                data.append("{y:canvas.width*(0.9968-2*%s*0.0159),x:0.551*canvas.width,speed:{x:0, y:-1*%s},w:0.01828*canvas.width,h:0.0159*canvas.height,stroke:'black',fill:'yellow',lane:4,braking:0.704918*canvas.height,collision:false}" % (i,s))
    return ",".join(data)

@app.route("/traffic/simulate")
def simulator():
    global last_request
    SIM_LASTED = (now() - last_request).seconds*600; last_request = now()
    REFRESH_URL = request.url
    params = dict(request.args)
    params = {key.lower():params[key][-1] for key in params}
    if "sim_rounds" in params:
        try:
            SIM_ROUNDS = int(float(params["sim_rounds"]))
        except:
            SIM_ROUNDS = 700
    else:
        SIM_ROUNDS = 700
    if "tl_interval" in params:
        try:
            TL_INTERVAL = int(float(params["tl_interval"]))
        except:
            TL_INTERVAL = 100
    else:
        TL_INTERVAL = 100
    if "mode" in params:
        TRAFFIC_MODE = params["mode"]
    else:
        TRAFFIC_MODE = "Normal"
    if "congestion" in params:
        try:
            cs = eval(params["congestion"]); n_cars = []
            j = -1
            for c in cs:
                j+=1
                if c > 1 or c < 0:
                    c = 0.5
                if j < 2:
                    n_cars.append(int(c*12))
                else:
                    n_cars.append(int(c*6))
            if len(n_cars) > 4:
                n_cars = n_cars[:4]
            if len(n_cars) < 4:
                diff = 4 - len(n_cars)
                for i in xrange(diff):
                    n_cars.append(4)
        except:
            n_cars = [5,5,5,5]
    else:
        n_cars = [5,5,5,5]
    if "speed" in params:
        try:
            ss = eval(params["speed"]); s_cars = []
            for s in ss:
                if s > 1 or s < 0:
                    s = 0.5
                s_cars.append(int(s*15))
            if len(s_cars) > 4:
                s_cars = s_cars[:4]
            if len(s_cars) < 4:
                diff = 4 - len(s_cars)
                for i in xrange(diff):
                    s_cars.append(7)
        except:
            s_cars = [7,7,7,7]
    else:
        s_cars = [7,7,7,7]

    DYNAMIC_CODE = """

        var TRAFFIC_MODE = '__MODE__';
        var objects = [

          __CAR_DATA__,
          {x:0.4*canvas.width, y:0.68*canvas.height, speed:{x:0, y:0}, w:0.009574*canvas.width, h:0.02*canvas.height, stroke:"white", fill:"green",lane:1},
          {x:0.59*canvas.width, y:0.30*canvas.height, speed:{x:0, y:0}, w:0.009574*canvas.width, h:0.02*canvas.height, stroke:"white", fill:"green",lane:2},
          {x:0.4*canvas.width, y:0.30*canvas.height, speed:{x:0, y:0}, w:0.009574*canvas.width, h:0.02*canvas.height, stroke:"white", fill:"red",lane:3},
          {x:0.59*canvas.width, y:0.68*canvas.height, speed:{x:0, y:0}, w:0.009574*canvas.width, h:0.02*canvas.height, stroke:"white", fill:"red",lane:4}
        ]
    """
    DYNAMIC_CODE = DYNAMIC_CODE.replace("__CAR_DATA__",car_data(n_cars,s_cars))
    DYNAMIC_CODE = DYNAMIC_CODE.replace("__MODE__",TRAFFIC_MODE)
    return render_template("game.html",DYNAMIC_CODE=DYNAMIC_CODE,REFRESH_URL=REFRESH_URL,TRAFFIC_MODE=TRAFFIC_MODE,SIM_LASTED=SIM_LASTED,SIM_ROUNDS=SIM_ROUNDS,TL_INTERVAL=TL_INTERVAL)

if __name__ == "__main__":
  app.run(port=3434,threaded=True)
