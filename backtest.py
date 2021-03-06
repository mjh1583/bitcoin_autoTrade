from datetime import datetime
from pprint import pprint
import pyupbit
import numpy as np

# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
# df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=7)
df = pyupbit.get_ohlcv("KRW-BTC", interval="minute1", count=60)

# 변동성 돌파 시준 범위 계산, (고가-저가) * k값
df['range'] = (df['high'] - df['low']) * 0.1

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

fee = 0.0005
# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

# MDD 계산
print("MDD(%): ", df['dd'].max())

# Access Key 값
access = ""
secret = ""

upbit = pyupbit.Upbit(access, secret)
target_coin = "KRW-SBD"
print(target_coin[4:])
balances = upbit.get_balances()
for b in balances:
    if b['currency'] == "SBD":
        if b['balance'] is not None:
            print("잔액 : ", float(b['balance']))
        else:
            print("no money")

# 엑셀로 출력
# df.to_excel("dd.xlsx")
pprint(df)