if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from Stream import Stream
from Operators import stream_func
from ML import Stream_Learn
import numpy as np
from sklearn import linear_model

# Parameters
num_features = 1
num_points = 1000

def train_function(x, y, model, window_state):
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    return regr

def predict_function(x, y, model):
    y_predict = model.predict(x)
    return (x[0], y_predict.flatten().tolist()[0])

def print_stream(y):
    print y

if __name__ == "__main__":

    i = 0
    x = np.zeros((100, 2))

    for i in range(0, 100):
        x[i, 0] = i
        x[i, 1] = 2 * i

    predict_stream = Stream('predict')

    model = Stream_Learn(data_train=x, data_out=predict_stream,
                         train_func=train_function,
                         predict_func=predict_function,
                         min_window_size=2,
                         max_window_size=2, step_size=1,
                         num_features=num_features)
    y = model.run()
    stream_func(inputs=y, f=print_stream, f_type='element', num_outputs=0)

    while i < num_points:
        x_value = np.random.rand(1, num_features) * 2 - 1
        x_b = np.hstack((np.ones((1, 1)), x_value)).transpose()
        values = x_value.tolist()[0]
        predict_stream.extend([tuple(values)])

        i += 1
