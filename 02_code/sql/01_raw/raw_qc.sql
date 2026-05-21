/*
 * 파일명: raw_qc.sql
 *
 * 목적:
 *     - Raw 스키마에 적재된 데이터들의 기본적인 정합성 검증
 *
 * 대상 테이블:
 *     - raw.raw_orders
 *     - raw.raw_inventory
 *     - raw.raw_process
 *     - raw.raw_production_log
 *     - raw.raw_machine_sensor
*/


-- ======================================================================================================================


/*
 * raw_orders 테이블 기본 정보
*/

-- 샘플
SELECT  *
  FROM  raw.raw_orders
 LIMIT  20;


-- row count: 150건
SELECT  COUNT(*) AS cnt
  FROM  raw.raw_orders;


/*
 * 컬럼 중복 및 NULL 확인
*/

-- PK 컬럼(order_id) 중복 확인: 중복 없음
SELECT  order_id
		,COUNT(*) AS duplicated_count
  FROM  raw.raw_orders
 GROUP
    BY  order_id
HAVING  COUNT(*) > 1;

-- 필수 컬럼 NULL 확인:
--     - order_id: 0건
--     - product_id: 0건
--     - order_qty: 0건
--     - order_date: 0건
--     - due_date: 0건
SELECT  SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END) AS null_blank_order_id
		,SUM(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 ELSE 0 END) AS null_blank_product_id
		,SUM(CASE WHEN order_qty IS NULL THEN 1 ELSE 0 END) AS null_order_qty
		,SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_order_date
		,SUM(CASE WHEN due_date IS NULL THEN 1 ELSE 0 END) AS null_due_date
  FROM  raw.raw_orders;


/*
 * 로직 정합성 확인
*/

-- 주문 수량이 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_orders
 WHERE  order_qty <= 0;

-- 납기일이 주문일보다 빠른 경우: 0건
SELECT  *
  FROM  raw.raw_orders
 WHERE  due_date < order_date;

-- 납기일이 지정한 날짜(최대 주문일 + 3일) 이상인지 확인(이상이면 PASS, 아니면 FAIL): PASS
SELECT  MAX(order_date) AS max_order_date
		,MIN(due_date) AS min_due_date
		,CASE WHEN MIN(due_Date) >= MAX(order_date) + INTERVAL '3 days' THEN 'PASS' ELSE 'FAIL' END AS qc_result
  FROM  raw.raw_orders;


/*
 * 조인 정합성 확인
*/

-- raw_orders.product_id가 raw_process에 없는 경우: 0건
SELECT  o.product_id
		,COUNT(*) AS order_count
  FROM  raw.raw_orders AS o
  LEFT
  JOIN  (
  		SELECT  DISTINCT product_id
  		  FROM  raw.raw_process
  		) AS p
    ON  p.product_id = o.product_id
 WHERE  p.product_id IS NULL
 GROUP
    BY  o.product_id
 ORDER
    BY  order_count DESC;


-- ======================================================================================================================


/*
 * raw_inventory 테이블 기본 정보
*/

-- 샘플
SELECT  *
  FROM  raw.raw_inventory
 LIMIT  20;

-- row count: 100건
SELECT  COUNT(*) AS cnt
  FROM  raw.raw_inventory;


/*
 * 컬럼 중복 및 NULL 확인
*/

-- PK 컬럼(material_id) 중복 확인: 중복 없음
SELECT  material_id
		,COUNT(*) AS duplicated_count
  FROM  raw.raw_inventory
 GROUP
    BY  material_id
HAVING  COUNT(*) > 1;

-- 필수 컬럼 NULL 확인:
--     - material_id: 0건
--     - unit_price: 0건
--     - stock_qty: 0건
--     - lead_time: 0건
SELECT  SUM(CASE WHEN material_id IS NULL OR TRIM(material_id) = '' THEN 1 ELSE 0 END) AS null_blank_material_id
		,SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END) AS null_unit_price
		,SUM(CASE WHEN stock_qty IS NULL THEN 1 ELSE 0 END) AS null_stock_qty
		,SUM(CASE WHEN lead_time IS NULL THEN 1 ELSE 0 END) AS null_lead_time
  FROM  raw.raw_inventory;


/*
 * 로직 정합성 확인
*/

-- 현재 재고 수량이 음수인 경우: 0건
SELECT  *
  FROM  raw.raw_inventory
 WHERE  stock_qty < 0;

-- 객단가가 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_inventory
 WHERE  unit_price <= 0;

-- 입고 예정 수량이 음수인 경우: 0건
SELECT  *
  FROM  raw.raw_inventory
 WHERE  incoming_qty < 0;

-- 리드타임이 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_inventory
 WHERE  lead_time <= 0;


