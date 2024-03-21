from __future__ import annotations
from datetime import time
from pandas import DataFrame as df
from pandas import read_csv
from pandas import concat
import pandas as pd
import numpy as np
from statsmodels.tsa.ar_model import AutoReg
from typing import TypeVar
T = TypeVar('T')

import queue
import threading

class MessageQueue(object):
    def __init__(self, max_local_data_table_size: int, disk_file: str):
        self.current_data = None
        self.earliest_timestamp = 0
        self.latest_timestamp = 0
        self.max_local_data_table_size = max_local_data_table_size
        self.filepath = disk_file

        self.mq = queue.Queue()

        self.lock = threading.Lock()
    
    def offer(self, timestamp: float, data: dict[str, T]):
        data['timestamp'] = timestamp

        self.lock.acquire()
        self.mq.put(data)
        self.lock.release()

    
    # TODO: put data into disk after each poll or other technique
    def poll(self):
        self.lock.acquire()
        if self.mq.empty():
            self.lock.release()
            return None

        data = self.mq.get()

        self.lock.release()

        self.log_data_to_disk(data)
        return data
    
    def empty(self):
        return self.mq.empty()

    def clear_csv_file(self):
        with open(self.filepath, 'w') as f:
            f.write('')
    
    def split_table(self, split_size: int=2):
        # store first 1/split_size of current data
        split_tables = np.array_split(self.current_data, split_size)
        new_current_data = None
        for table in split_tables[1:]:
            if new_current_data is None:
                new_current_data = table
            else:
                new_current_data = np.concatenate(new_current_data, table)
        self.current_data = new_current_data

        values_to_store = split_tables[0]
        try:
            old_values = read_csv(self.filepath, header=0, index_col=0, encoding='utf-8')
            # old_values = old_values.append(values_to_store, ignore_index=True)
            # old_values = pd.concat([old_values, pd.DataFrame([values_to_store])], ignore_index=True)
            old_values = pd.concat([old_values, values_to_store], ignore_index=True)
        except:
            old_values = values_to_store
        old_values.to_csv(self.filepath)

        # update earliest timestamp
        self.earliest_timestamp = self.current_data['timestamp'].iloc[0]

    # def log_data(self, timestamp: float, data: dict[str, T]):
    def log_data_to_disk(self, data: dict[str, T]):
        # data['timestamp'] = timestamp
        # print("Enter log_data_to_disk")
        timestamp = data['timestamp']
        new_data = df.from_dict(data, orient="columns")

        cols = new_data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        new_data = new_data[cols]
        
        self.earliest_timestamp = timestamp
        self.latest_timestamp = timestamp
        self.current_data = new_data
        if (self.current_data is None):
            self.earliest_timestamp = timestamp
            self.latest_timestamp = timestamp
            self.current_data = new_data
        else:
            # self.current_data = self.current_data.append(new_data, ignore_index=True)
            # self.current_data = pd.concat([self.current_data, pd.DataFrame([new_data])], ignore_index=True)
            self.current_data = pd.concat([self.current_data, new_data], ignore_index=True)

            self.latest_timestamp = timestamp
            if (len(self.current_data.index) > self.max_local_data_table_size):
                self.split_table()
        
        # print(self.current_data)
        new_data.to_csv(self.filepath, mode="a", header=False, index=False)
        
    def get_data_from_disk(self, start_timestamp, end_timestamp):
        current_filtered_values = self.current_data[(self.current_data['timestamp'] >= start_timestamp) & (self.current_data['timestamp'] <= end_timestamp)]
        if start_timestamp < self.earliest_timestamp:
            old_values = read_csv(self.filepath, header=0, index_col=0)
            filtered_values = old_values[(old_values['timestamp'] >= start_timestamp) & (old_values['timestamp'] <= end_timestamp)]
            # current_filtered_values = filtered_values.append(current_filtered_values, ignore_index=True)
            # current_filtered_values = pd.concat([current_filtered_values, pd.DataFrame([current_filtered_values])], ignore_index=True)
            current_filtered_values = pd.concat([filtered_values, current_filtered_values], ignore_index=True)
        return current_filtered_values # returns dataframe object w filtered data between timestamps

    # def get_prediction(self, target_timestamp):
    #     data = self.current_data.data
    #     model_fit = AutoReg(data, lags=1).fit()
    #     return model_fit.predict(start=target_timestamp, end=target_timestamp+1)


# # mq = MessageQueue(4, r"./mq_test.csv")
# mq = MessageQueue(4, r"/home/wangzhe/Desktop/CS525/SpotAlloc/Models/mq_test.csv")
# mq.offer(1, {"load": [10], "utility":[100]})
# mq.offer(1, {"load": [10], "utility":[100]})
# mq.offer(2, {"load": [20], "utility":[200]})
# mq.offer(3, {"load": [30], "utility":[300]})
# mq.offer(4, {"load": [40], "utility":[400]})
# mq.offer(5, {"load": [50], "utility":[500]})

# data = mq.poll()
# print(data)

# data = mq.poll()
# print(data)

# data = mq.poll()
# print(data)

# mq.clear_csv_file()

# data = mq.poll()
# print(data)