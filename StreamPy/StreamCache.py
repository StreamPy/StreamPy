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
        self.end = 0
        self.stream = stream
    
    def find_max_end(self):
        start = 0
        end = 0
        for key in self.start:
            if self.start[key] > end:
                start = key
                end = self.start[key]
        return start, end

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
        self.recent_dict[(start, end)][self.end] = value
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
            self.recent_dict[(start, end)][self.end:self.end + num_values_write] = values[values_start:values_start + num_values_write]
            num_values -= num_values_write
            self.end += num_values_write

            if num_values > 0:
                self.create_slice(end + 1, end + SECTOR_SIZE)
                start, end = end + 1, end + SECTOR_SIZE
                self.end = 0
                values_start += num_values_write

    def get_slice(self, start, end):
        if (start, end) in self.recent_dict:
            return (start, end, self.recent_dict[(start, end)])
        data = []
        f_start = self.find_max_start_before(start)
        cur_start = f_start
        while cur_start <= end:
            if cur_start in self.start:
                f_end = self.start[cur_start]
                data += self.recent_dict[(cur_start, f_end)]
                del self.recent_dict[(cur_start, f_end)]
                del self.start[cur_start]
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
        
        self.recent_dict[(f_start, f_end)] = data
        self.start[f_start] = f_end
        self.num_slices = len(self.recent_dict)
        return (f_start, f_end, data)

    def create_slice(self, start, end):
        if self.num_slices == self.max_slices:
            self.evict()
        size = end - start + 1
        self.recent_dict[(start, end)] = [0] * size
        self.start[start] = end
        self.num_slices += 1
        self.end = 0
        return self.recent_dict[(start, end)]

    def evict(self):
        begin = self.stream.get_begin()
        for key in self.recent_dict:
            start, end = key
            if end < begin:
                del self.recent_dict[key]
                del self.start[start]
                self.num_slices -= 1
                return
        slice_info = self.recent_dict.popitem()
        start = slice_info[0][0]
        del self.start[start]
        self.write_to_file(slice_info)
        self.num_slices -= 1
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
