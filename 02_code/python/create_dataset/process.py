import pandas as pd
import numpy as np

# 재현성 고정
np.random.seed(42)

# 데이터 로드
orders = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\orders.csv")
inventory = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\inventory.csv")
mfg = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\00_used_data\hybrid_manufacturing_categorical.csv")


# 공정별 표준 사이클타임
cycle_time_map = (
    mfg.groupby("Operation_Type")["Processing_Time"].mean().round(2).to_dict()
)

# product_id 정의
product_ids = sorted(orders["product_id"].unique())

# material_id 정의
material_ids = sorted(inventory["material_id"].unique())

# 공정 정의
process_master = [
    ("A", 1, "Milling"),
    ("B", 2, "Lathe"),
    ("C", 3, "Drilling"),
    ("D", 4, "Grinding"),
    ("E", 5, "Additive")
]

# 공정별 원자재 필요 수량 범위 정의
required_qty_range = {
    "Milling" : (2, 5),
    "Lathe" : (2, 4),
    "Drilling" : (1, 3),
    "Grinding" : (1, 2),
    "Additive" : (3, 6)
}

# 각 행을 생성
rows = []

for product_id in product_ids:
    # 동일 제품 안에서 원자재 과대 중복 방지
    used_materials = set()

    for process_id, process_step, process_name in process_master:
        # 공정별 원자재 3~5개 사용
        n_materials = np.random.randint(3, 6)

        # 아직 사용하지 않은 원자재를 우선 후보로 사용
        available_materials = [m for m in material_ids if m not in used_materials]

        # 후보 원자재가 부족하다면 전체 원자재에서 다시 선택
        if len(available_materials) < n_materials:
            available_materials = material_ids
        
        # 해당 제품/공정에서 사용할 원자재 선택
        selected_materials = np.random.choice(
            available_materials,
            size=n_materials,
            replace=False
        )

        # 공정별 표준 사이클 타임
        standard_cycle_time = cycle_time_map.get(process_name)

        # 공정별 필요 수량 범위
        qty_low, qty_high = required_qty_range[process_name]

        for material_id in selected_materials: 
            # 현재 제품에서 사용한 원자재 기록
            used_materials.add(material_id)

            # 공정 특성에 맞는 원자재 필요 수량 생성
            required_material_qty = np.random.randint(qty_low, qty_high+1)

            rows.append({
                "product_id" : product_id,
                "process_id" : process_id,
                "material_id" : material_id,
                "process_step" : process_step,
                "process_name" : process_name,
                "required_material_qty" : required_material_qty,
                "standard_cycle_time" : standard_cycle_time
            })

# DataFrame으로 변환
raw_process = pd.DataFrame(rows)

output_path = r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\process.csv"

try:
    raw_process.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("process.csv 생성 완료:", raw_process.shape)
    
except Exception as e:
    print("생성 실패:", e)