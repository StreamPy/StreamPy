import sys
import os
import pickle

SECTOR_SIZE = 10

class StreamCache:

    def __init__(self, stream, num_slices):
        self.recent_dict = {}
        self.num_slices = 0
        self.max_slices = num_slices
        self.files = {}
        self.start = {}
        self.slice_ids = range(0, num_slices)
        self.end = 0
        self.stream = stream
    
    def find_max_end(self):
        start = 0
        max_end = 0
        for key in self.start:
            end, slice_id = self.start[key]
            if end > max_end:
                start = key
                max_end = end
        return start, max_end

    def find_min_start(self):
        start = None
        for key in self.start:
            if start is None or key <= start:
                start = key
        return start

    def find_min_start_except(self, start):
        min_start = None
        for key in self.start:
            if key != start and (min_start is None or key < min_start):
                min_start = key
        return min_start

    def find_max_start_before(self, start):
        max_start = 0
        for key in self.start:
            if key == start:
                return key
            elif key > max_start and key <= start:
                max_start = key
        for key in self.files:
            if key == start:
                return key
            elif key > max_start and key <= start:
                max_start = key
        return max_start

    def append(self, value):
        if self.num_slices == 0:
            self.create_slice(0, SECTOR_SIZE)
        start, end = self.find_max_end()
        if self.end > end - start:
            self.create_slice(end + 1, end + SECTOR_SIZE)
            start, end = end + 1, end + SECTOR_SIZE
            self.end = 0
        slice_id = self.start[start][1]
        self.recent_dict[slice_id][self.end] = value
        self.end += 1

    def extend(self, values):
        if self.num_slices == 0:
            self.create_slice(0, SECTOR_SIZE)
        start, end = self.find_max_end()
        num_values = len(values)
        values_start = 0
        while num_values != 0:
            num_indices = end - (self.end + start) + 1
            num_values_write = min(num_indices, num_values)
            slice_id = self.start[start][1]
            self.recent_dict[slice_id][self.end:self.end + num_values_write] = values[values_start:values_start + num_values_write]
            num_values -= num_values_write
            self.end += num_values_write

            if num_values > 0:
                self.create_slice(end + 1, end + SECTOR_SIZE)
                start, end = end + 1, end + SECTOR_SIZE
                self.end = 0
                values_start += num_values_write

    def get_slice(self, start, end):

        data = []
        f_start = self.find_max_start_before(start)
        cur_start = f_start
        while cur_start <= end:
            if cur_start in self.start:
                f_end, slice_id = self.start[cur_start]
                data += self.recent_dict[slice_id]
                del self.recent_dict[slice_id]
                del self.start[cur_start]
                self.slice_ids.append(slice_id)
                if f_end >= end:
                    break
                else:
                    cur_start = f_end + 1
            else:
                f_end = self.files[cur_start]
                f_data = self.read_from_file(cur_start)
                data += f_data
                if f_end >= end:
                    break
                else:
                   cur_start = f_end + 1 
        while len(self.recent_dict) >= self.max_slices:
            self.evict_except(f_start)

        slice_id = self.get_next_slice_id()
        self.recent_dict[slice_id] = data
        self.start[f_start] = f_end, slice_id
        self.num_slices = len(self.recent_dict)
        return (f_start, f_end, data)

    def create_slice(self, start, end):
        if self.num_slices == self.max_slices:
            self.evict()
        size = end - start + 1
        slice_id = self.get_next_slice_id()
        self.recent_dict[slice_id] = [0] * size
        self.start[start] = end, slice_id
        self.num_slices += 1
        self.end = 0
        return self.recent_dict[slice_id]

    def evict(self):
        begin = self.stream.get_begin()
        min_start = self.find_min_start()
        end, slice_id = self.start[min_start]
        data = self.recent_dict[slice_id]
        del self.recent_dict[slice_id]
        del self.start[min_start]
        self.slice_ids.append(slice_id)
        self.num_slices -= 1

        if end >= begin:
            self.write_to_file(((min_start, end), data))
        return

    def evict_except(self, start):
        begin = self.stream.get_begin()
        min_start = self.find_min_start_except(start)
        end, slice_id = self.start[min_start]
        data = self.recent_dict[slice_id]
        del self.recent_dict[slice_id]
        del self.start[min_start]
        self.slice_ids.append(slice_id)
        self.num_slices -= 1

        if end >= begin:
            self.write_to_file(((min_start, end), data))
        return

    def write_to_file(self, slice_info):
        (start, end), data = slice_info
        filename = "{0}_{1}.data".format(start, end)
        with open(filename, 'w') as f:
            pickle.dump(data, f)
        self.files[start] = end

    def read_from_file(self, start):
        filename = "{0}_{1}.data".format(start, self.files[start])
        with open(filename, 'r') as f:
            data = pickle.load(f)
        os.remove(filename)
        del self.files[start]
        return data

    def update_indices(self):
        min_start = self.find_min_start()         

    def get_next_slice_id(self):
        return self.slice_ids.pop()
