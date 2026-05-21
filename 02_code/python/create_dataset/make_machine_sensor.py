"""
make_machine_sensor.py

데이터 명세서 기준 raw_machine_sensor.csv 생성 스크립트

기능:
    - production_log.csv 기준 unit 단위 설비 센서 데이터 생성
    - process.csv의 standard_cycle_time을 활용해 lot/process별 unit 수 추정
    - Predictive Maintenance Dataset 기반 machine_id별 센서 기준값 생성
    - machine_id 장기 누적 시계열성 반영
    - lot 내부 단기 시계열성 반영
    - 센서 위험도, downtime, lot 진행률 기반 failure_target 생성
    - raw_machine_sensor.csv 저장
"""


import pandas as pd
import numpy as np
from pathlib import Path


# 기준 설정
RANDOM_SEED = 42

PRODUCTION_LOG_PATH = Path("00_data/01_raw_data/production_log.csv")
PROCESS_PATH = Path("00_data/01_raw_data/process.csv")
MAINTENANCE_PATH = Path("00_data/00_used_data/predictive_maintenance.csv")
OUTPUT_PATH = Path("00_data/01_raw_data/machine_sensor.csv")


# make_machine_sensor: raw_machine_sensor 데이터 생성
def make_machine_sensor(
        production_log_path: Path,
        process_path: Path,
        maintenance_path: Path,
        output_path: Path
) -> pd.DataFrame:
    """
    raw_machine_sensor 데이터를 생성하고 CSV로 저장합니다.

    Args:
        production_log_path (Path): production_log.csv 경로
        process_path (Path): process.csv 경로
        maintenance_path (Path): Predictive Maintenance 원본 데이터 경로
        output_path (Path): 생성된 raw_machine_sensor.csv 저장 경로

    Returns:
        pd.DataFrame: 생성된 raw_machine_sensor 데이터프레임

    Raises:
        FileNotFoundError: 입력 파일이 존재하지 않을 경우
        KeyError: 필요한 컬럼이 입력 데이터에 없을 경우
        ValueError: standard_cycle_time 매핑 실패 또는 센서 기준 데이터가 비어 있을 경우
    """

    np.random.seed(RANDOM_SEED)

    if not production_log_path.exists():
        raise FileNotFoundError(f"production_log.csv가 존재하지 않습니다: {production_log_path}")

    if not process_path.exists():
        raise FileNotFoundError(f"process.csv가 존재하지 않습니다: {process_path}")

    if not maintenance_path.exists():
        raise FileNotFoundError(f"Predictive Maintenance 원본 파일이 존재하지 않습니다: {maintenance_path}")

    production_log = pd.read_csv(production_log_path)
    process = pd.read_csv(process_path)
    maintenance = pd.read_csv(maintenance_path)

    production_log_required_columns = [
        "lot_id",
        "process_id",
        "product_id",
        "machine_id",
        "total_work_time",
        "setup_time",
        "downtime"
    ]

    process_required_columns = [
        "product_id",
        "process_id",
        "standard_cycle_time"
    ]

    maintenance_required_columns = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
        "Target"
    ]

    missing_log_columns = [
        col for col in production_log_required_columns
        if col not in production_log.columns
    ]

    missing_process_columns = [
        col for col in process_required_columns
        if col not in process.columns
    ]

    missing_maintenance_columns = [
        col for col in maintenance_required_columns
        if col not in maintenance.columns
    ]

    if missing_log_columns:
        raise KeyError(f"production_log.csv에 필요한 컬럼이 없습니다: {missing_log_columns}")

    if missing_process_columns:
        raise KeyError(f"process.csv에 필요한 컬럼이 없습니다: {missing_process_columns}")

    if missing_maintenance_columns:
        raise KeyError(f"Predictive Maintenance 데이터에 필요한 컬럼이 없습니다: {missing_maintenance_columns}")

    process_time = (
        process[
            [
                "product_id",
                "process_id",
                "standard_cycle_time"
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    log = production_log.merge(
        process_time,
        on=["product_id", "process_id"],
        how="left"
    )

    if log["standard_cycle_time"].isna().sum() > 0:
        raise ValueError(
            "production_log와 process 간 standard_cycle_time 매핑 실패 row가 존재합니다."
        )

    sensor_base = (
        maintenance[maintenance_required_columns]
        .dropna()
        .reset_index(drop=True)
    )

    if sensor_base.empty:
        raise ValueError("Predictive Maintenance 센서 기준 데이터가 비어 있습니다.")

    # unit 수 추정
    log["estimated_unit_qty"] = (
        (
            (log["total_work_time"] - log["setup_time"] - log["downtime"])
            * 60
        )
        / log["standard_cycle_time"]
    ).round()

    log["estimated_unit_qty"] = (
        log["estimated_unit_qty"]
        .clip(lower=1)
        .astype(int)
    )

    # 공정별 보정값
    process_sensor_factor = {
        "A": {
            "temp": 1.02,
            "speed": 1.05,
            "torque": 1.00,
            "vibration": (0.20, 0.50),
            "pressure": (3.0, 5.0),
            "load": (50, 80)
        },
        "B": {
            "temp": 1.01,
            "speed": 0.95,
            "torque": 1.10,
            "vibration": (0.25, 0.55),
            "pressure": (3.5, 5.5),
            "load": (55, 85)
        },
        "C": {
            "temp": 1.00,
            "speed": 1.10,
            "torque": 0.90,
            "vibration": (0.15, 0.40),
            "pressure": (2.5, 4.5),
            "load": (40, 70)
        },
        "D": {
            "temp": 1.03,
            "speed": 1.00,
            "torque": 1.15,
            "vibration": (0.40, 0.80),
            "pressure": (4.0, 6.5),
            "load": (65, 95)
        },
        "E": {
            "temp": 1.04,
            "speed": 0.85,
            "torque": 1.05,
            "vibration": (0.20, 0.45),
            "pressure": (3.0, 5.0),
            "load": (60, 90)
        }
    }

    # machine_id별 기준값 생성
    machine_ids = sorted(log["machine_id"].dropna().unique())

    machine_base = {}

    for machine_id in machine_ids:
        sampled = sensor_base.sample(n=1).iloc[0]

        machine_base[machine_id] = {
            "air_temperature": sampled["Air temperature [K]"],
            "process_temperature": sampled["Process temperature [K]"],
            "rotational_speed": sampled["Rotational speed [rpm]"],
            "torque": sampled["Torque [Nm]"],
            "tool_wear": sampled["Tool wear [min]"],
            "coolant_temperature": sampled["Process temperature [K]"] - np.random.uniform(8, 15),
            "motor_temperature": sampled["Process temperature [K]"] + np.random.uniform(5, 12),
            "tool_temperature": sampled["Process temperature [K]"] + np.random.uniform(3, 10),
            "humidity": np.random.uniform(30, 70),
            "voltage": np.random.uniform(210, 240)
        }

    # machine_id별 누적 카운터
    machine_counter = {machine_id: 0 for machine_id in machine_ids}

    rows = []

    log = log.sort_values(["lot_id", "process_id"]).reset_index(drop=True)

    for _, row in log.iterrows():
        lot_id = row["lot_id"]
        process_id = row["process_id"]
        machine_id = row["machine_id"]
        downtime = float(row["downtime"])
        unit_qty = int(row["estimated_unit_qty"])

        factor = process_sensor_factor[process_id]
        base = machine_base[machine_id]

        if downtime < 10:
            abnormal_factor = 1.00
        elif downtime < 30:
            abnormal_factor = 1.03
        else:
            abnormal_factor = 1.08

        for unit_no in range(1, unit_qty + 1):
            machine_counter[machine_id] += 1
            sequence = machine_counter[machine_id]

            unit_id = f"{lot_id}_{process_id}_{str(unit_no).zfill(3)}"

            # machine_id 장기 누적 열화
            machine_time_trend = sequence * 0.0008
            machine_wear_trend = sequence * 0.015

            # lot 내부 단기 열화
            lot_progress = unit_no / unit_qty

            lot_temp_trend = lot_progress * 1.20
            lot_motor_trend = lot_progress * 1.50
            lot_tool_temp_trend = lot_progress * 1.30
            lot_wear_trend = lot_progress * 4.00
            lot_vibration_trend = lot_progress * 0.08

            # 온도 계열
            air_temperature = (
                base["air_temperature"]
                * factor["temp"]
                + machine_time_trend
                + lot_temp_trend * 0.4
                + np.random.normal(0, 0.15)
            )

            process_temperature = (
                base["process_temperature"]
                * factor["temp"]
                * abnormal_factor
                + machine_time_trend * 1.2
                + lot_temp_trend
                + np.random.normal(0, 0.15)
            )

            coolant_temperature = (
                base["coolant_temperature"]
                * factor["temp"]
                + machine_time_trend * 0.8
                + lot_temp_trend * 0.3
                + np.random.normal(0, 0.12)
            )

            motor_temperature = (
                base["motor_temperature"]
                * factor["temp"]
                * abnormal_factor
                + machine_time_trend * 1.5
                + lot_motor_trend
                + np.random.normal(0, 0.18)
            )

            tool_temperature = (
                base["tool_temperature"]
                * factor["temp"]
                * abnormal_factor
                + machine_time_trend * 1.2
                + lot_tool_temp_trend
                + np.random.normal(0, 0.18)
            )

            # 마모
            tool_wear = int(
                base["tool_wear"]
                + machine_wear_trend
                + lot_wear_trend
                + np.random.normal(0, 0.8)
            )

            # 습도는 공장 환경 변수로 보고 lot 내부 시계열성 제거
            humidity = (
                base["humidity"]
                + np.random.normal(0, 0.25)
            )

            # 회전 / 토크
            rotational_speed = (
                base["rotational_speed"]
                * factor["speed"]
                * np.random.uniform(0.96, 1.04)
            )

            torque = (
                base["torque"]
                * factor["torque"]
                * np.random.uniform(0.95, 1.05)
            )

            # 진동 / 압력 / 부하
            vibration_low, vibration_high = factor["vibration"]
            pressure_low, pressure_high = factor["pressure"]
            load_low, load_high = factor["load"]

            vibration = (
                np.random.uniform(vibration_low, vibration_high)
                * abnormal_factor
                + lot_vibration_trend
            )

            pressure = (
                np.random.uniform(pressure_low, pressure_high)
                * abnormal_factor
            )

            load = (
                np.random.uniform(load_low, load_high)
                * abnormal_factor
            )

            tool_vibration = (
                vibration
                * np.random.uniform(1.1, 1.5)
                + machine_time_trend * 0.002
                + lot_vibration_trend * 0.7
            )

            # 전압 / 전력
            voltage = (
                base["voltage"]
                * np.random.uniform(0.98, 1.02)
            )

            power_consumption = (
                (torque * rotational_speed)
                / 1000
                * np.random.uniform(0.8, 1.2)
            )

            # 센서 위험도 계산
            risk_score = 0

            if process_temperature > 325:
                risk_score += 1

            if motor_temperature > 335:
                risk_score += 1

            if tool_temperature > 333:
                risk_score += 1

            if vibration > 0.65:
                risk_score += 1

            if tool_vibration > 0.9:
                risk_score += 1

            if torque > 55:
                risk_score += 1

            if tool_wear > 210:
                risk_score += 1

            if load > 90:
                risk_score += 1

            if downtime >= 30:
                risk_score += 1

            # lot 후반부 생산 리스크 증가
            if lot_progress >= 0.80:
                risk_score += 1

            # risk_score 기반 failure 확률
            if risk_score >= 6:
                failure_prob = 0.35
            elif risk_score == 5:
                failure_prob = 0.22
            elif risk_score == 4:
                failure_prob = 0.12
            elif risk_score == 3:
                failure_prob = 0.06
            elif risk_score == 2:
                failure_prob = 0.025
            elif risk_score == 1:
                failure_prob = 0.010
            else:
                failure_prob = 0.003

            failure_target = int(np.random.rand() < failure_prob)

            rows.append({
                "lot_id": lot_id,
                "unit_id": unit_id,
                "process_id": process_id,
                "machine_id": machine_id,
                "air_temperature": round(air_temperature, 2),
                "process_temperature": round(process_temperature, 2),
                "coolant_temperature": round(coolant_temperature, 2),
                "motor_temperature": round(motor_temperature, 2),
                "rotational_speed": round(rotational_speed, 2),
                "torque": round(torque, 2),
                "vibration": round(vibration, 4),
                "pressure": round(pressure, 2),
                "load": round(load, 2),
                "tool_wear": max(tool_wear, 0),
                "tool_temperature": round(tool_temperature, 2),
                "tool_vibration": round(tool_vibration, 4),
                "humidity": round(humidity, 2),
                "power_consumption": round(power_consumption, 2),
                "voltage": round(voltage, 2),
                "failure_target": failure_target
            })

    machine_sensor = pd.DataFrame(rows)

    machine_sensor = machine_sensor[
        [
            "lot_id",
            "unit_id",
            "process_id",
            "machine_id",
            "air_temperature",
            "process_temperature",
            "coolant_temperature",
            "motor_temperature",
            "rotational_speed",
            "torque",
            "vibration",
            "pressure",
            "load",
            "tool_wear",
            "tool_temperature",
            "tool_vibration",
            "humidity",
            "power_consumption",
            "voltage",
            "failure_target"
        ]
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    machine_sensor.to_csv(output_path, index=False, encoding="utf-8-sig")

    return machine_sensor


# main: 스크립트 실행
def main():
    """
    raw_machine_sensor 생성 스크립트 실행

    Raises:
        Exception: 데이터 생성 또는 저장 실패 시 예외 발생
    """

    try:
        machine_sensor = make_machine_sensor(
            PRODUCTION_LOG_PATH,
            PROCESS_PATH,
            MAINTENANCE_PATH,
            OUTPUT_PATH
        )

        print("machine_sensor.csv 생성 완료")
        print(f"저장 경로: {OUTPUT_PATH}")
        print(f"데이터 크기: {machine_sensor.shape}")

        print("\n미리보기")
        print(machine_sensor.head())

        print("\nlot 수")
        print(machine_sensor["lot_id"].nunique())

        print("\n공정별 row 수")
        print(machine_sensor["process_id"].value_counts().sort_index())

        print("\n설비별 row 수")
        print(machine_sensor["machine_id"].value_counts().sort_index())

        print("\nfailure_target 분포")
        print(machine_sensor["failure_target"].value_counts(normalize=True).round(4))

        print("\nPK 중복 확인")
        print(
            machine_sensor.duplicated(
                subset=["lot_id", "unit_id", "process_id", "machine_id"]
            ).sum()
        )

        print("\n결측치 확인")
        print(machine_sensor.isna().sum())

    except Exception as e:
        print(f"machine_sensor.csv 생성 실패: {e}")


if __name__ == "__main__":
    main()