/*
 * 조인 정합성 확인
*/

-- raw_process.material_id가 raw_inventory에 없는 경우: 0건
SELECT  p.material_id
		,COUNT(*) AS process_count
  FROM  raw.raw_process AS p
  LEFT
  JOIN  raw.raw_inventory AS i
    ON  p.material_id = i.material_id
 WHERE  i.material_id IS NULL
 GROUP
    BY  p.material_id
 ORDER
    BY  process_count DESC;


-- ======================================================================================================================


/*
 * raw_process 테이블 기본 정보
*/

-- 샘플
SELECT  *
  FROM  raw.raw_process
 LIMIT  20;

-- row count: 297건
SELECT  COUNT(*) AS cnt
  FROM  raw.raw_process;


/*
 * 컬럼 중복 및 NULL 확인
*/

-- PK 컬럼(product_id, process_id, material_id) 중복 확인: 중복 없음
SELECT  product_id
		,process_id
		,material_id
		,COUNT(*) AS duplicated_count
  FROM  raw.raw_process
 GROUP
    BY  product_id
		,process_id
		,material_id
HAVING  COUNT(*) > 1;

-- 필수 컬럼 NULL 확인:
--     - product_id: 0건
--     - process_id: 0건
--     - material_id: 0건
--     - process_step: 0건
--     - required_material_qty: 0건
--     - standard_cycle_time: 0건
SELECT  SUM(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 ELSE 0 END) AS null_blank_product_id
		,SUM(CASE WHEN process_id IS NULL OR TRIM(process_id) = '' THEN 1 ELSE 0 END) AS null_blank_process_id
		,SUM(CASE WHEN material_id IS NULL OR TRIM(material_id) = '' THEN 1 ELSE 0 END) AS null_blank_material_id
		,SUM(CASE WHEN process_step IS NULL THEN 1 ELSE 0 END) AS null_process_step
		,SUM(CASE WHEN required_material_qty IS NULL THEN 1 ELSE 0 END) AS null_required_material_qty
		,SUM(CASE WHEN standard_cycle_time IS NULL THEN 1 ELSE 0 END) AS null_standard_cycle_time
  FROM  raw.raw_process;


/*
 * 로직 정합성 확인
*/

-- process_id가 A~E가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_process
 WHERE  process_id NOT IN ('A', 'B', 'C', 'D', 'E');

-- process_id와 process_step 매핑이 맞지 않는 경우: 0건
SELECT  *
  FROM  raw.raw_process
 WHERE  (process_id = 'A' AND process_step <> 1)
    OR  (process_id = 'B' AND process_step <> 2)
	OR  (process_id = 'C' AND process_step <> 3)
	OR  (process_id = 'D' AND process_step <> 4)
	OR  (process_id = 'E' AND process_step <> 5);

-- 필요 원자재 수량이 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_process
 WHERE  required_material_qty <= 0;

-- 표준 작업 시간이 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_process
 WHERE  standard_cycle_time <= 0;

-- 제품별 A~E 공정이 모두 존재하지 않는 경우: 0건
SELECT  product_id
		,COUNT(DISTINCT process_id) AS process_count
  FROM  raw.raw_process
 GROUP
    BY  product_id
HAVING  COUNT(DISTINCT process_id) <> 5;


/*
 * 조인 정합성 확인
*/

-- raw_process.material_id가 raw_inventory에 없는 경우: 0건
SELECT  p.material_id
		,COUNT(*) AS process_count
  FROM  raw.raw_process AS p
  LEFT
  JOIN  raw.raw_inventory AS i
    ON  i.material_id = p.material_id
 WHERE  i.material_id IS NULL
 GROUP
    BY  p.material_id
 ORDER
    BY  process_count DESC;

-- raw_orders.product_id가 raw_process에 없는 경우: 0건
SELECT  o.product_id
		,COUNT(*) AS order_count
  FROM  raw.raw_orders AS o
  LEFT
  JOIN  (
		SELECT  DISTINCT product_id
		  FROM  raw.raw_process
  		) AS p
    ON  p.product_id = o.product_id
 WHERE  p.product_id IS NULL
 GROUP
    BY  o.product_id
 ORDER
    BY  order_count DESC;


-- ======================================================================================================================


/*
 * raw_production_log 테이블 기본 정보
*/

-- 샘플
SELECT  *
  FROM  raw.raw_production_log
 LIMIT  20;

-- row count: 5000건
SELECT  COUNT(*) AS cnt
  FROM  raw.raw_production_log;


/*
 * 컬럼 중복 및 NULL 확인
*/

