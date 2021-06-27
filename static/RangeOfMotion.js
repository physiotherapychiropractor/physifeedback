export class RangeOfMotion {

    _left = [];
    _right = [];
    _max_right = [];
    _max_left = [];
    _pose;
    
    constructor(pose_class_name) {
        this._pose = pose_class_name;
    }

    getAngle(firstPoint, midPoint, lastPoint) {
        const [firstPointX, firstPointY, ignore1] = firstPoint;
        const [midPointX, midPointY, ignore2] = midPoint;
        const [lastPointX, lastPointY, ignore3] = lastPoint;
        var result = (Math.atan2(lastPointY - midPointY,
                                        lastPointX - midPointX)
                            - Math.atan2(firstPointY - midPointY,
                                        firstPointX - midPointX)) / (Math.PI / 180);
        result = Math.abs(result);
        if (result > 180) {
            result = 360.0 - result;
        }
        return result;
    }

    saveAndGetPercentage(left, right, offset, maximum) {
        const left_p = Math.min(Math.max(0, Math.round(((left - offset) / maximum) * 100)), 100);
        const right_p = Math.min(Math.max(0, Math.round(((right - offset) / maximum) * 100)), 100);
        this._left.push(left_p);
        this._right.push(right_p);
        return [left_p, right_p];
    }

    shoulderPress(pose_landmarks) {
        const left_elbow = this.getAngle(pose_landmarks[15], pose_landmarks[13], pose_landmarks[11]);
        const right_elbow = this.getAngle(pose_landmarks[16], pose_landmarks[14], pose_landmarks[12]);
        return this.saveAndGetPercentage(left_elbow, right_elbow, 90, 90);
    }

    hamstring(pose_landmarks) {
        const right_knee = this.getAngle(pose_landmarks[24], pose_landmarks[26], pose_landmarks[28]);
        const left_knee = this.getAngle(pose_landmarks[23], pose_landmarks[25], pose_landmarks[27]);
        return this.saveAndGetPercentage(left_knee, right_knee, 90, 90);
    }

    shoulderFlexion(pose_landmarks) {
        const right_shoulder = this.getAngle(pose_landmarks[16], pose_landmarks[12], pose_landmarks[24]);
        const left_shoulder = this.getAngle(pose_landmarks[15], pose_landmarks[11], pose_landmarks[23]);
        const leftshoulder_ROMint = Math.round(((left_shoulder / 180) * 100));
        this._left.push(leftshoulder_ROMint);
        return this.saveAndGetPercentage(left_shoulder, right_shoulder, 0, 180);
    }

    lateralLegRaise(pose_landmarks) {
        const right_hip = this.getAngle(pose_landmarks[23], pose_landmarks[24], pose_landmarks[28]);
        const left_hip = this.getAngle(pose_landmarks[24], pose_landmarks[23], pose_landmarks[27]);
        return this.saveAndGetPercentage(left_hip, right_hip, 90, 60);
    }

    bridge(pose_landmarks) {
        const right_hip = this.getAngle((pose_landmarks[12, 0], pose_landmarks[12, 1]),
                                (pose_landmarks[24, 0], pose_landmarks[24, 1]),
                                (pose_landmarks[26, 0], pose_landmarks[26, 1]));
        const left_hip = this.getAngle((pose_landmarks[11, 0], pose_landmarks[11, 1]),
                                (pose_landmarks[23, 0], pose_landmarks[23, 1]),
                                (pose_landmarks[25, 0], pose_landmarks[25, 1]));
        return this.saveAndGetPercentage(left_hip, right_hip, 120, 60);
    }

    map = {
        'bridge': this.bridge,
        'hamstring': this.hamstring,
        'laterallegraise': this.lateralLegRaise,
        'shoulderflexion': this.shoulderFlexion,
        'shoulderpress': this.shoulderPress,
    };

    rom(pose_landmarks, prev_rep_count, curr_rep_count) {
        if (curr_rep_count == prev_rep_count + 1) {
            this._max_right.push(Math.max(...this._right));
            this._max_left.push(Math.max(...this._left));
            this._left = [];
            this._right = [];
        }
        switch (this._pose) {
            case 'bridge':
                return this.bridge(pose_landmarks);
            case 'hamstring':
                return this.hamstring(pose_landmarks);
            case 'laterallegraise':
                return this.lateralLegRaise(pose_landmarks);
            case 'shoulderflexion':
                return this.shoulderFlexion(pose_landmarks);
            case 'shoulderpress':
                return this.shoulderPress(pose_landmarks);
            default:
                return;
        }
    }

    avgROM() {
        if (this._max_left.length == 0 || this._max_right.length == 0) {
            return ['', ''];
        }
        var left = Math.round(this._max_left.reduce((a, b) => a + b, 0) / this._max_left.length) + '%';
        var right = Math.round(this._max_right.reduce((a, b) => a + b, 0) / this._max_right.length) + '%';
        return [left, right];
    }
}