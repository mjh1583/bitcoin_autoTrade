import pyupbit

# 로그인
access = "bpuqrdNfkU6Z9jCDdfS7RxBj5xZsLtxVmpAuv4L6"          # 본인 값으로 변경
secret = "QjEuvoNnZ9MABI1HHYvFEpcxSeKOjb6JIUnih5Z6"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

# 잔고조회
print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회