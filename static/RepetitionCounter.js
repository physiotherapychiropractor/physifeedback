export class RepetitionCounter {
    // """Counts number of repetitions of given target pose class."""

    _class_name = '';
    _pose_entered = false;
    _n_repeats = 0;
    

    constructor(class_name, enter_threshold=6, exit_threshold=4) {
        this._class_name = class_name;

        // # If pose counter passes given threshold, then we enter the pose.
        this._enter_threshold = enter_threshold;
        this._exit_threshold = exit_threshold;

        // # Either we are in given pose or not.
        // this._pose_entered = False;

        // # Number of times we exited the pose.
        // this._n_repeats = 0;
    }

    get n_repeats() {
        return this._n_repeats;
    }

    repetitionCounter(pose_classification) {
        // """Counts number of repetitions happend until given frame.

        // We use two thresholds. First you need to go above the higher one to enter
        // the pose, and then you need to go below the lower one to exit it. Difference
        // between the thresholds makes it stable to prediction jittering (which will
        // cause wrong counts in case of having only one threshold).

        // Args:
        // pose_classification: Pose classification dictionary on current frame.
            // Sample:
            // {
                // 'pushups_down': 8.3,
                // 'pushups_up': 1.7,
            // }

        // Returns:
        // Integer counter of repetitions.
        // """
        // # Get pose confidence.
        var pose_confidence = 0.0;
        if (this._class_name in pose_classification) {
            pose_confidence = pose_classification[this._class_name];
        }
        // # On the very first frame or if we were out of the pose, just check if we
        // # entered it on this frame and update the state.

        if (!this._pose_entered) {
            this._pose_entered = pose_confidence > this._enter_threshold;
            return this._n_repeats;
        }

        // # If we were in the pose and are exiting it, then increase the counter and
        // # update the state.
        if (pose_confidence < this._exit_threshold) {
            this._n_repeats += 1;
            this._pose_entered = false;
        }

        return this._n_repeats;
    }
}