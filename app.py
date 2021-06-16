from flask import Flask, render_template, request, jsonify
import numpy as np
import sys
# from flask_bootstrap import Bootstrap

from model.classifier import models, smoother, RepetitionCounter

app = Flask(__name__)
# Bootstrap(app)
pose_class = 'shoulderpress'
repetition_counter = RepetitionCounter(
    class_name=pose_class + '_up',
    enter_threshold=6,
    exit_threshold=4)


@app.route('/')
def hello_world():
    return render_template('test.html')


@app.route('/demo')
def demo():
    return render_template('demo/demo.html')


def updateRepetitionCounterIfNeeded(pose):
    global pose_class, repetition_counter
    if pose_class != pose:
        pose_class = pose
        repetition_counter = RepetitionCounter(
            class_name=pose_class + '_up',
            enter_threshold=6,
            exit_threshold=4)


def setPose(pose):
    if pose:
        updateRepetitionCounterIfNeeded(pose)
        return pose
    else:
        return 'full_model'


def getRepCount(classification):
    global repetition_counter
    if classification is not None:
        return repetition_counter(classification)
    return repetition_counter.n_repeats


@app.route('/getpose', methods=['POST'])
def getpose():
    global repetition_counter
    # print(request)
    pose_classification = None
    pose = setPose(request.args.get('pose'))

    if request.method == 'POST':
        json = request.json
        pose_landmarks = np.array(
            [[lmk['x'] * json['width'], lmk['y'] * json['height'], lmk['z'] * json['width']]
             for lmk in json['pose_landmarks']],
            dtype=np.float32)
        pose_classification = models[pose](pose_landmarks)

    response = jsonify({'pose': pose_classification, 'rep': getRepCount(pose_classification)})
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(debug=True)

# colors:
# #10d4dc
# #fbbc5c
# #d5f3ed
# #fccc7d
