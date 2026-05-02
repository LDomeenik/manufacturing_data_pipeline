import pandas as pd
import numpy as np

# 재현성 고정
np.random.seed(42)

# 주문 수 고정
N_ORDERS = 5000

# 완제품 수 고정
N_PRODUCTS = 20

# 완제품 ID 생성
product_ids = [f"PRD{str(i).zfill(3)}" for i in range(1, N_PRODUCTS+1)]

# 주문 ID 생성
order_ids = [f"ORD{str(i).zfill(6)}" for i in range(1, N_ORDERS+1)]

# 주문별 제품 랜덤 선택
weights = np.random.dirichlet(np.ones(N_PRODUCTS))

selected_products = np.random.choice(
    product_ids,
    size=N_ORDERS,
    p=weights
)

# 주문 수량 생성
order_qty = np.random.normal(loc=50, scale=20, size=N_ORDERS)
order_qty = order_qty.astype(int)
order_qty = np.clip(order_qty, 5, 150)

# 주문 일자 생성
start_date = pd.to_datetime("2025-08-28")

order_dates = start_date + pd.to_timedelta(
    np.random.randint(0, 100, size=N_ORDERS),
    unit="D"
)

# 납기일 생성
base_lead = np.random.randint(10, 20, size=N_ORDERS)

urgency = np.random.choice(
    [0, -3, -7],
    size=N_ORDERS,
    p=[0.7, 0.2, 0.1]
)

due_dates = order_dates + pd.to_timedelta(base_lead + urgency, unit="D")

# orders 생성
orders = pd.DataFrame({
    "order_id" : order_ids,
    "product_id" : selected_products,
    "order_qty" : order_qty,
    "order_date" : order_dates,
    "due_date" : due_dates
})

# CSV로 내보내기
try:
    orders.to_csv("orders.csv", index=False, encoding="utf-8-sig")
    print("orders.csv 생성 완료:", orders.shape)
    print(orders.head())
except Exception as e:
    print("생성 실패:", e)