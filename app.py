from flask import Flask, render_template, request
import json
import numpy as np
import sys
from flask_bootstrap import Bootstrap

from model.classifier import model, smoother

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def hello_world():
    return render_template('test.html')

@app.route('/demo')
def demo():
    return render_template('demo/demo.html')


@app.route('/getpose', methods=['POST'])
def getpose():
    pose_classification = ''
    if request.method == 'POST':
        json = request.json
        pose_landmarks = np.array(
            [[lmk['x'] * json['width'], lmk['y'] * json['height'], lmk['z'] * json['width']]
             for lmk in json['pose_landmarks']],
            dtype=np.float32)
        pose_classification = model(pose_landmarks)
    # print(pose_classification, file=sys.stderr)
    return pose_classification


if __name__ == '__main__':
    app.run()
