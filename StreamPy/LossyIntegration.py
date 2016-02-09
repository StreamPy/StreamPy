import numpy as np

def lossy_integration(data, initial_value, FACTOR):
    data[0] -= initial_value * FACTOR
    for i in range(1, np.shape(data)[0]):
        data[i] -= data[i-1]*FACTOR
    return data


def main():
    """For input:
          data=[2, 5, 8, 11, 14, 17, ...],
          initial_value=2,
       the expected output is:
          [ 2  4  6  8 10 12 ....]

    """
    print lossy_integration(
        data=np.array([2, 5, 8, 11, 14, 17]),
        initial_value=0,
        FACTOR=0.5)

if __name__ == '__main__':
    main()
    

