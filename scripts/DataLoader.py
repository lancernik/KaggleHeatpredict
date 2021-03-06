import pandas as pd 
import numpy as np
from model_utils import reduce_mem_usage,fill_weather_dataset
from model_utils import find_bad_zeros,find_bad_building1099
from sklearn.preprocessing import LabelEncoder
import gc

"""
    This script consist of all functions that are used in preparring dataset, without 

    using many lines of code. For train set there are performed some basic preparation 

    methods such as mergin different dataset,scaling values that are too large so that 

    they will not have big impact on training process,Encoding categorical feature,

    finding minimal bit representation of features and dropping dataset after merging.

"""
def train_df(build_meta_csv: str, 
        train_csv : str, 
        weather_train_csv : str,
        merge : bool,
        datetime : bool,
        unmerged : bool,
        drop : bool,
        encode_and_scale : bool,
        trim_bad_rows : bool,
        fill_weather : bool,
        col_drop = None,
        axis = None) -> pd.DataFrame:
        # Reading data
        build = pd.read_csv(build_meta_csv)
        train_data = pd.read_csv(train_csv)
        weather = pd.read_csv(weather_train_csv)
        if fill_weather:
            weather = fill_weather_dataset(weather)
        # Reducing memory on the train data
        train = reduce_mem_usage(train_data)
        if merge:
            train = train_data.merge(build,on='building_id',how='left')
            train = train.merge(weather,on=['site_id','timestamp'],how='left')
            del build,weather 
            gc.collect()
        if datetime:
            train['timestamp'] = pd.to_datetime(train['timestamp'])
            train['year'] = train['timestamp'].dt.year.astype(np.uint16)
            train['month'] = train['timestamp'].dt.month.astype(np.uint8)
            train['day'] = train['timestamp'].dt.day.astype(np.uint8)
            train['weekday'] = train['timestamp'].dt.weekday.astype(np.uint8)
            train['hour'] = train['timestamp'].dt.hour.astype(np.uint8)
        if trim_bad_rows:
            bad_zeros = find_bad_zeros(train,train['meter_reading'])
            bad_building = find_bad_building1099(train,train['meter_reading'])
            train = train.drop(bad_zeros) 
            train = train.drop(bad_building)
        if drop:
            train = train.drop(col_drop,axis=axis)
            gc.collect()
        if encode_and_scale: 
            le = LabelEncoder() 
            train['primary_use'] = le.fit(train['primary_use']).transform(train['primary_use'])
            train['meter_reading'] = np.log1p(train['meter_reading'])
            train['square_feet'] = np.log1p(train['square_feet'])
        if unmerged: 
            return build,train,weather
        else: 
            return train

def test_df(test_csv : str, 
        weather_test_csv : str, 
        merge : bool, 
        datetime : bool,
        unmerged : bool,
        drop : bool,
        fill_weather : bool,
        col_drop = None,
        axis = None) -> pd.DataFrame:
        # Reading data 
        test_data = pd.read_csv(test_csv)
        weather_test = pd.read_csv(weather_test_csv)
        if fill_weather: 
            weather = fill_weather_dataset(weather_test)
        # Reducing memory on the test data 
        test = reduce_mem_usage(test_data)
        if merge:
            test = test_data.merge(weather_test,on=['timestamp'],how='left')
            del weather_test
            gc.collect()
        if datetime:
            test['timestamp'] = pd.to_datetime(test['timestamp'])
            test['year'] = test['timestamp'].dt.year.astype(np.uint16)
            test['month'] = test['timestamp'].dt.month.astype(np.uint8)
            test['day'] = test['timestamp'].dt.month.astype(np.uint8)
            test['weekday'] = test['timestamp'].dt.weekday.astype(np.uint8)
            test['hour'] = test['timestamp'].dt.hour.astype(np.uint8)
        if drop:
            test = test.drop(col_drop,axis=axis)
            gc.collect()
        if unmerged: 
            return test,weather_test
        else: 
            return test