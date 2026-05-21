-- Raw Schema 생성
CREATE SCHEMA IF NOT EXISTS raw;

-- 기존 테이블 삭제
DROP TABLE IF EXISTS raw.raw_machine_sensor;
DROP TABLE IF EXISTS raw.raw_production_log;
DROP TABLE IF EXISTS raw.raw_process;
DROP TABLE IF EXISTS raw.raw_inventory;
DROP TABLE IF EXISTS raw.raw_orders;

-- orders 테이블 생성
CREATE TABLE raw.raw_orders (
	order_id	VARCHAR(50)	NOT NULL	PRIMARY KEY,
	product_id	VARCHAR(50)	NOT NULL,
	order_qty	INT			NOT NULL,
	order_date	DATE		NOT NULL,
	due_date	DATE		NOT NULL
);

CREATE INDEX idx_raw_orders_product_id
ON raw.raw_orders(product_id);

CREATE INDEX idx_raw_orders_order_date
ON raw.raw_orders(order_date);

CREATE INDEX idx_raw_orders_due_date
ON raw.raw_orders(due_date);


-- inventory 테이블 생성
CREATE TABLE raw.raw_inventory (
	material_id			VARCHAR(50)		NOT NULL	PRIMARY KEY,
	unit_price			NUMERIC(10, 2),
	stock_qty			INT				NOT NULL,
	incoming_qty		INT,
	incoming_order_date	DATE,
	lead_time			INT				NOT NULL
);

CREATE INDEX idx_raw_inventory_stock_qty
ON raw.raw_inventory(stock_qty);

CREATE INDEX idx_raw_inventory_lead_time
ON raw.raw_inventory(lead_time);

CREATE INDEX idx_raw_inventory_incoming_order_date
ON raw.raw_inventory(incoming_order_date);


-- process 테이블 생성
CREATE TABLE raw.raw_process (
	product_id				VARCHAR(50)		NOT NULL,
	process_id				VARCHAR(50)		NOT NULL,
	material_id				VARCHAR(50)		NOT NULL,
	process_step			INT				NOT NULL,
	required_material_qty	INT				NOT NULL,
	standard_cycle_time		NUMERIC(10, 2)	NOT NULL,

	PRIMARY KEY (
		product_id,
		process_id,
		material_id
	)
);

CREATE INDEX idx_raw_process_product_id
ON raw.raw_process(product_id);

CREATE INDEX idx_raw_process_process_id
ON raw.raw_process(process_id);

CREATE INDEX idx_raw_process_material_id
ON raw.raw_process(material_id);

CREATE INDEX idx_raw_process_process_step
ON raw.raw_process(process_step);


-- production_log 테이블 생성
CREATE TABLE raw.raw_production_log (
	lot_id				VARCHAR(50)		NOT NULL,
	process_id			VARCHAR(50)		NOT NULL,
	order_id			VARCHAR(50)		NOT NULL,
	product_id			VARCHAR(50)		NOT NULL,
	machine_id			VARCHAR(50)		NOT NULL,
	total_work_time		NUMERIC(10, 2)	NOT NULL,
	setup_time			NUMERIC(10, 2)	NOT NULL,
	downtime			NUMERIC(10, 2)	NOT NULL,

	PRIMARY KEY (
		lot_id,
		process_id
	)
);

CREATE INDEX idx_raw_production_log_order_id
ON raw.raw_production_log(order_id);

CREATE INDEX idx_raw_production_log_product_id
ON raw.raw_production_log(product_id);

CREATE INDEX idx_raw_production_log_process_id
ON raw.raw_production_log(process_id);

CREATE INDEX idx_raw_production_log_machine_id
ON raw.raw_production_log(machine_id);


-- machine_sensor 테이블 생성
CREATE TABLE raw.raw_machine_sensor (
    lot_id 					VARCHAR(50) 	NOT NULL,
    unit_id 				VARCHAR(80) 	NOT NULL,
    process_id 				VARCHAR(50) 	NOT NULL,
    machine_id 				VARCHAR(50)	 	NOT NULL,

    air_temperature 		NUMERIC(10, 2) 	NOT NULL,
    process_temperature 	NUMERIC(10, 2) 	NOT NULL,
    coolant_temperature 	NUMERIC(10, 2) 	NOT NULL,
    motor_temperature 		NUMERIC(10, 2) 	NOT NULL,

    rotational_speed 		NUMERIC(10, 2) 	NOT NULL,
    torque 					NUMERIC(10, 2) 	NOT NULL,

    vibration 				NUMERIC(10, 4) 	NOT NULL,
    pressure 				NUMERIC(10, 2) 	NOT NULL,
    load 					NUMERIC(10, 2) 	NOT NULL,

    tool_wear 				INT 			NOT NULL,

    tool_temperature 		NUMERIC(10, 2) 	NOT NULL,
    tool_vibration 			NUMERIC(10, 4) 	NOT NULL,

    humidity 				NUMERIC(10, 2) 	NOT NULL,
    power_consumption 		NUMERIC(10, 2) 	NOT NULL,
    voltage 				NUMERIC(10, 2) 	NOT NULL,

    failure_target 			INT 			NOT NULL,

    PRIMARY KEY (
        lot_id,
        unit_id,
        process_id,
        machine_id
    )
);

CREATE INDEX idx_raw_machine_sensor_lot_id
ON raw.raw_machine_sensor(lot_id);

CREATE INDEX idx_raw_machine_sensor_unit_id
ON raw.raw_machine_sensor(unit_id);

CREATE INDEX idx_raw_machine_sensor_process_id
ON raw.raw_machine_sensor(process_id);

CREATE INDEX idx_raw_machine_sensor_machine_id
ON raw.raw_machine_sensor(machine_id);

CREATE INDEX idx_raw_machine_sensor_failure_target
ON raw.raw_machine_sensor(failure_target);