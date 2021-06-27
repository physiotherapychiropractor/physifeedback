export class RepTimer {
    _start_time = 0
    _current_time = 0
    _history = []
    _elapsed_time = 0

    average() {
        if (this._history.length > 0) {
            return Math.round(this._history.reduce((a, b) => a + b, 0) / this._history.length, 2) + 's';
        }
        return null;
    }

    repTimer(prev_repetition_count, repetitions_count) {
        this._current_time = new Date().getTime() / 1000;
        if (repetitions_count == 0) {
            return null;
        }
        if (repetitions_count == prev_repetition_count + 1) {
            this._history.push(this._elapsed_time);
            this._start_time = this._current_time;
        }
        this._elapsed_time = Math.round(this._current_time - this._start_time);
        return this._elapsed_time + 's';
    }
}
