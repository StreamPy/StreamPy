if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from ML import Stream_Learn, KMeans, Geomap
from ML.KMeans import kmeans
from Stream import Stream

import requests
import json

def all_func(x, y, model, state, window_state):
    if state is None:
        state = Geomap.Geomap(llcrnrlat = 20, llcrnrlon = -126, urcrnrlat = 60, urcrnrlon = -65)
    state.clear()
    state.plot(x, kmeans.findClosestCentroids(x, model.centroids), s = 70)
    import pdb; pdb.set_trace()
    # state.plot(model.centroids, color = 'Red', s = 50)
    return state


x = Stream('x')

m = KMeans.KMeansStream(draw = False, output = False, k = 5)
model = Stream_Learn(x, x, m.train, m.predict, 5, 30, 1, 2, all_func = all_func)

y = model.run()

r = requests.get('http://stream.meetup.com/2/rsvps', stream=True)

i = 0

for line in r.iter_lines():
    if line:
        data = json.loads(line)
        lat, lon = data['group']['group_lat'], data['group']['group_lon']
        if data['group']['group_country'] == 'us':
            x.extend([(lat, lon)])
            print i
            i += 1
