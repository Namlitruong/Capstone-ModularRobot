import json
import random
import time
from datetime import datetime

import CANbus

from flask import Flask, Response, render_template

application = Flask(__name__)



@application.route('/')
def index():
    return render_template('index.html')


@application.route('/chart-data')
def chart_data():
    def generate_random_data():
        count = 4
        while True:
            msg = CANbus.receive()
            if (count == 4):
                if (int(msg.data[0]) == 0):
                    print('angle')
                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': int(msg.data[1])/0.925})
                    yield f"data:{json_data}\n\n"
                
                elif (int(msg.data[0]) == 1):
                    print('speed')
                    json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': int(msg.data[1])})
                    yield f"data:{json_data}\n\n"
                count = 0
            count = count + 1
            

    return Response(generate_random_data(), mimetype='text/event-stream')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port = 6969, threaded = True)
