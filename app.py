from flask import Flask, render_template, request
import json
import numpy as np
import sys
# from flask_bootstrap import Bootstrap

from model.classifier import models, smoother, RepetitionCounter

app = Flask(__name__)
# Bootstrap(app)
pose_class = 'shoulderpress'
repetition_counter = RepetitionCounter(
    class_name=pose_class,
    enter_threshold=6,
    exit_threshold=4)

@app.route('/')
def hello_world():
    return render_template('test.html')

@app.route('/demo')
def demo():
    return render_template('demo/demo.html')


@app.route('/getpose', methods=['POST'])
def getpose():
    global repetition_counter, pose_class
    print(request)
    pose_classification = ''
    if request.args.get('pose'):
        pose = request.args.get('pose')
        if pose_class != pose:
            pose_class = pose
            repetition_counter = RepetitionCounter(
                class_name=pose_class,
                enter_threshold=6,
                exit_threshold=4
            )
    else:
        pose = 'full_model'
    if request.method == 'POST':
        json = request.json
        pose_landmarks = np.array(
            [[lmk['x'] * json['width'], lmk['y'] * json['height'], lmk['z'] * json['width']]
             for lmk in json['pose_landmarks']],
            dtype=np.float32)
        pose_classification = models[pose](pose_landmarks)
    # print(pose_classification, file=sys.stderr)
    return pose_classification


if __name__ == '__main__':
    app.run(debug=True)
