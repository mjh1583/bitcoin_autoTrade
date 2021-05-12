import time
import pyupbit
import datetime
import requests

import upmarketCheck
import bestk

access = ""
secret = ""
myToken = ""

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = pyupbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#bitcoinautotrade", "autotrade start")

# 오늘의 종목을 검색하기 위한 flag
flag = 0

# 구매한 코인의 가격
buy_cost = 0

while True:
    try:
        if flag == 0:
            flag = 1
            # 상승장 종목 리스트
            upper_list = upmarketCheck.upper_market()
            # print(upper_list)

            # 각 상승장 종목 별 best K 값 구하기
            bestk_list = bestk.get_best_k(upper_list)
            target = bestk.today_coin(bestk_list)
            # print(target)

            # k값
            target_k_value = target[1]
            # 코인 종목
            target_coin = target[2]
        
        # 현재 시간
        now = datetime.datetime.now() 
        # 장 시작 시간
        start_time = get_start_time(target_coin)
        # 장 마감 시간
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(target_coin, target_k_value)
            ma15 = get_ma15(target_coin)
            current_price = get_current_price(target_coin)
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = pyupbit.buy_market_order(target_coin, krw * 0.9995) # 시장가 매수
                    buy_cost = buy_result['price']
                    post_message(myToken,"#bitcoinautotrade", target_coin + " buy : " +str(buy_result))
        else:
            # 하루가 지났으므로 다시 타겟을 설정하도록 flag 수정
            flag = 0
            btc = get_balance(target_coin)
            if btc > 0.00015: # 여기 값 바꿔야 함 코인의 원화 가격이 5000원 이상일때, 근데 항상 10000원 이상씩 가지고 있을텐데 굳이 필요한가? 빼도 될듯함
                sell_result = pyupbit.sell_market_order(target_coin, btc * 0.9995) # 시장가 매도
                post_message(myToken,"#bitcoinautotrade", target_coin + " sell : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#bitcoinautotrade", e)
        time.sleep(1)