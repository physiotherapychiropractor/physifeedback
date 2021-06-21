import csv
import math
import numpy as np
import os
import time

poses = ['bridge', 'hamstring', 'laterallegraise', 'shoulderflexion', 'shoulderpress']


class RangeOfMotion:

    def __init__(self, pose_class_name):
        self._left = []
        self._right = []
        self._pose = pose_class_name
        self._max_right = []
        self._max_left = []

    def saveAndGetPercentage(self, left, right, offset, maximum):
        left_p = min(max(0, round(((left - offset) / maximum) * 100)), 100)
        right_p = min(max(0, round(((right - offset) / maximum) * 100)), 100)
        self._left.append(left_p)
        self._right.append(right_p)
        return left_p, right_p

    def shoulderPress(self, pose_landmarks):
        left_elbow = self.getAngle((pose_landmarks[15, 0], pose_landmarks[15, 1]),
                                   (pose_landmarks[13, 0], pose_landmarks[13, 1]),
                                   (pose_landmarks[11, 0], pose_landmarks[11, 1]))
        right_elbow = self.getAngle((pose_landmarks[16, 0], pose_landmarks[16, 1]),
                                    (pose_landmarks[14, 0], pose_landmarks[14, 1]),
                                    (pose_landmarks[12, 0], pose_landmarks[12, 1]))
        return self.saveAndGetPercentage(left_elbow, right_elbow, 90, 90)

    def hamstring(self, pose_landmarks):
        right_knee = self.getAngle((pose_landmarks[24, 0], pose_landmarks[24, 1]),
                                   (pose_landmarks[26, 0], pose_landmarks[26, 1]),
                                   (pose_landmarks[28, 0], pose_landmarks[28, 1]))
        left_knee = self.getAngle((pose_landmarks[23, 0], pose_landmarks[23, 1]),
                                  (pose_landmarks[25, 0], pose_landmarks[25, 1]),
                                  (pose_landmarks[27, 0], pose_landmarks[27, 1]))
        return self.saveAndGetPercentage(left_knee, right_knee, 90, 90)

    def shoulderFlexion(self, pose_landmarks):
        right_shoulder = self.getAngle((pose_landmarks[16, 0], pose_landmarks[16, 1]),
                                       (pose_landmarks[12, 0], pose_landmarks[12, 1]),
                                       (pose_landmarks[24, 0], pose_landmarks[24, 1]))
        left_shoulder = self.getAngle((pose_landmarks[15, 0], pose_landmarks[15, 1]),
                                      (pose_landmarks[11, 0], pose_landmarks[11, 1]),
                                      (pose_landmarks[23, 0], pose_landmarks[23, 1]))
        leftshoulder_ROMint = round(((left_shoulder / 180) * 100))
        self._left.append(leftshoulder_ROMint)
        return self.saveAndGetPercentage(left_shoulder, right_shoulder, 0, 180)

    def lateralLegRaise(self, pose_landmarks):
        right_hip = self.getAngle((pose_landmarks[23, 0], pose_landmarks[23, 1]),
                                  (pose_landmarks[24, 0], pose_landmarks[24, 1]),
                                  (pose_landmarks[28, 0], pose_landmarks[28, 1]))
        left_hip = self.getAngle((pose_landmarks[24, 0], pose_landmarks[24, 1]),
                                 (pose_landmarks[23, 0], pose_landmarks[23, 1]),
                                 (pose_landmarks[27, 0], pose_landmarks[27, 1]))
        return self.saveAndGetPercentage(left_hip, right_hip, 90, 60)

    def bridge(self, pose_landmarks):
        right_hip = self.getAngle((pose_landmarks[12, 0], pose_landmarks[12, 1]),
                                  (pose_landmarks[24, 0], pose_landmarks[24, 1]),
                                  (pose_landmarks[26, 0], pose_landmarks[26, 1]))
        left_hip = self.getAngle((pose_landmarks[11, 0], pose_landmarks[11, 1]),
                                 (pose_landmarks[23, 0], pose_landmarks[23, 1]),
                                 (pose_landmarks[25, 0], pose_landmarks[25, 1]))
        return self.saveAndGetPercentage(left_hip, right_hip, 120, 60)

    def getAngle(self, firstPoint, midPoint, lastPoint):
        firstPointX, firstPointY = firstPoint
        midPointX, midPointY = midPoint
        lastPointX, lastPointY = lastPoint
        result = math.degrees(math.atan2(lastPointY - midPointY,
                                         lastPointX - midPointX)
                              - math.atan2(firstPointY - midPointY,
                                           firstPointX - midPointX))
        result = np.abs(result)
        if result > 180:
            result = 360.0 - result
        return result

    _rom = {
        'bridge': bridge,
        'hamstring': hamstring,
        'laterallegraise': lateralLegRaise,
        'shoulderflexion': shoulderFlexion,
        'shoulderpress': shoulderPress,
    }

    def rom(self, pose_landmarks, prev_rep_count, curr_rep_count):
        if curr_rep_count == prev_rep_count + 1:
            self._max_right.append(max(self._right))
            self._max_left.append(max(self._left))
            self._left = []
            self._right = []
        return self._rom[self._pose](self, pose_landmarks)

    def avgROM(self):
        if len(self._max_left) == 0 or len(self._max_right) == 0:
            return None, None
        left = str(round(sum(self._max_left) / len(self._max_left))) + '%'
        right = str(round(sum(self._max_right) / len(self._max_right))) + '%'
        return left, right


