import pandas as pd
import numpy as np

# 재현성 고정
np.random.seed(42)

# 데이터 로드
orders = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\orders.csv")
process = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\process.csv")

# 공정 기준 정보
process_master = (
    process[[
        "product_id",
        "process_id",
        "process_step",
        "standard_cycle_time",
        "process_name"
    ]]
    .drop_duplicates()
    .sort_values(["product_id", "process_step"])
)

# 공정별 설비 정의
machine_pool = {
    "A" : ["MILL_01", "MILL_02", "MILL_03", "MILL_04"],
    "B" : ["LATHE_01", "LATHE_02", "LATHE_03"],
    "C" : ["DRILL_01", "DRILL_02"],
    "D" : ["GRIND_01"],
    "E" : ["ADD_01", "ADD_02"]
}

# 공정별 setup_time 범위
setup_time_range = {
    "Milling" : (10, 25),
    "Lathe" : (8, 20),
    "Drilling" : (5, 15),
    "Grinding" : (5, 10),
    "Additive" : (15, 30)
}

# production_log 생성
rows = []

for idx, order in orders.iterrows():
    order_id = order["order_id"]
    product_id = order["product_id"]

    lot_id = f"LOT{str(idx + 1).zfill(6)}"

    product_processes = process_master[
        process_master["product_id"] == product_id
    ]

    for _, proc in product_processes.iterrows():
        process_id = proc["process_id"]
        process_name = proc["process_name"]
        standard_cycle_time = proc["standard_cycle_time"]

        # 설비 배정
        machine_id = np.random.choice(machine_pool[process_id])

        # setup_time
        low, high = setup_time_range[process_name]
        setup_time = round(np.random.uniform(low, high), 2)

        # downtime
        downtime = np.random.choice(
            [
                np.random.uniform(0, 10),
                np.random.uniform(10, 50)
            ],
            p=[0.85, 0.15]
        )
        downtime = round(downtime, 2)

        # actual_work_time
        actual_work_time = (
            standard_cycle_time * np.random.uniform(0.9, 1.2) + setup_time + downtime
        )
        actual_work_time = round(actual_work_time, 2)

        # job_status
        if downtime >= 30 or actual_work_time >= standard_cycle_time * 1.45:
            job_status = "Delayed"
        else:
            job_status = "Completed"
        
        rows.append({
            "lot_id" : lot_id,
            "process_id" : process_id,
            "order_id" : order_id,
            "product_id" : product_id,
            "machine_id" : machine_id,
            "actual_work_time" : actual_work_time,
            "setup_time" : setup_time,
            "downtime" : downtime,
            "job_status" : job_status
        })

raw_production_log = pd.DataFrame(rows)

# CSV로 내보내기
output_path = output_path = r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\production_log.csv"

try:
    raw_production_log.to_csv(output_path, index=False, encoding="utf-8-sig")
    print("process.csv 생성 완료:", raw_production_log.shape)
    
except Exception as e:
    print("생성 실패:", e)