import pandas as pd
import numpy as np

# 재현성 고정
np.random.seed(42)

# 데이터 로드
orders = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\orders.csv")

log = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\production_log.csv")

defect = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\00_used_data\manufacturing_defect_dataset.csv")

# 필요한 컬럼만 추출
defect_base = defect[[
    "ProductionVolume",
    "ProductionCost",
    "DefectRate",
    "QualityScore",
    "MaintenanceHours",
    "DowntimePercentage"
]].copy()

# 결측 제거
defect_base = defect_base.dropna().reset_index(drop=True)

# 주문 수량 매핑
order_qty_map = orders.set_index("order_id")["order_qty"]

# 공정별 민감도 설정
process_defect_factor = {
    "A" : 1.00,
    "B" : 1.05,
    "C" : 0.90,
    "D" : 1.20,
    "E" : 1.15
}

# 데이터 적재
rows = []

for _, row in log.iterrows():
    order_id = row["order_id"]
    process_id = row["process_id"]

    # 주문 수량을 공정 투입 수량으로 사용
    input_qty = int(order_qty_map[order_id])

    # Defect Dataset에서 1행 샘플링
    sampled = defect_base.sample(n=1).iloc[0]

    # 실제 데이터 기반 값
    sampled_defect = np.random.choice(defect["DefectRate"])
    sampled_defect_rate = sampled_defect / 35
    sampled_quality_score = sampled["QualityScore"]
    sampled_production_cost = sampled["ProductionCost"]
    sampled_maintenance_hours = sampled["MaintenanceHours"]
    sampled_downtime_percentage = sampled["DowntimePercentage"]

    # downtime 영향 반영
    downtime = row["downtime"]

    if downtime < 10:
        downtime_factor = 1.00
    elif downtime < 30:
        downtime_factor = 1.15
    else:
        downtime_factor = 1.35
    
    # 공정별 민감도 반영
    process_factor = process_defect_factor[process_id]

    # 최종 실제 불량률
    actual_defect_rate = (
        sampled_defect_rate * downtime_factor * process_factor * np.random.uniform(0.95, 1.05)
    )

    # 비정상적으로 커지는 값 방지
    actual_defect_rate = np.clip(actual_defect_rate, 0.005, 0.25)
    actual_defect_rate = round(actual_defect_rate, 4)

    # 수량 계산
    defect_qty = int(round(input_qty * actual_defect_rate))
    output_qty = input_qty - defect_qty

    # 품질 점수
    quality_score = (
        sampled_quality_score - (actual_defect_rate * 100 * 0.3) - (downtime * 0.03)
    )

    quality_score = round(np.clip(quality_score, 0, 100), 2)

    # 생산 비용
    production_cost = (
        sampled_production_cost * (input_qty / max(sampled["ProductionVolume"], 1)) + downtime * 2
    )

    production_cost = round(production_cost, 2)

    # 유지보수 시간 / 다운타임 비율
    maintenance_hours = round(
        sampled_maintenance_hours + (downtime * 0.05), 2
    )

    downtime_percentage = round(
        max(
            sampled_downtime_percentage, row["downtime"] / row["actual_work_time"]
        ), 4
    )

    # 결과 상태
    if actual_defect_rate >= 0.15:
        result_status = "Fail"
    elif actual_defect_rate >= 0.08:
        result_status = "Warning"
    else:
        result_status = "Normal"
    
    rows.append({
        "lot_id" : row["lot_id"],
        "process_id" : process_id,
        "order_id" : order_id,
        "product_id" : row["product_id"],
        "input_qty" : input_qty,
        "output_qty" : output_qty,
        "defect_qty" : defect_qty,
        "actual_defect_rate" : actual_defect_rate,
        "quality_score" : quality_score,
        "production_cost" : production_cost,
        "maintenance_hours" : maintenance_hours,
        "downtime_percentage" : downtime_percentage,
        "result_status" : result_status
    })

raw_production_result = pd.DataFrame(rows)

# CSV로 내보내기
output_path = r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\production_result.csv"

try:
    raw_production_result.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("process.csv 생성 완료:", raw_production_result.shape)
    
except Exception as e:
    print("생성 실패:", e)