class RepTimer:
    def __init__(self):
        self._start_time = 0
        self._current_time = 0
        self._history = []
        self._elapsed_time = 0

    def average(self):
        if len(self._history) > 0:
            return str(round(sum(self._history) / len(self._history), 2)) + 's'
        return None

    def __call__(self, prev_repetition_count, repetitions_count):
        self._current_time = time.time()
        if repetitions_count == 0:
            return None
        if repetitions_count == prev_repetition_count + 1:
            self._history.append(self._elapsed_time)
            self._start_time = self._current_time
        self._elapsed_time = round(self._current_time - self._start_time)
        return str(self._elapsed_time) + 's'


class RepetitionCounter(object):
    """Counts number of repetitions of given target pose class."""

    def __init__(self, class_name, enter_threshold=6, exit_threshold=4):
        self._class_name = class_name

        # If pose counter passes given threshold, then we enter the pose.
        self._enter_threshold = enter_threshold
        self._exit_threshold = exit_threshold

        # Either we are in given pose or not.
        self._pose_entered = False

        # Number of times we exited the pose.
        self._n_repeats = 0

    @property
    def n_repeats(self):
        return self._n_repeats

    def __call__(self, pose_classification):
        """Counts number of repetitions happend until given frame.

        We use two thresholds. First you need to go above the higher one to enter
        the pose, and then you need to go below the lower one to exit it. Difference
        between the thresholds makes it stable to prediction jittering (which will
        cause wrong counts in case of having only one threshold).

        Args:
          pose_classification: Pose classification dictionary on current frame.
            Sample:
              {
                'pushups_down': 8.3,
                'pushups_up': 1.7,
              }

        Returns:
          Integer counter of repetitions.
        """
        # Get pose confidence.
        pose_confidence = 0.0
        if self._class_name in pose_classification:
            pose_confidence = pose_classification[self._class_name]

        # On the very first frame or if we were out of the pose, just check if we
        # entered it on this frame and update the state.

        if not self._pose_entered:
            self._pose_entered = pose_confidence > self._enter_threshold
            return self._n_repeats

        # If we were in the pose and are exiting it, then increase the counter and
        # update the state.
        if pose_confidence < self._exit_threshold:
            self._n_repeats += 1
            self._pose_entered = False

        return self._n_repeats


