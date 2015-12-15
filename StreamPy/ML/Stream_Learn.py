import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from functools import partial
from Stream import Stream, _no_value
from Operators import stream_func, dynamic_window_func
import numpy as np


class Stream_Learn:
    """
    Stream framework for machine learning.

    This class supports machine learning for streaming data using PSTREAMS.
    Given data for training and predicting along with functions to learn and
    predict, this class will output a stream of predictions. Both batch and
    continual learning is supported.

    Parameters
    ----------
    data_train : `Stream` or numpy.ndarray or other
        A object containing data to be trained on. In the case of `Stream`, the
        object contains tuples of values where each tuple represents a row of
        data. Each tuple must have at least `num_features` values. The object
        can also contain non-tuples provided `filter_func` is used to extract
        the tuples in correct format.
        In the case of a `numpy` array, the array must have at least
        `num_features` columns.
        Any additional values / columns correspond to the output y data.
        If this is not a `Stream` or `numpy` array, the data will not be split
        into x and y.
    data_out : `Stream`
        A `Stream` object containing data to generate predictions on.
        The `Stream` contains tuples of values where each tuple represents a
        row of data and must have at least `num_features` values.
    train_func : function
        A function that trains a model.
        This function takes parameters x and y data, a model object, and a
        window_state tuple, and returns a trained model object.
        In the case of `data_train` as a `Stream`, this function has the
        signature (numpy.ndarray numpy.ndarray Object) -> (Object). The first
        parameter x will have dimensions i x `num_features`, where
        `min_window_size` <= i <= `max_window_size`. The second parameter y
        will have dimensions i x num_outputs, where num_outputs refers to the
        number of y outputs for an input. For example, num_outputs is 1 for 1
        scalar output. For unsupervised learning, num_outputs is 0.
        In the case of `data_train` as a `numpy` array, this function has the
        signature (numpy.ndarray numpy.ndarray Object) -> (Object). The first
        parameter x will have dimensions N x `num_features`, where N refers to
        the total number of training examples. The second parameter y will have
        dimensions N x num_outputs where num_outputs is defined as before.
        If `data_train` is none of the above, the function has the signature
        (Object None Object) -> (Object). The first parameter is `data_train`.
        The third parameter is a model defined by this function.
        The fourth parameter is a window_state tuple with the values
        (current_window_size, steady_state, reset, `step_size`,
        `max_window_size`),
        where current_window_size describes the number of points in the window,
        steady_state is a boolean that describes whether the window has reached
        `max_window_size`, and reset is a boolean that can be set to True to
        reset the window.
    predict_func : function
        A function that takes as input 2 tuples corresponding to 1 row of data
        and a model and returns the prediction output.
        This function has the signature (tuple tuple Object) -> (Object).
        The first tuple x has `num_features` values and the second tuple y
        has num_outputs values, where num_outputs refers to the number of y
        outputs for an input. In the case of unsupervised learning, y is empty.
    min_window_size : int
        An int specifying the minimum size of the window to train on for
        continual learning. This will be ignored for batch learning.
    max_window_size : int
        An int specifying the maximum size of the window to train on for
        continual learning. This will be ignored for batch learning.
    step_size : int
        An int specifying the number of tuples to move the window by for
        continual learning. This will be ignored for batch learning.
    num_features : int
        An int that describes the number of features in the data.
    filter_func : function, optional
        A function that filters data for training.
        This function takes parameters x and y data and a model object, and
        returns a tuple with signature (boolean, tuple). The first value in the
        output describes if the data is to be trained on (True) or if it is an
        outlier (False). The second value is the tuple of data in correct
        format as described for `data_train`.
        If `data_train` is a `Stream` that contains tuples, this function has
        the signature (tuple tuple Object) -> (tuple). The first tuple x has
        `num_features` values and the second tuple y has num_outputs values,
        where num_outputs refers to the number of y outputs for an input.
        The third parameter is a model defined by `train_func`.
        If `data_train` is a `Stream` that does not contain tuples, this
        function has the signature (Object None Object) -> (tuple), where
        the first parameter has the same type as the values in `data_train`.
    all_func : function, optional
        A function that processes the data for usage such as visualization.
        This function takes parameters x and y data, a model object, a state
        object, and a window_state tuple and returns an updated state object.
        This function has the signature
        (np.ndarray np.ndarray Object Object tuple) -> (Object).
        The first numpy array x has dimensions i x `num_features`, where
        `min_window_size` <= i <= `max_window_size`. The second numpy array y
        has dimensions i x num_outputs, where num_outputs refers to the number
        of y outputs for an input. The third parameter is the model object
        defined by `train_func`. The fourth parameter is a state object defined
        by this function. The fifth parameter is a window_state tuple with
        values as defined in description for `train_func`.

"""

    def __init__(self, data_train, data_out, train_func, predict_func,
                 min_window_size, max_window_size, step_size, num_features,
                 filter_func=None, all_func=None):
        self.data_train = data_train
        self.data_out = data_out
        self.train_func = train_func
        self.predict_func = predict_func
        self.min_window_size = min_window_size
        self.max_window_size = max_window_size
        self.step_size = step_size
        self.num_features = num_features
        self.filter_func = filter_func
        self.all_func = all_func
        self.window_state = [0, False, False, self.step_size,
                             self.max_window_size]

    def _initialize(self):
        self.trained = False
        self.model = None
        self.x_train = Stream('x_train')
        self.state = None

    def _filter_f(self, n):
        # If filter_func is provided and the model has been trained
        if self.trained and self.filter_func is not None:
            if not isinstance(n, tuple):
                [train_data, data] = self.filter_func(n, None, self.model)
            else:
                x = n[0:self.num_features]
                y = n[self.num_features:]
                [train_data, data] = self.filter_func(x, y, self.model)
            if train_data:
                self.x_train.extend([data])

        # filter_func is None or the model is not trained
        else:
            self.x_train.extend([n])

    def _train(self, lst, state):
        data = np.array(lst)
        x = data[:, 0:self.num_features]
        y = data[:, self.num_features:]
        self.model = self.train_func(x, y, self.model, state)
        self.trained = True
        if state[1] and state[2]:
            self.model = None
            self.trained = False
        return (_no_value, state)

    def _predict(self, n):
        if self.trained:
            if not isinstance(n, tuple):
                return self.predict_func(n, None, self.model)
            x = n[0:self.num_features]
            y = n[self.num_features:]
            return self.predict_func(x, y, self.model)
        return _no_value

    def _all_f(self, lst, state):
        data = np.array(lst)
        x = data[:, 0:self.num_features]
        y = data[:, self.num_features:]
        self.state = self.all_func(x, y, self.model, self.state, state)
        return (_no_value, state)

    def _init_streams(self):

        self.stream_filter = partial(stream_func, f_type='element',
                                     f=self._filter_f, num_outputs=0)
        self.stream_train = partial(dynamic_window_func, f=self._train,
                                    min_window_size=self.min_window_size,
                                    max_window_size=self.max_window_size,
                                    step_size=self.step_size,
                                    state=self.window_state)
        self.stream_predict = partial(stream_func, f_type='element',
                                      f=self._predict, num_outputs=1)
        self.stream_all = partial(dynamic_window_func, f=self._all_f,
                                  min_window_size=self.min_window_size,
                                  max_window_size=self.max_window_size,
                                  step_size=self.step_size,
                                  state=[0, False, False])

    def run(self):
        """
        Runs the framework and returns a `Stream` of outputs.

        Returns
        -------
        y_predict : `Stream`
            A `Stream` containing outputs as returned by `predict_func`.

        """
        self._initialize()
        self._init_streams()
        self.model_stream = Stream('model')
        self.all_stream = Stream('all')

        # Continual learning
        if isinstance(self.data_train, Stream):
            self.stream_filter(self.data_train)
            self.stream_train(inputs=self.x_train)
            if self.all_func is not None:
                self.stream_all(inputs=self.data_train)

        # Batch learning with numpy array
        elif isinstance(self.data_train, np.ndarray):
            x = self.data_train[:, 0:self.num_features]
            y = self.data_train[:, self.num_features:]
            self.model = self.train_func(x, y, None, None)
            self.trained = True

        # Batch learning
        else:
            self.model = self.train_func(self.data_train, None, None, None)
            self.trained = True

        y_predict = self.stream_predict(self.data_out)

        return y_predict

    def reset(self):
        """
        Resets the training window to `min_window_size`.

        This function resets the training window to `min_window_size`. After
        resetting, the window has the last `min_window_size` points in the
        `Stream` `x_train`. For example, if `max_window_size` is 100,
        `min_window_size` is 2, and the window contains points [1, 100],
        after resetting the window contains points [98, 99].

        Notes
        -----
        If reset() is called before the window has reached `max_window_size`,
        the window will continue increasing in size until it reaches
        `max_window_size`. Then, the window will reset to `min_window_size`.

        """
        self.window_state[2] = True
