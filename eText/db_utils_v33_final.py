#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块 - 严格按照南方电网新能源数据上送规范 V3.3修订版（2022.2月）建立数据库表结构
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = r"D:/001/eText/eparser.db"

def init_db():
    """初始化数据库，严格按照南方电网新能源数据上送规范 V3.3修订版（2022.2月）建立表结构"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 风力发电机组信息表 (FDJZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wind_turbine_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            turbine_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            wind_speed REAL,
            wind_direction REAL,
            ambient_temp REAL,
            nacelle_temp REAL,
            rotor_speed REAL,
            generator_speed REAL,
            yaw_position REAL,
            cable_twist_angle REAL,
            blade1_pitch_angle REAL,
            blade2_pitch_angle REAL,
            blade3_pitch_angle REAL,
            stator_temp REAL,
            bearing_temp REAL,
            gearbox_oil_temp REAL,
            gearbox_bearing_temp REAL,
            gearbox_oil_pressure REAL,
            gearbox_oil_level REAL,
            active_power REAL,
            reactive_power REAL,
            power_factor REAL,
            generator_voltage REAL,
            generator_current REAL,
            grid_voltage REAL,
            grid_current REAL,
            theoretical_power REAL,
            turbine_status INTEGER,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, turbine_id, timestamp)
        )
    """)
    
    # 2. 升压站信息表 (SYZXX)
    # 主升压变信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS main_transformer_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            transformer_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            lv_voltage_a REAL,
            lv_voltage_b REAL,
            lv_voltage_c REAL,
            lv_voltage_ab REAL,
            lv_voltage_bc REAL,
            lv_voltage_ca REAL,
            lv_current_a REAL,
            lv_current_b REAL,
            lv_current_c REAL,
            lv_active_power REAL,
            lv_active_power_status INTEGER,
            lv_reactive_power REAL,
            lv_reactive_power_status INTEGER,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_current_a REAL,
            hv_current_b REAL,
            hv_current_c REAL,
            hv_active_power REAL,
            hv_active_power_status INTEGER,
            hv_reactive_power REAL,
            hv_reactive_power_status INTEGER,
            hv_power_factor REAL,
            tap_position INTEGER,
            tap_position_status INTEGER,
            hv_switch_remote_local INTEGER,
            lv_switch_remote_local INTEGER,
            protection_action_total INTEGER,
            protection_device_fault TEXT,
            protection_action_signal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, transformer_id, timestamp)
        )
    """)
    
    # 并网点信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grid_connection_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            voltage_a REAL,
            voltage_b REAL,
            voltage_c REAL,
            voltage_ab REAL,
            voltage_bc REAL,
            voltage_ca REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            active_power REAL,
            reactive_power REAL,
            power_factor REAL,
            energy_consumption REAL,
            voltage_flicker_a REAL,
            voltage_flicker_b REAL,
            voltage_flicker_c REAL,
            voltage_deviation_a REAL,
            voltage_deviation_b REAL,
            voltage_deviation_c REAL,
            frequency_deviation_a REAL,
            frequency_deviation_b REAL,
            frequency_deviation_c REAL,
            harmonic_thd_a REAL,
            harmonic_thd_b REAL,
            harmonic_thd_c REAL,
            switch_remote_local INTEGER,
            protection_action_total INTEGER,
            control_circuit_break INTEGER,
            reclosing_action INTEGER,
            protection_device_fault TEXT,
            switch_fault INTEGER,
            protection_action_signal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 升压站母线信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS busbar_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            busbar_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_frequency REAL,
            lv_voltage_a REAL,
            lv_voltage_b REAL,
            lv_voltage_c REAL,
            lv_voltage_ab REAL,
            lv_voltage_bc REAL,
            lv_voltage_ca REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, busbar_name, timestamp)
        )
    """)
    
    # 无功补偿设备信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reactive_compensation_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            device_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            reactive_power REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, device_name, timestamp)
        )
    """)
    
    # 集电线信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feeder_line_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            feeder_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            active_power REAL,
            active_power_status INTEGER,
            reactive_power REAL,
            reactive_power_status INTEGER,
            power_factor REAL,
            voltage_ab REAL,
            voltage_bc REAL,
            voltage_ca REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, feeder_name, timestamp)
        )
    """)
    
    # 断路器信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breaker_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            breaker_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            active_power REAL,
            active_power_quality INTEGER,
            reactive_power REAL,
            reactive_power_quality INTEGER,
            power_factor REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, breaker_name, timestamp)
        )
    """)
    
    # 刀闸信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS disconnect_switch_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            switch_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, switch_name, timestamp)
        )
    """)
    
    # 接地刀闸信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grounding_switch_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            switch_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            status INTEGER,
            status_quality INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, switch_name, timestamp)
        )
    """)
    
    # 等效发电机信息
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equivalent_generator_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            generator_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            active_power_quality INTEGER,
            reactive_power REAL,
            reactive_power_quality INTEGER,
            phase_voltage_a REAL,
            phase_current_a REAL,
            max_adjustable_output REAL,
            min_adjustable_output REAL,
            rated_capacity REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, generator_id, timestamp)
        )
    """)
    
    # 3. 风电场总体信息表 (ZTXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wind_farm_overall_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            longitude REAL,
            latitude REAL,
            normal_generation_active_capacity REAL,
            normal_generation_reactive_capacity REAL,
            normal_generation_units INTEGER,
            planned_maintenance_active_capacity REAL,
            planned_maintenance_reactive_capacity REAL,
            planned_maintenance_units INTEGER,
            curtailed_active_capacity REAL,
            curtailed_reactive_capacity REAL,
            curtailed_units INTEGER,
            standby_active_capacity REAL,
            standby_reactive_capacity REAL,
            standby_units INTEGER,
            communication_interrupt_active_capacity REAL,
            communication_interrupt_reactive_capacity REAL,
            communication_interrupt_units INTEGER,
            unplanned_outage_active_capacity REAL,
            unplanned_outage_reactive_capacity REAL,
            unplanned_outage_units INTEGER,
            reactive_compensation_availability_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 4. 气象环境信息表 (QXHJ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS meteorological_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            temp_10m REAL,
            humidity_10m REAL,
            pressure_10m REAL,
            wind_speed_10m REAL,
            wind_direction_10m REAL,
            wind_speed_30m REAL,
            wind_direction_30m REAL,
            wind_speed_50m REAL,
            wind_direction_50m REAL,
            wind_speed_70m REAL,
            wind_direction_70m REAL,
            hub_height_wind_speed REAL,
            hub_height_wind_direction REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 5. AGC信息表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agc_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            max_output_limit REAL,
            min_output_limit REAL,
            response_rate REAL,
            target_value_return REAL,
            status INTEGER,
            remote_local INTEGER,
            increase_lock INTEGER,
            decrease_lock INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 6. AVC信息表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avc_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            hv_bus_voltage_upper_limit REAL,
            hv_bus_voltage_lower_limit REAL,
            status INTEGER,
            remote_local INTEGER,
            increase_lock INTEGER,
            decrease_lock INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 7. 短期功率预测信息表 (DQYC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS short_term_forecast_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            forecast_time TIME NOT NULL,
            timestamp DATETIME NOT NULL,
            forecast_power REAL,
            planned_capacity REAL,
            operating_units INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, forecast_date, forecast_time, timestamp)
        )
    """)
    
    # 8. 超短期功率预测信息表 (CDQYC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ultra_short_term_forecast_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            forecast_time TIME NOT NULL,
            timestamp DATETIME NOT NULL,
            forecast_power REAL,
            operating_capacity REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, forecast_date, forecast_time, timestamp)
        )
    """)
    
    # 9. 统计信息表 (TJXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS statistics_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            turbine_count INTEGER,
            installed_capacity REAL,
            total_active_power REAL,
            total_reactive_power REAL,
            available_generation_power REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 10. 光伏箱变/方阵信息表 (XB-FZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_transformer_array_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            transformer_id TEXT,
            array_id TEXT,
            timestamp DATETIME NOT NULL,
            lv_voltage_a REAL,
            lv_current_a REAL,
            lv_active_power REAL,
            hv_voltage_a REAL,
            hv_voltage_b REAL,
            hv_voltage_c REAL,
            hv_voltage_ab REAL,
            hv_voltage_bc REAL,
            hv_voltage_ca REAL,
            hv_current_a REAL,
            hv_current_b REAL,
            hv_current_c REAL,
            hv_active_power REAL,
            hv_reactive_power REAL,
            hv_power_factor REAL,
            winding_temp REAL,
            daily_energy REAL,
            monthly_energy REAL,
            yearly_energy REAL,
            cumulative_energy REAL,
            theoretical_max_power REAL,
            reactive_output_range REAL,
            transformer_status INTEGER,
            dc_overvoltage INTEGER,
            ac_overvoltage INTEGER,
            ac_undervoltage INTEGER,
            protection_signals TEXT,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, transformer_id, array_id, timestamp)
        )
    """)
    
    # 11. 光伏逆变器/汇流箱信息表 (NBQ-HLX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_inverter_combiner_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            inverter_id TEXT,
            combiner_id TEXT,
            timestamp DATETIME NOT NULL,
            dc_voltage REAL,
            dc_current REAL,
            dc_power REAL,
            ac_voltage_a REAL,
            ac_voltage_b REAL,
            ac_voltage_c REAL,
            ac_voltage_ab REAL,
            ac_voltage_bc REAL,
            ac_voltage_ca REAL,
            ac_current_a REAL,
            ac_current_b REAL,
            ac_current_c REAL,
            ac_active_power REAL,
            ac_reactive_power REAL,
            ac_power_factor REAL,
            inverter_temp REAL,
            daily_energy REAL,
            monthly_energy REAL,
            yearly_energy REAL,
            cumulative_energy REAL,
            max_output_power REAL,
            reactive_output_range REAL,
            grid_status INTEGER,
            fault_status INTEGER,
            maintenance_status INTEGER,
            curtailment_status INTEGER,
            normal_shutdown_status INTEGER,
            communication_interrupt_status INTEGER,
            dc_overvoltage INTEGER,
            ac_overvoltage INTEGER,
            ac_undervoltage INTEGER,
            protection_signals TEXT,
            feeder_line TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, inverter_id, combiner_id, timestamp)
        )
    """)
    
    # 12. 光伏电站总体信息表 (ZTXX)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_farm_overall_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            longitude REAL,
            latitude REAL,
            normal_generation_active_capacity REAL,
            normal_generation_reactive_capacity REAL,
            normal_generation_units INTEGER,
            planned_maintenance_active_capacity REAL,
            planned_maintenance_reactive_capacity REAL,
            planned_maintenance_units INTEGER,
            curtailed_active_capacity REAL,
            curtailed_reactive_capacity REAL,
            curtailed_units INTEGER,
            standby_active_capacity REAL,
            standby_reactive_capacity REAL,
            standby_units INTEGER,
            communication_interrupt_active_capacity REAL,
            communication_interrupt_reactive_capacity REAL,
            communication_interrupt_units INTEGER,
            unplanned_outage_active_capacity REAL,
            unplanned_outage_reactive_capacity REAL,
            unplanned_outage_units INTEGER,
            actual_grid_capacity REAL,
            total_output REAL,
            controllable_capacity REAL,
            theoretical_max_active_power REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 13. 光伏气象环境信息表 (QXHJ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pv_meteorological_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            total_radiation REAL,
            direct_radiation REAL,
            diffuse_radiation REAL,
            reflected_radiation REAL,
            temperature REAL,
            pv_module_temperature REAL,
            pressure REAL,
            humidity REAL,
            wind_speed REAL,
            wind_direction REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 14. 太阳跟踪系统信息表 (TYGZ)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS solar_tracking_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_code TEXT NOT NULL,
            station_name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            height_angle REAL,
            azimuth_angle REAL,
            operation_status INTEGER,
            auto_manual_status INTEGER,
            anti_wind_snow_status INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(station_code, timestamp)
        )
    """)
    
    # 15. 解析结果主表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parse_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            parse_time TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_result(result):
    """保存解析结果到数据库，严格按照规范存储到对应表中"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 保存主记录
    summary_json = json.dumps(result, ensure_ascii=False, indent=2)
    cur.execute("""
        INSERT INTO parse_results (filename, parse_time, summary_json)
        VALUES (?, ?, ?)
    """, (result["filename"], result["parse_time"], summary_json))
    
    conn.commit()
    conn.close()