class FullBodyPoseEmbedder(object):
    """Converts 3D pose landmarks into 3D embedding."""

    def __init__(self, torso_size_multiplier=2.5):
        # Multiplier to apply to the torso to get minimal body size.
        self._torso_size_multiplier = torso_size_multiplier

        # Names of the landmarks as they appear in the prediction.
        self._landmark_names = [
            'nose',
            'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear',
            'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder',
            'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist',
            'left_pinky_1', 'right_pinky_1',
            'left_index_1', 'right_index_1',
            'left_thumb_2', 'right_thumb_2',
            'left_hip', 'right_hip',
            'left_knee', 'right_knee',
            'left_ankle', 'right_ankle',
            'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index',
        ]

    def __call__(self, landmarks):
        """Normalizes pose landmarks and converts to embedding

        Args:
          landmarks - NumPy array with 3D landmarks of shape (N, 3).

        Result:
          Numpy array with pose embedding of shape (M, 3) where `M` is the number of
          pairwise distances defined in `_get_pose_distance_embedding`.
        """
        assert landmarks.shape[0] == len(self._landmark_names), 'Unexpected number of landmarks: {}'.format(
            landmarks.shape[0])

        # Get pose landmarks.
        landmarks = np.copy(landmarks)

        # Normalize landmarks.
        landmarks = self._normalize_pose_landmarks(landmarks)

        # Get embedding.
        embedding = self._get_pose_distance_embedding(landmarks)

        return embedding

    def _normalize_pose_landmarks(self, landmarks):
        """Normalizes landmarks translation and scale."""
        landmarks = np.copy(landmarks)

        # Normalize translation.
        pose_center = self._get_pose_center(landmarks)
        landmarks -= pose_center

        # Normalize scale.
        pose_size = self._get_pose_size(landmarks, self._torso_size_multiplier)
        landmarks /= pose_size
        # Multiplication by 100 is not required, but makes it eaasier to debug.
        landmarks *= 100

        return landmarks

    def _get_pose_center(self, landmarks):
        """Calculates pose center as point between hips."""
        left_hip = landmarks[self._landmark_names.index('left_hip')]
        right_hip = landmarks[self._landmark_names.index('right_hip')]
        center = (left_hip + right_hip) * 0.5
        return center

    def _get_pose_size(self, landmarks, torso_size_multiplier):
        """Calculates pose size.

        It is the maximum of two values:
          * Torso size multiplied by `torso_size_multiplier`
          * Maximum distance from pose center to any pose landmark
        """
        # This approach uses only 2D landmarks to compute pose size.
        landmarks = landmarks[:, :2]

        # Hips center.
        left_hip = landmarks[self._landmark_names.index('left_hip')]
        right_hip = landmarks[self._landmark_names.index('right_hip')]
        hips = (left_hip + right_hip) * 0.5

        # Shoulders center.
        left_shoulder = landmarks[self._landmark_names.index('left_shoulder')]
        right_shoulder = landmarks[self._landmark_names.index('right_shoulder')]
        shoulders = (left_shoulder + right_shoulder) * 0.5

        # Torso size as the minimum body size.
        torso_size = np.linalg.norm(shoulders - hips)

        # Max dist to pose center.
        pose_center = self._get_pose_center(landmarks)
        max_dist = np.max(np.linalg.norm(landmarks - pose_center, axis=1))

        return max(torso_size * torso_size_multiplier, max_dist)

    def _get_pose_distance_embedding(self, landmarks):
        """Converts pose landmarks into 3D embedding.

        We use several pairwise 3D distances to form pose embedding. All distances
        include X and Y components with sign. We differnt types of pairs to cover
        different pose classes. Feel free to remove some or add new.

        Args:
          landmarks - NumPy array with 3D landmarks of shape (N, 3).

        Result:
          Numpy array with pose embedding of shape (M, 3) where `M` is the number of
          pairwise distances.
        """
        embedding = np.array([
            # One joint.

            self._get_distance(
                self._get_average_by_names(landmarks, 'left_hip', 'right_hip'),
                self._get_average_by_names(landmarks, 'left_shoulder', 'right_shoulder')),

            self._get_distance_by_names(landmarks, 'left_shoulder', 'left_elbow'),
            self._get_distance_by_names(landmarks, 'right_shoulder', 'right_elbow'),

            self._get_distance_by_names(landmarks, 'left_elbow', 'left_wrist'),
            self._get_distance_by_names(landmarks, 'right_elbow', 'right_wrist'),

            self._get_distance_by_names(landmarks, 'left_hip', 'left_knee'),
            self._get_distance_by_names(landmarks, 'right_hip', 'right_knee'),

            self._get_distance_by_names(landmarks, 'left_knee', 'left_ankle'),
            self._get_distance_by_names(landmarks, 'right_knee', 'right_ankle'),

            # Two joints.

            self._get_distance_by_names(landmarks, 'left_shoulder', 'left_wrist'),
            self._get_distance_by_names(landmarks, 'right_shoulder', 'right_wrist'),

            self._get_distance_by_names(landmarks, 'left_hip', 'left_ankle'),
            self._get_distance_by_names(landmarks, 'right_hip', 'right_ankle'),

            # Four joints.

            self._get_distance_by_names(landmarks, 'left_hip', 'left_wrist'),
            self._get_distance_by_names(landmarks, 'right_hip', 'right_wrist'),

            # Five joints.

            self._get_distance_by_names(landmarks, 'left_shoulder', 'left_ankle'),
            self._get_distance_by_names(landmarks, 'right_shoulder', 'right_ankle'),

            self._get_distance_by_names(landmarks, 'left_hip', 'left_wrist'),
            self._get_distance_by_names(landmarks, 'right_hip', 'right_wrist'),

            # Cross body.

            self._get_distance_by_names(landmarks, 'left_elbow', 'right_elbow'),
            self._get_distance_by_names(landmarks, 'left_knee', 'right_knee'),

            self._get_distance_by_names(landmarks, 'left_wrist', 'right_wrist'),
            self._get_distance_by_names(landmarks, 'left_ankle', 'right_ankle'),

            # Body bent direction.

            # self._get_distance(
            #     self._get_average_by_names(landmarks, 'left_wrist', 'left_ankle'),
            #     landmarks[self._landmark_names.index('left_hip')]),
            # self._get_distance(
            #     self._get_average_by_names(landmarks, 'right_wrist', 'right_ankle'),
            #     landmarks[self._landmark_names.index('right_hip')]),
        ])

        return embedding

    def _get_average_by_names(self, landmarks, name_from, name_to):
        lmk_from = landmarks[self._landmark_names.index(name_from)]
        lmk_to = landmarks[self._landmark_names.index(name_to)]
        return (lmk_from + lmk_to) * 0.5

    def _get_distance_by_names(self, landmarks, name_from, name_to):
        lmk_from = landmarks[self._landmark_names.index(name_from)]
        lmk_to = landmarks[self._landmark_names.index(name_to)]
        return self._get_distance(lmk_from, lmk_to)

    def _get_distance(self, lmk_from, lmk_to):
        return lmk_to - lmk_from


