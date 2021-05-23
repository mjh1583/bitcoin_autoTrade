import pyupbit
import numpy as np
import time
from pprint import pprint

# def get_ror(k):
#     df = pyupbit.get_ohlcv("KRW-SOLVE", count=7)
#     df['range'] = (df['high'] - df['low']) * k
#     df['target'] = df['open'] + df['range'].shift(1)

#     fee = 0.0005
#     df['ror'] = np.where(df['high'] > df['target'],
#                          df['close'] / df['target'] - fee,
#                          1)

#     ror = df['ror'].cumprod()[-2]
#     return ror

# for k in np.arange(0.1, 1.0, 0.1):
#     ror = get_ror(k)
#     print("%.1f %.6f" % (k, ror))

# k값에 대한 수익률 반환 함수
def get_ror(ticker, k):
    df = pyupbit.get_ohlcv(ticker, count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

# 최적의 k값을 구하는 함수
def get_best_k(upper_list):
    rors = []
    bestk_list = []

    for ticker in upper_list:
        for k in np.arange(0.1, 1.0, 0.1):
            ror = get_ror(ticker, k)
            rors.append([ror, k])
        sorted_rors = sorted(rors, key=lambda x:x[0], reverse=True)
        #pprint(sorted_rors)
        bestk_list.append([sorted_rors[0], ticker])
        rors = []
        time.sleep(1)
    
    #pprint(bestk_list)
    return bestk_list
    
# 가장 좋은 수익률을 가지는 코인 종류와 k값 찾아 반환
def today_coin(bestk_list):
    sorted_bestk_list = sorted(bestk_list, key=lambda x:x[0], reverse=True)
    #pprint(sorted_bestk_list)
    target = sorted_bestk_list[0]
    #print(target)
    return target
            
# upper_list = ["KRW-EMC2", "KRW-SOLVE", "KRW-DOGE"]
# bestk_list = get_best_k(upper_list)
# today_coin(bestk_list)