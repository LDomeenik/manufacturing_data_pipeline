import pandas as pd
import numpy as np

# 재현성 고정
np.random.seed(42)

# 데이터 로드
log = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\production_log.csv")

maintenance = pd.read_csv(r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\00_used_data\predictive_maintenance.csv")

# 실제 센서 컬럼만 추출
sensor_base = maintenance[[
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Type",
    "Target"
]].dropna().reset_index(drop=True)

# 공정별 센서 보정값
process_sensor_factor = {
    "A" : {
        "temp" : 1.02,
        "speed" : 1.05,
        "torque" : 1.00,
        "vibration" : (0.20, 0.50),
        "pressure" : (3.0, 5.0),
        "load" : (50, 80)
    },
    "B" : {
        "temp" : 1.01,
        "speed" : 0.95,
        "torque" : 1.10,
        "vibration" : (0.25, 0.55),
        "pressure" : (3.5, 5.5),
        "load" : (55, 85)
    },
    "C" : {
        "temp" : 1.00,
        "speed" : 1.10,
        "torque" : 0.90,
        "vibration" : (0.15, 0.40),
        "pressure" : (2.5, 4.5),
        "load" : (40, 70)
    },
    "D" : {
        "temp" : 1.03,
        "speed" : 1.00,
        "torque" : 1.15,
        "vibration" : (0.40, 0.80),
        "pressure" : (4.0, 6.5),
        "load" : (65, 95)
    },
    "E" : {
        "temp" : 1.04,
        "speed" : 0.85,
        "torque" : 1.05,
        "vibration" : (0.20, 0.45),
        "pressure" : (3.0, 5.0),
        "load" : (60, 90)
    }
}

# 설비 Type별 보정값
type_factor = {
    "L" : 1.10,
    "M" : 1.00,
    "H" : 0.90
}

# production_log 기준 센서 데이터 생성
rows = []

for _, row in log.iterrows():
    process_id = row["process_id"]
    factor = process_sensor_factor[process_id]

    # Precitive Maintenance Dataset에서 1행 샘플링
    sampled = sensor_base.sample(n=1).iloc[0]

    machine_type = sampled["Type"]
    machine_type_factor = type_factor.get(machine_type, 1.0)

    downtime = row["downtime"]

    # downtime이 클수록 센서값 불안정
    if downtime < 10:
        abnormal_factor = 1.00
    elif downtime < 30:
        abnormal_factor = 1.03
    else:
        abnormal_factor = 1.08
    
    # 실제 데이터 기반 센서값 + 공정/Type/downtime 보정
    air_temperature = sampled["Air temperature [K]"] * factor["temp"]

    process_temperature = (
        sampled["Process temperature [K]"] * factor["temp"] * abnormal_factor * machine_type_factor
    )

    rotational_speed = (
        sampled["Rotational speed [rpm]"] * factor["speed"] * abnormal_factor * machine_type_factor
    )

    torque = (
        sampled["Torque [Nm]"] * factor["torque"] * abnormal_factor * machine_type_factor
    )

    tool_wear = int(sampled["Tool wear [min]"] * machine_type_factor)

    # 데이터셋에 없는 센서값은 공정별 기준 범위로 생성
    vibration_low, vibration_high = factor["vibration"]
    pressure_low, pressure_high = factor["pressure"]
    load_low, load_high = factor["load"]

    vibration = (
        np.random.uniform(vibration_low, vibration_high) * abnormal_factor * machine_type_factor
    )

    pressure = (
        np.random.uniform(pressure_low, pressure_high) * abnormal_factor
    )

    load = (
        np.random.uniform(load_low, load_high) * abnormal_factor * machine_type_factor
    )

    coolant_temperature = process_temperature - np.random.uniform(8, 15)
    motor_temperature = process_temperature + np.random.uniform(5, 12)
    tool_temperature = process_temperature + np.random.uniform(3, 10)
    tool_vibration = vibration * np.random.uniform(1.1, 1.5)

    machine_age = np.random.randint(1, 11)
    maintenance_cycle = np.random.randint(30, 181)
    humidity = np.random.uniform(30, 70)

    power_consumption = (
        (torque * rotational_speed) / 1000 * np.random.uniform(0.8, 1.2)
    )

    voltage = np.random.uniform(210, 240)

    # 실제 Target 사용 + downtime이 큰 경우 이상 가능성 보정
    failure_target = int(sampled["Target"])

    if downtime >= 35 and np.random.rand() < 0.35:
        failure_target = 1
    
    rows.append({
        "lot_id" : row["lot_id"],
        "process_id" : process_id,
        "machine_id" : row["machine_id"],
        "machine_type" : machine_type,
        "air_temperature" : round(air_temperature, 2),
        "process_temperature" : round(process_temperature, 2),
        "coolant_temperature" : round(coolant_temperature, 2),
        "motor_temperature" : round(motor_temperature, 2),
        "rotational_speed" : round(rotational_speed, 2),
        "torque" : round(torque, 2),
        "vibration" : round(vibration, 4),
        "pressure" : round(pressure, 2),
        "load" : round(load, 2),
        "tool_wear" : tool_wear,
        "tool_temperature" : round(tool_temperature, 2),
        "tool_vibration" : round(tool_vibration, 4),
        "machine_age" : machine_age,
        "maintenance_cycle" : maintenance_cycle,
        "humidity" : round(humidity, 2),
        "power_consumption" : round(power_consumption, 2),
        "voltage" : round(voltage, 2),
        "failure_target" : failure_target
    })

raw_machine_sensor = pd.DataFrame(rows)

# CSV로 내보내기
output_path = r"C:\Users\jydom\OneDrive\문서\Project\manufacturing\00_data\01_raw_data\machine_sensor.csv"

try:
    raw_machine_sensor.to_csv(output_path, index=False, encoding='utf-8-sig')
    print("process.csv 생성 완료:", raw_machine_sensor.shape)
    
except Exception as e:
    print("생성 실패:", e)