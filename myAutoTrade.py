import time
import pyupbit
import datetime
import requests

import upmarketCheck
import bestk

# Access Key 값
access = ""
secret = ""
myToken = ""

# slack 봇 채널 이름
botName = "#bitcoinautotrade"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    # 최근 이틀의 가격 조회
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

def sell_coin(target_coin, btc):
    sell_result = pyupbit.sell_market_order(target_coin, btc * 0.9995) # 시장가 매도
    post_message(myToken, botName, target_coin + " sell : " + str(sell_result))
    # 매도 했으므로 다시 코인을 조회하기 위하여 flag 값 수정
    global flag
    flag = 0

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 시작 메세지 슬랙 전송
post_message(myToken, botName, "autotrade start")

# 오늘의 종목을 검색하기 위한 flag
flag = 0

# 구매한 코인의 가격
buy_cost = 0

# 상승장 리스트
upper_list = []

# 코인 별 최적의 k값(수익률 최대)
bestk_list = []

# 목표 코인과 k값
target = []

# 목표 코인의 k값
target_k_value = 0

# 목표 코인
target_coin = ""

# 코인을 샀을 때의 가격(가격 갱신에도 사용)
buy_cost = 0

# 코인을 샀을 때의 시간
buy_time = 0

# 무한 반복으로 자동 매매 실행
while True:
    try:
        # 처음 진입 or 하루가 지남 or 보유 금액이 5000원 이상(flag = 0) 타겟으로 할 코인과 k값 설정
        if flag == 0:
            flag = 1
            # 상승장 종목 리스트
            upper_list = upmarketCheck.upper_market()
            #print(upper_list)

            # 각 상승장 종목 별 best K 값 구하기
            bestk_list = bestk.get_best_k(upper_list)
            target = bestk.today_coin(bestk_list)
            #print(target)

            # k값
            target_k_value = target[0][1]
            #print(target_k_value)
            # 코인 종목
            target_coin = target[1]
            #print(target_coin)
            print("목표 설정 완료")
        
        # 현재 시간
        now = datetime.datetime.now() 
        
        # 장 시작 시간 (09:00)
        start_time = get_start_time(target_coin)
        
        # 장 마감 시간 (장 시작 시간의 다음날, 09:00)
        end_time = start_time + datetime.timedelta(days=1)

        # 장 시작(09:00)으로 부터 24시간이 지나지 않음(24시간에서 10초를 빼고 계산)
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            print("자동 매매 조건문 진입")
            target_price = get_target_price(target_coin, target_k_value) # 목표코인의 매수 목표 가격
            ma15 = get_ma15(target_coin) # 목표 코인의 15일 이동평균
            current_price = get_current_price(target_coin) # 목표 코인의 현재 가격

            # 매도
            # 보유한 코인이 있으면
            if buy_cost > 0:
                print("현재 코인 소유중")
                # 현재 보유한 코인의 잔액 조회
                btc = get_balance(target_coin)

                # 현재 가격이 구매한 가격의 10% 보다 크고 구매시간으로 부터 1시간 이내라면
                if current_price >= buy_cost * 1.1 and now <= buy_time + datetime.timedelta(hours=1):
                    buy_cost = current_price # 비트코인의 현재가를 가져옴
                    buy_time = now # 현재 시간으로 저장
                    post_message(myToken, botName, target_coin + " 떡상중")
                    '''
                    매수한 비트코인의 가격이 1시간 안에 10%이상 올랐으므로 매도를 진행하지 않고 지켜봄
                    대신 비트코인의 구매가격을 현재 10%이상 오른 가격으로 바꿔줌으로써 하락이 발생할때 매도가능하게 함
                    '''
                    print("코인 떡상중")
                   
                # 현재 가격이 구매한 가격에서 2% 이상 떨어지면
                if current_price <= buy_cost * 0.98:
                    print("코인 매도 조건문 진입")
                    sell_coin(target_coin, btc)
                    print("코인 매도 완료")
                   
            # 매수
            # 매수목표가격보다 현재가격이 높고 15일 이동평균선보다 현재가가 높으면
            if target_price < current_price and ma15 < current_price:
                print("매수 조건문 진입")
                krw = get_balance("KRW") # 현재 잔액 확인(지갑에 든 한화(한국돈))

                # 보유한 현금이 5000원이상(업비트에서 5000원 이상만 결제 가능)
                if krw >= 5000:
                    print("코인 매수 조건문 진입")
                    buy_result = pyupbit.buy_market_order(target_coin, krw * 0.9995) # 시장가 매수
                    buy_cost = buy_result['price'] # 현재 보유한 비트코인의 구매 가격
                    buy_time = datetime.datetime.now() # 비트코인 구매 시간
                    print(target_coin + " 매수 가격 : " + buy_cost)
                    post_message(myToken, botName, target_coin + " buy : " + str(buy_result))
                    print("코인 매수 완료")
        
        # 비트코인을 사고 장마감시간이 되면(하루가 지나면) 가지고 있는 비트코인은 모두 매도
        else:
            print("하루가 지났음")
            # 하루가 지났으므로 다시 타겟을 설정하도록 flag 수정
            btc = get_balance(target_coin) # 매수한 코인의 잔액 조회
            #if btc > 0.00015: # 여기 값 바꿔야 함 코인의 원화 가격이 5000원 이상일때, 근데 항상 10000원 이상씩 가지고 있을텐데 굳이 필요한가? 빼도 될듯함
            # 보유한 비트코인이 있으면
            if btc > 0:
                print("코인 매도 조건문 진입")
                sell_coin(target_coin, btc)
                print("코인 매도 완료")
                
        # 1초 쉬어줌
        time.sleep(1)
    # 에러 발생시 예외 처리
    except Exception as e:
        print(e)
        post_message(myToken, botName, e)
        time.sleep(1)