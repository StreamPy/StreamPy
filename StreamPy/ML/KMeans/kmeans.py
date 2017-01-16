import numpy as np
import matplotlib.pyplot as plt
import random

TIME_SLEEP = 0.000000001


def initialize(k, low, high):
    """Returns k random points with x and y coordinates in [low, high).

    Parameters
    ----------
    k : int
        The number of points to return.
    low : int
        The lower bound (inclusive) for a point.
    high : int
        The upper bound (exclusive) for a point.

    Returns
    -------
    centroids : numpy.ndarray
        Numpy array with dimensions `k` by 2.

    """
    centroids = np.random.rand(k, 2) * (high - low) + low
    return centroids


def initializeCentroids(X, k):
    """Returns k random points from the data `X` without replacement.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with dimensions n * 2, where n >= `k`.
    k : int
        The number of points to return

    Returns
    -------
    numpy.ndarray
        Numpy array with dimensions `k` by 2.

    """
    index = random.sample(xrange(0, len(X)), k)
    return X[index, :]


def findClosestCentroids(X, centroids):
    """
    Returns a numpy array containing the index of the closest centroid for
    each point in X.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with 2 columns.
    centroids : numpy.ndarray
        A numpy array with 2 columns.

    Returns
    -------
    index : numpy.ndarray
        A numpy array with dimensions n * 1, where n is the number of rows in
        `X`. For each row i in `index`, index[i] is in [0, k) where k is the
        number of rows in `centroids`.

    """
    index = np.array([np.argmin([np.dot(x_i - y_k, x_i - y_k)
                                 for y_k in centroids])
                      for x_i in X])
    return index


def computeCentroids(X, index, k):
    """
    Finds the centroids for the data given the index of the closest centroid
    for each data point.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with dimensions n * 2 for some integer n.
    index : numpy.ndarray
        A numpy array with dimensions n * 1 that describes the closest centroid
        to each point in `X`.
    k : int
        Describes the number of centroids. k - 1 is the maximum value that
        appears in `index`.

    Returns
    -------
    centroids : numpy.ndarray
        A numpy array with dimensions `k` * 2.

    Notes
    -----
    The centroids are computed by taking the mean of each group of points in
    `X` with the same index value. For i in [0, k), centroids[i] is the mean
    of all data points X[j] where index[j] is i.

    """
    centroids = np.zeros((k, 2))

    for i in range(0, k):
        idx = np.where(index == i)[0]
        if len(idx) != 0:
            data = X[idx, :]
            centroids[i, :] = np.mean(data, 0)

    return centroids


def kmeans(X, k, initial_centroids=None, draw=False, output=False):
    """Runs kmeans until clusters stop moving.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with 2 columns.
    k : int
        Describes the number of centroids.
    initial_centroids : numpy.ndarray, optional
        A numpy array with initial centroids to run the algorithm. This array
        has with dimensions `k` * 2. If not provided, algorithm is initialized
        with random centroids from the data `X`.
    draw : boolean, optional
        Describes whether the data is to be plotted (data must have 2 or less
        dimensions). The default is False.
    output : boolean, optional
        Describes whether debug info is to be printed (the default is False).
        Info includes current number of iterations and number of changed points
        over time.

    Returns
    -------
    centroids : numpy.ndarray
        Numpy array with learned centroids (dimensions are `k` * 2).
    index : numpy.ndarray
        Numpy array with dimensions n * 1, where n is the number of rows in
        `X`. Each value describes the closest centroid to each data point in
        `X`.
    num_iters : int
        Describes the number of iterations taken to run kmeans.

    """

    num_iters = 0
    # Use initial centroids if provided
    if initial_centroids is not None:
        centroids = initial_centroids
    # Set initial centroids to random
    else:
        centroids = initializeCentroids(X, k)

    previous = centroids
    index = np.zeros((len(X), 1))
    previous_index = np.zeros((len(X), 1))

    while True:
        index = findClosestCentroids(X, centroids)
        # If no points have been reassigned, the centroids will not move and we
        # are done
        if np.array_equal(index, previous_index):
            break

        # Print number of points reassigned
        if num_iters != 0 and output:
            print np.count_nonzero(index - previous_index),\
                " data points changed color"
        previous_index = index
        if draw:
            plotKMeans(X, centroids, previous, index)

        previous = centroids
        centroids = computeCentroids(X, index, k)

        num_iters += 1

    if output:
        print "Num iters: ", num_iters
    return [centroids, index, num_iters]


