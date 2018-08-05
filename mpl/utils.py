
from builtins import range

from numpy import isnan


def valid_intervals(values_array_1d):
    
    if values_array_1d.ndim != 1:
        raise Exception("Valid interval value ndim not 1")

    if values_array_1d.shape[0] <= 0:
        raise Exception("Valid interval value shape first element not positive")

    valid_list = []
    interval = []
    for i in range(values_array_1d.shape[0]):
        if isnan(values_array_1d[i]):
            if len(interval) > 0: 
                valid_list.append(interval)
                interval = []
        else:
            interval.append(i)
    else:
        if len(interval) > 0:
            valid_list.append(interval)
     
    intdict_list = []       
    for interval in valid_list:
        if len(interval) > 1:
            int_dict = dict(start= interval[0], end = interval[-1])
            intdict_list.append(int_dict)
            
    return intdict_list  