class PoseSample(object):

    def __init__(self, name, landmarks, class_name, embedding):
        self.name = name
        self.landmarks = landmarks
        self.class_name = class_name

        self.embedding = embedding


class PoseSampleOutlier(object):

    def __init__(self, sample, detected_class, all_classes):
        self.sample = sample
        self.detected_class = detected_class
        self.all_classes = all_classes


class PoseClassifier(object):
    """Classifies pose landmarks."""

    def __init__(self,
                 pose_samples_folder,
                 pose_embedder,
                 file_extension='csv',
                 file_separator=',',
                 n_landmarks=33,
                 n_dimensions=3,
                 top_n_by_max_distance=30,
                 top_n_by_mean_distance=10,
                 axes_weights=(1., 1., 0.2)):
        self._pose_embedder = pose_embedder
        self._n_landmarks = n_landmarks
        self._n_dimensions = n_dimensions
        self._top_n_by_max_distance = top_n_by_max_distance
        self._top_n_by_mean_distance = top_n_by_mean_distance
        self._axes_weights = axes_weights

        self._pose_samples = self._load_pose_samples(pose_samples_folder,
                                                     file_extension,
                                                     file_separator,
                                                     n_landmarks,
                                                     n_dimensions,
                                                     pose_embedder)

    def _load_pose_samples(self,
                           pose_samples_folder,
                           file_extension,
                           file_separator,
                           n_landmarks,
                           n_dimensions,
                           pose_embedder):
        """Loads pose samples from a given folder.

        Required folder structure:
          neutral_standing.csv
          pushups_down.csv
          pushups_up.csv
          squats_down.csv
          ...

        Required CSV structure:
          sample_00001,x1,y1,z1,x2,y2,z2,....
          sample_00002,x1,y1,z1,x2,y2,z2,....
          ...
        """
        # Each file in the folder represents one pose class.
        file_names = [name for name in os.listdir(pose_samples_folder) if name.endswith(file_extension)]

        pose_samples = []
        for file_name in file_names:
            # Use file name as pose class name.
            class_name = file_name[:-(len(file_extension) + 1)]

            # Parse CSV.
            with open(os.path.join(pose_samples_folder, file_name)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=file_separator)
                for row in csv_reader:
                    assert len(row) == n_landmarks * n_dimensions + 1, 'Wrong number of values: {}'.format(len(row))
                    landmarks = np.array(row[1:], np.float32).reshape([n_landmarks, n_dimensions])
                    pose_samples.append(PoseSample(
                        name=row[0],
                        landmarks=landmarks,
                        class_name=class_name,
                        embedding=pose_embedder(landmarks),
                    ))

        return pose_samples

    def find_pose_sample_outliers(self):
        """Classifies each sample against the entire database."""
        # Find outliers in target poses
        outliers = []
        for sample in self._pose_samples:
            # Find nearest poses for the target one.
            pose_landmarks = sample.landmarks.copy()
            pose_classification = self.__call__(pose_landmarks)
            class_names = [class_name for class_name, count in pose_classification.items() if
                           count == max(pose_classification.values())]

            # Sample is an outlier if nearest poses have different class or more than
            # one pose class is detected as nearest.
            if sample.class_name not in class_names or len(class_names) != 1:
                outliers.append(PoseSampleOutlier(sample, class_names, pose_classification))

        return outliers

    def __call__(self, pose_landmarks):
        """Classifies given pose.

        Classification is done in two stages:
          * First we pick top-N samples by MAX distance. It allows to remove samples
            that are almost the same as given pose, but has few joints bent in the
            other direction.
          * Then we pick top-N samples by MEAN distance. After outliers are removed
            on a previous step, we can pick samples that are closes on average.

        Args:
          pose_landmarks: NumPy array with 3D landmarks of shape (N, 3).

        Returns:
          Dictionary with count of nearest pose samples from the database. Sample:
            {
              'pushups_down': 8,
              'pushups_up': 2,
            }
        """
        # Check that provided and target poses have the same shape.
        assert pose_landmarks.shape == (self._n_landmarks, self._n_dimensions), 'Unexpected shape: {}'.format(
            pose_landmarks.shape)

        # Get given pose embedding.
        pose_embedding = self._pose_embedder(pose_landmarks)
        flipped_pose_embedding = self._pose_embedder(pose_landmarks * np.array([-1, 1, 1]))

        # Filter by max distance.
        #
        # That helps to remove outliers - poses that are almost the same as the
        # given one, but has one joint bent into another direction and actually
        # represnt a different pose class.
        max_dist_heap = []
        for sample_idx, sample in enumerate(self._pose_samples):
            max_dist = min(
                np.max(np.abs(sample.embedding - pose_embedding) * self._axes_weights),
                np.max(np.abs(sample.embedding - flipped_pose_embedding) * self._axes_weights),
            )
            max_dist_heap.append([max_dist, sample_idx])

        max_dist_heap = sorted(max_dist_heap, key=lambda x: x[0])
        max_dist_heap = max_dist_heap[:self._top_n_by_max_distance]

        # Filter by mean distance.
        #
        # After removing outliers we can find the nearest pose by mean distance.
        mean_dist_heap = []
        for _, sample_idx in max_dist_heap:
            sample = self._pose_samples[sample_idx]
            mean_dist = min(
                np.mean(np.abs(sample.embedding - pose_embedding) * self._axes_weights),
                np.mean(np.abs(sample.embedding - flipped_pose_embedding) * self._axes_weights),
            )
            mean_dist_heap.append([mean_dist, sample_idx])

        mean_dist_heap = sorted(mean_dist_heap, key=lambda x: x[0])
        mean_dist_heap = mean_dist_heap[:self._top_n_by_mean_distance]

        # Collect results into map: (class_name -> n_samples)
        class_names = [self._pose_samples[sample_idx].class_name for _, sample_idx in mean_dist_heap]
        result = {class_name: class_names.count(class_name) for class_name in set(class_names)}

        return result