def query_results():
    """查询所有解析结果"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, parse_time, summary_json FROM parse_results ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_station_info():
    """获取所有场站信息"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT station_code, station_name FROM (
            SELECT station_code, station_name FROM wind_turbine_info
            UNION
            SELECT station_code, station_name FROM main_transformer_info
            UNION
            SELECT station_code, station_name FROM pv_transformer_array_info
            UNION
            SELECT station_code, station_name FROM pv_inverter_combiner_info
        ) ORDER BY station_code
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_wind_turbine_data(station_code, start_date=None, end_date=None):
    """获取风力发电机组数据"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    sql = """
        SELECT * FROM wind_turbine_info 
        WHERE station_code = ?
    """
    params = [station_code]
    
    if start_date:
        sql += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND timestamp <= ?"
        params.append(end_date)
    
    sql += " ORDER BY timestamp DESC, turbine_id"
    
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_pv_transformer_data(station_code, start_date=None, end_date=None):
    """获取光伏箱变数据"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    sql = """
        SELECT * FROM pv_transformer_array_info 
        WHERE station_code = ?
    """
    params = [station_code]
    
    if start_date:
        sql += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND timestamp <= ?"
        params.append(end_date)
    
    sql += " ORDER BY timestamp DESC, transformer_id"
    
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成，严格按照南方电网新能源数据上送规范 V3.3修订版（2022.2月）建立表结构")