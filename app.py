from flask import Flask, render_template, request, jsonify
import numpy as np
import sys
# from flask_bootstrap import Bootstrap

from model.classifier import models, smoother, RepetitionCounter, RepTimer, RangeOfMotion

app = Flask(__name__)
# Bootstrap(app)
pose_class = 'shoulderpress'
repetition_counter = RepetitionCounter(
    class_name=pose_class + '_up',
    enter_threshold=6,
    exit_threshold=4)
rep_timer = RepTimer()
rom = RangeOfMotion(pose_class)


@app.route('/')
def physifeedback():
    return render_template('demo.html')


def updateMetricCountersIfNeeded(pose):
    global pose_class, repetition_counter, rep_timer, rom
    if pose_class != pose:
        pose_class = pose
        repetition_counter = RepetitionCounter(
            class_name=pose_class + '_up',
            enter_threshold=6,
            exit_threshold=4)
        rep_timer = RepTimer()
        rom = RangeOfMotion(pose_class)


def setPose(pose):
    if pose:
        updateMetricCountersIfNeeded(pose)
        return pose
    else:
        return 'full_model'


def getRepCount(classification):
    global repetition_counter
    prev_count = repetition_counter.n_repeats
    if classification is not None:
        return prev_count, repetition_counter(classification)
    return prev_count, repetition_counter.n_repeats


@app.route('/getpose', methods=['POST'])
def getpose():
    # print(request)
    pose_classification = None
    pose = setPose(request.args.get('pose'))

    json = request.json
    pose_landmarks = np.array(
        [[lmk['x'] * json['width'], lmk['y'] * json['height'], lmk['z'] * json['width']]
         for lmk in json['pose_landmarks']],
        dtype=np.float32)
    pose_classification = models[pose](pose_landmarks)

    prev_rep_count, curr_rep_count = getRepCount(pose_classification)
    left, right = rom.rom(pose_landmarks, prev_rep_count, curr_rep_count)
    avg_left, avg_right = rom.avgROM()
    response = jsonify({'pose': pose_classification,
                        'rep': {
                            'count': curr_rep_count,
                            'time': rep_timer(int(prev_rep_count), int(curr_rep_count)),
                            'avg': rep_timer.average(),
                        },
                        'rom': {
                            'left': left,
                            'right': right,
                            'avg_left': avg_left,
                            'avg_right': avg_right,
                        }})
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(debug=True)

# colors:
# #10d4dc
# #fbbc5c
# #d5f3ed
# #fccc7d