class EMADictSmoothing(object):
    """Smoothes pose classification."""

    def __init__(self, window_size=10, alpha=0.2):
        self._window_size = window_size
        self._alpha = alpha

        self._data_in_window = []

    def __call__(self, data):
        """Smoothes given pose classification.

        Smoothing is done by computing Exponential Moving Average for every pose
        class observed in the given time window. Missed pose classes arre replaced
        with 0.

        Args:
          data: Dictionary with pose classification. Sample:
              {
                'pushups_down': 8,
                'pushups_up': 2,
              }

        Result:
          Dictionary in the same format but with smoothed and float instead of
          integer values. Sample:
            {
              'pushups_down': 8.3,
              'pushups_up': 1.7,
            }
        """
        # Add new data to the beginning of the window for simpler code.
        self._data_in_window.insert(0, data)
        self._data_in_window = self._data_in_window[:self._window_size]

        # Get all keys.
        keys = set([key for data in self._data_in_window for key, _ in data.items()])

        # Get smoothed values.
        smoothed_data = dict()
        for key in keys:
            factor = 1.0
            top_sum = 0.0
            bottom_sum = 0.0
            for data in self._data_in_window:
                value = data[key] if key in data else 0.0

                top_sum += factor * value
                bottom_sum += factor

                # Update factor.
                factor *= (1.0 - self._alpha)

            smoothed_data[key] = top_sum / bottom_sum

        return smoothed_data


pose_embedder = FullBodyPoseEmbedder()

models = {}

for pose in poses:
    model = PoseClassifier(
        pose_samples_folder='model/csv/' + pose,
        pose_embedder=pose_embedder,
        top_n_by_max_distance=30,
        top_n_by_mean_distance=10)
    models[pose] = model

models['full_model'] = PoseClassifier(
    pose_samples_folder='model/csv/all',
    pose_embedder=pose_embedder,
    top_n_by_max_distance=30,
    top_n_by_mean_distance=10)

smoother = EMADictSmoothing(
    window_size=10,
    alpha=0.2)
