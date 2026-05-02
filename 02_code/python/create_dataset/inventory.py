"""

"""


# 데이터 로드
import pandas as pd

df = pd.read_csv("supply_chain_data.csv")

df.head()

# 필요 컬럼
df = df[[
    "SKU",
    "Price",
    "Stock levels",
    "Order quantities",
    "Lead time",
    "Manufacturing costs"
]]

df.head()

# 컬럼명 변경
df = df.rename(columns={
    "SKU" : "material_id",
    "Product type" : "material_type",
    "Price" : "unit_price",
    "Stock levels" : "stock_qty",
    "Order quantities" : "incoming_qty",
    "Lead time" : "lead_time",
    "Manufacturing costs" : "manufacturing_cost"
})

df.head()

# PK 타입 정리
df["material_id"] = df["material_id"].astype(str)

# CSV로 내보내기
try:
    df.to_csv("inventory.csv", index=False)
    print("inventory.csv 생성 완료:", df.shape)
    
except Exception as e:
    print("생성 실패:", e)