def initializeDataCenter(centroid, scale, n):
    """
    Initialize n points with a normal distribution and scale around a
    centroid.

    Parameters
    ----------
    centroid : numpy.ndarray
        Numpy array with dimensions 1 * 2.
    scale : int
        Describes the scale for the distribution.
    n : int
        Describes the number of points to make.

    Returns
    -------
    X : numpy.ndarray
        A numpy array with dimensions `n` * 2.

    """
    X = np.random.normal(centroid, scale=scale, size=(n, 2))
    return X


def initializeData(n, k, scale, low, high):
    """
    Initialize n points around k random centroids each with a normal
    distribution and scale.

    Parameters
    ----------
    n : int
        Describes the numbe of points to make around each centroid.
    k : int
        Describes the number of centroids.
    scale : int
        Describes the scale for the distribution.
    low : int
        The lower bound (inclusive) for a centroid.
    high : int
        The upper bound (exclusive) for a centroid.

    Returns
    -------
    X : numpy.ndarray
        A numpy array with dimensions (`n` * `k`) * 2.

    """
    centroids = initialize(k, low, high)

    for i in range(0, len(centroids)):
        if i == 0:
            X = initializeDataCenter(centroids[i], scale, n)
        else:
            X = np.vstack((X, initializeDataCenter(centroids[i], scale, n)))

    return X


def _plotData(X, index, k):
    rainbow = plt.get_cmap('rainbow')
    plt.scatter(X[:, 0], X[:, 1], c=index, cmap=rainbow)


def plotKMeans(X, centroids, previous, index):
    """Plots the data and centroids.

    This function plots the data with the current centroids and shows the
    movement of the centroids.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with 2 columns.
    centroids : numpy.ndarray
        A numpy array with 2 columns.
    previous : numpy.ndarray
        A numpy array with 2 columns and the same number of rows as
        `centroids`.
    index : numpy.ndarray
        A numpy array with 1 column.

    """

    k = len(centroids)
    plt.clf()
    _plotData(X, index, k)
    plt.scatter(centroids[:, 0], centroids[:, 1], 20)

    for i in range(0, k):
        plt.plot((centroids[i, 0], previous[i, 0]), (centroids[i, 1],
                 previous[i, 1]), color='black')
    plt.pause(TIME_SLEEP)


def init_plot(figsize=(15, 8)):
    """Initializes the plot.

    Parameters
    ----------
    figsize : tuple, optional
        A tuple containing the width and height of the plot (the default is
        (15, 8)).

    """
    plt.ion()
    f = plt.figure(figsize=figsize)
    plt.show()


def evaluate_error(X, centroids, index):
    """Returns the mean squared error.

    Parameters
    ----------
    X : numpy.ndarray
        A numpy array with 2 columns.
    centroids : numpy.ndarray
        A numpy array with 2 columns.
    index : numpy.ndarray
        A numpy array with 1 column.

    Returns
    -------
    float
        The mean squared error.

    Notes
    -----
    The mean squared error is calculated as the average squared distance of
    each point from the closest centroid.

    """
    s = 0
    for i in range(0, len(X)):
        centroid_index = index[i]
        s += np.dot(X[i] - centroids[centroid_index], X[i] -
                    centroids[centroid_index])

    return float(s) / X.shape[0]
