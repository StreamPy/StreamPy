if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from Stream import Stream
from Operators import stream_func
from ML import Stream_Learn, LinearRegression
from ML.LinearRegression import linear_regression
import numpy as np

# Parameters

draw = True
output = False
num_features = 1
min_window_size = 2
max_window_size = 50
num_points = 1000
step_size = 1

if __name__ == "__main__":

    i = 0
    w = np.random.rand(num_features + 1, 1) * 2 - 1
    w *= 5

    m = LinearRegression.LinearRegressionStream(draw=draw, output=output,
                                          alpha=0.001)

    x = Stream('x')

    model = Stream_Learn(data_train=x, data_out=x, train_func=m.train,
                         predict_func=m.predict,
                         min_window_size=min_window_size,
                         max_window_size=max_window_size, step_size=step_size,
                         num_features=num_features)
    y = model.run()

    while i < num_points:
        w[1] += 0.01
        x_value = np.ones((1, num_features)) * i
        x_b = np.hstack((np.ones((1, 1)), x_value)).transpose()
        y_value = w.transpose().dot(x_b)[0][0]
        values = x_value.tolist()[0]
        values.append(y_value)
        x.extend([tuple(values)])

        print i
        i += 1

    print "Average error: ", m.avg_error