-- PK 컬럼(lot_id, process_id) 중복 확인: 중복 없음
SELECT  lot_id
		,process_id
		,COUNT(*) AS duplicated_count
  FROM  raw.raw_production_log
 GROUP
    BY  lot_id
		,process_id
HAVING  COUNT(*) > 1;

-- 필수 컬럼 NULL 확인:
--     - lot_id: 0건
--     - process_id: 0건
--     - order_id: 0건
--     - product_id: 0건
--     - machine_id: 0건
--     - total_work_time: 0건
--     - setup_time: 0건
--     - downtime: 0건
SELECT  SUM(CASE WHEN lot_id IS NULL OR TRIM(lot_id) = '' THEN 1 ELSE 0 END) AS null_blank_lot_id
		,SUM(CASE WHEN process_id IS NULL OR TRIM(process_id) = '' THEN 1 ELSE 0 END) AS null_blank_process_id
		,SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END) AS null_blank_order_id
		,SUM(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 ELSE 0 END) AS null_blank_product_id
		,SUM(CASE WHEN machine_id IS NULL OR TRIM(machine_id) = '' THEN 1 ELSE 0 END) AS null_blank_machine_id
		,SUM(CASE WHEN total_work_time IS NULL THEN 1 ELSE 0 END) AS null_total_work_time
		,SUM(CASE WHEN setup_time IS NULL THEN 1 ELSE 0 END) AS null_setup_time
		,SUM(CASE WHEN downtime IS NULL THEN 1 ELSE 0 END) AS null_downtime
  FROM  raw.raw_production_log;


/*
 * 로직 정합성 확인
*/

-- process_id가 A~E가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_production_log
 WHERE  process_id NOT IN ('A', 'B', 'C', 'D', 'E');

-- 총 작업 시간이 양수가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_production_log
 WHERE  total_work_time <= 0;

-- 준비 시간이 음수인 경우: 0건
SELECT  *
  FROM  raw.raw_production_log
 WHERE  setup_time < 0;

-- 중단 시간이 음수인 경우: 0건
SELECT  *
  FROM  raw.raw_production_log
 WHERE  downtime < 0;

-- 하나의 lot_id가 A~E 5개 공정을 모두 가지지 않는 경우: 0건
SELECT  lot_id
		,COUNT(DISTINCT process_id) AS process_count
  FROM  raw.raw_production_log
 GROUP
    BY  lot_id
HAVING  COUNT(DISTINCT process_id) <> 5;


/*
 * 조인 정합성 확인
*/

-- raw_production_log.product_id가 raw_process에 없는 경우: 0건
SELECT  pl.product_id
		,COUNT(*) AS production_count
  FROM  raw.raw_production_log AS pl
  LEFT
  JOIN  (
		SELECT  DISTINCT product_id
		  FROM  raw.raw_process
	    ) AS p
    ON  p.product_id = pl.product_id
 WHERE  p.product_id IS NULL
 GROUP
    BY  pl.product_id
 ORDER
    BY  production_count DESC;

-- raw_production_log.process_id가 raw_process에 없는 경우: 0건
SELECT  pl.process_id
		,COUNT(*) AS production_count
  FROM  raw.raw_production_log AS pl
  LEFT
  JOIN  (
		SELECT  DISTINCT process_id
		  FROM  raw.raw_process
  		) AS p
	ON  p.process_id = pl.process_id
 WHERE  p.process_id IS NULL
 GROUP
    BY  pl.process_id
 ORDER
    BY  production_count DESC;

-- raw_production_log의 product_id + process_id 조합이 raw_process에 없는 경우: 0건
SELECT  pl.product_id
		,pl.process_id
		,COUNT(*) AS production_count
  FROM  raw.raw_production_log AS pl
  LEFT
  JOIN  (
		SELECT  DISTINCT product_id
				,process_id
		  FROM  raw.raw_process
  		) AS p
	ON  p.product_id = pl.product_id
   AND  p.process_id = pl.process_id
 WHERE  p.product_id IS NULL
 GROUP
    BY  pl.product_id
		,pl.process_id
 ORDER
    BY  production_count DESC;


-- ======================================================================================================================


/*
 * raw_machine_sensor 테이블 기본 정보
*/

-- 샘플
SELECT  *
  FROM  raw.raw_machine_sensor
 LIMIT  20;

-- row count: 234,777건
SELECT  COUNT(*) AS cnt
  FROM  raw.raw_machine_sensor;


/*
 * 컬럼 중복 및 NULL 확인
*/

-- PK 컬럼(lot_id, unit_id, process_id, machine_id) 중복 확인: 중복 없음
SELECT  lot_id
		,unit_id
		,process_id
		,machine_id
		,COUNT(*) AS duplicated_count
  FROM  raw.raw_machine_sensor
 GROUP
    BY  lot_id
		,unit_id
		,process_id
		,machine_id
