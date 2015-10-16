if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))


from Stream import Stream
from ML import Stream_Learn
from ML import KMeans
from ML.KMeans import kmeans
import numpy as np

# Parameters

draw = True
output = True
num_centroids = 5
k = 5
max_window_size = 1000
num_points = 15000
step_size = 1

if __name__ == "__main__":

    i = 0
    centroids = kmeans.initialize(num_centroids, -5, 5)
    x = Stream('x')

    m = KMeans.KMeansStream(draw=draw, output=output, k=k)

    model = Stream_Learn(data_train=x, data_out=x, train_func=m.train,
                         predict_func=m.predict, min_window_size=k,
                         max_window_size=max_window_size, step_size=step_size,
                         num_features=2)
    y = model.run()

    while i < num_points:
        index = np.random.randint(0, num_centroids)
        z = np.random.rand(1, 2) * 2 - 1
        centroids[index] = centroids[index].reshape(1, 2) + z * 2
        x.extend([tuple(kmeans.initializeDataCenter(centroids[index],
                                                    1, 1).tolist()[0])])
        print i
        i += 1

    print "Average number of iterations: ", m.avg_iterations
    print "Average error: ", m.avg_error
