import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

TIME_SLEEP = 0.000000001


class Geomap:
    """
    Mapping framework for plotting data onto a map.

    Given latitude - longitude coordinates, this framework allows data to be
    plotted onto a world map with specified region and projection. Data can be
    plotted with different colors as well as labels. Previous data can also be
    cleared.

    Parameters
    ----------
    figsize : tuple
        A tuple containing the width and height of the plot for the map (the
        default is (15, 8)).
    kwargs : keyword arguments
        Keyword arguments. The valid keywords are the keywords for the __init__
        method of Basemap.
    """

    def __init__(self, figsize=(15, 8), **kwargs):
        self._initialize(figsize, **kwargs)

    def _initialize(self, figsize, **kwargs):
        plt.ion()
        self.map = Basemap(**kwargs)
        self.f = plt.figure(figsize=figsize)
        self._draw_map()
        self.f.tight_layout()
        self.pt_sets = []

    def _draw_map(self):
        self.map.drawcoastlines()
        self.map.drawcountries()
        self.map.drawstates()
        self.map.fillcontinents(color='gainsboro', lake_color='grey')
        self.map.drawmapboundary(fill_color='grey')

    def plot(self, x, index=None, text=None, color='Blue', s=30):
        """
        Plots data onto the map.

        This function allows data in the form of latitude-longitude coordinates
        to be plotted on the map. Supports coloring by index or name as well as
        text labels.

        Parameters
        ----------
        x : numpy.ndarray
            A numpy array containing data to be plotted. Dimensions must be
            n * 2, where n is the number of data points. The first column is
            the latitude and the second column is the longitude.
        index : numpy.ndarray or list, optional
            A numpy array or list containing indices for coloring the data.
            Dimensions must be n * 1, where n is the number of data points. If
            not provided, data is colored with `color`.
        text : numpy.ndarray, optional
            A numpy array containing string labels for each data point.
            Dimensions must be n * 1, where n is the number of data points.
        color : string, optional
            A string specifying the color of the data points (the default is
            blue). Used if index is not provided.
        s : int, optional
            An int specifying the size of the data points (the default is 30).
        """

        lat = x[:, 0]
        lon = x[:, 1]
        x_map, y_map = self.map(lon, lat)
        if index is None:
            c = color
        else:
            c = index
        rainbow = plt.get_cmap('rainbow')
        p = self.map.scatter(x_map, y_map, c=c, cmap=rainbow, s=s, zorder=2)
        self.pt_sets.append(p)
        if text is not None:
            for i in range(0, len(x)):
                p = plt.annotate(text[i][0], xy=(x_map[i], y_map[i]),
                                 xytext=(x_map[i] + 0.5, y_map[i] + 0.5),
                                 fontsize=10,
                                 bbox={'facecolor': 'white', 'alpha': 0.5})
                self.pt_sets.append(p)
        plt.pause(TIME_SLEEP)

    def clear(self):
        """
        Clears all plotted data on the map.

        """

        for p in self.pt_sets[:]:
            p.remove()
            self.pt_sets.remove(p)