HAVING  COUNT(*) > 1;

-- 필수 컬럼 NULL 확인
--     - lot_id: 0건
--     - unit_id: 0건
--     - process_id: 0건
--     - machine_id: 0건
--     - 기타 설비 변수들: 0건
SELECT  SUM(CASE WHEN lot_id IS NULL OR TRIM(lot_id) = '' THEN 1 ELSE 0 END) AS null_blank_lot_id
		,SUM(CASE WHEN unit_id IS NULL OR TRIM(unit_id) = '' THEN 1 ELSE 0 END) AS null_blank_unit_id
		,SUM(CASE WHEN process_id IS NULL OR TRIM(process_id) = '' THEN 1 ELSE 0 END) AS null_blank_process_id
		,SUM(CASE WHEN machine_id IS NULL OR TRIM(machine_id) = '' THEN 1 ELSE 0 END) AS null_blank_machine_id
		,SUM(CASE WHEN air_temperature IS NULL THEN 1 ELSE 0 END) AS null_air_temperature
		,SUM(CASE WHEN process_temperature IS NULL THEN 1 ELSE 0 END) AS null_prcess_temperature
		,SUM(CASE WHEN coolant_temperature IS NULL THEN 1 ELSE 0 END) AS null_coolant_temperature
		,SUM(CASE WHEN motor_temperature IS NULL THEN 1 ELSE 0 END) AS null_motor_temperature
		,SUM(CASE WHEN rotational_speed IS NULL THEN 1 ELSE 0 END) AS null_rotational_speed
		,SUM(CASE WHEN torque IS NULL THEN 1 ELSE 0 END) AS null_torque
		,SUM(CASE WHEN vibration IS NULL THEN 1 ELSE 0 END) AS null_vibration
		,SUM(CASE WHEN pressure IS NULL THEN 1 ELSE 0 END) AS null_pressure
		,SUM(CASE WHEN load IS NULL THEN 1 ELSE 0 END) AS null_load
		,SUM(CASE WHEN tool_wear IS NULL THEN 1 ELSE 0 END) AS null_too_wear
		,SUM(CASE WHEN tool_temperature IS NULL THEN 1 ELSE 0 END) AS null_tool_temperature
		,SUM(CASE WHEN tool_vibration IS NULL THEN 1 ELSE 0 END) AS null_tool_vibration
		,SUM(CASE WHEN humidity IS NULL THEN 1 ELSE 0 END) AS null_humidity
		,SUM(CASE WHEN power_consumption IS NULL THEN 1 ELSE 0 END) AS null_power_consumption
		,SUM(CASE WHEN voltage IS NULL THEN 1 ELSE 0 END) AS null_voltage
		,SUM(CASE WHEN failure_target IS NULL THEN 1 ELSE 0 END) AS null_failure_target
  FROM  raw.raw_machine_sensor;


/*
 * 로직 정합성 확인
*/

-- process_id가 A~E가 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_machine_sensor
 WHERE  process_id NOT IN ('A', 'B', 'C', 'D', 'E');

-- failure_target이 0 또는 1이 아닌 경우: 0건
SELECT  *
  FROM  raw.raw_machine_sensor
 WHERE  failure_target NOT IN (0, 1);


/*
 * 조인 정합성 확인
*/

-- raw_machine_sensor의 lot_id + process_id + machine_id 조합이 raw_production_log에 없는 경우: 0건
SELECT  ms.lot_id
		,ms.process_id
		,ms.machine_id
		,COUNT(*) AS sensor_count
  FROM  raw.raw_machine_sensor AS ms
  LEFT
  JOIN  raw.raw_production_log AS pl
    ON  pl.lot_id = ms.lot_id
   AND  pl.process_id = ms.process_id
   AND  pl.machine_id = ms.machine_id
 WHERE  pl.lot_id IS NULL
 GROUP
    BY  ms.lot_id
		,ms.process_id
		,ms.machine_id
 ORDER
    BY  sensor_count DESC;

-- raw_production_log에는 있는데 raw_machine_sensor에는 없는 lot_id + process_id + machine_id 조합: 0건
SELECT  pl.lot_id
		,pl.process_id
		,pl.machine_id
  FROM  raw.raw_production_log AS pl
  LEFT
  JOIN  (
		SELECT  DISTINCT lot_id
				,process_id
				,machine_id
		  FROM  raw.raw_machine_sensor
		) AS ms
    ON  pl.lot_id = ms.lot_id
   AND  pl.process_id = ms.process_id
   AND  pl.machine_id = ms.machine_id
 WHERE  ms.lot_id IS NULL;