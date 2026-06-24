from datetime import datetime
import os
import sys
import re
import subprocess
import platform

def convert_seconds_to_hhmmss(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def parse_battery_report(html_content):
    design_capacity = None
    full_charge_capacity = None
    
    m_design = re.search(r'DESIGN CAPACITY.*?</td>\s*<td>\s*([\d,]+)\s*mWh', html_content, re.DOTALL | re.IGNORECASE)
    if m_design:
        design_capacity = m_design.group(1).replace(",", "")
        
    m_full = re.search(r'FULL CHARGE CAPACITY.*?</td>\s*<td>\s*([\d,]+)\s*mWh', html_content, re.DOTALL | re.IGNORECASE)
    if m_full:
        full_charge_capacity = m_full.group(1).replace(",", "")
        
    recent_usage = []
    row_pattern = re.compile(
        r'<tr[^>]*>\s*'
        r'<td class="dateTime"><span class="date">(?P<date>[^<]*)</span><span class="time">(?P<time>[^<]*)</span></td>\s*'
        r'<td class="state">\s*(?P<state>[^<]*?)\s*</td>\s*'
        r'<td class="acdc">\s*(?P<source>[^<]*?)\s*</td>\s*'
        r'<td class="percent">\s*(?P<percent>[^<]*?)\s*</td>\s*'
        r'<td class="mw">\s*(?P<capacity>[^<]*?)\s*</td>\s*'
        r'</tr>',
        re.DOTALL | re.IGNORECASE
    )
    
    current_date = ""
    for match in row_pattern.finditer(html_content):
        d_val = match.group('date').strip()
        t_val = match.group('time').strip()
        state_val = match.group('state').strip()
        source_val = match.group('source').strip()
        pct_val = match.group('percent').strip()
        cap_val = match.group('capacity').strip()
        
        if d_val:
            current_date = d_val
            
        full_time_str = f"{current_date} {t_val}".strip()
        dt = None
        try:
            dt = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
            
        cap_clean = None
        if cap_val:
            cap_clean_str = re.sub(r'[^\d]', '', cap_val)
            if cap_clean_str:
                cap_clean = int(cap_clean_str)
                
        recent_usage.append({
            "time": dt,
            "state": state_val,
            "source": source_val,
            "percent": pct_val,
            "capacity_mwh": cap_clean
        })
        
    return design_capacity, full_charge_capacity, recent_usage

def find_closest_usage(target_time, recent_usage):
    if not recent_usage:
        return None
    closest_entry = None
    min_diff = None
    for entry in recent_usage:
        if entry["time"] is None:
            continue
        diff = abs((entry["time"] - target_time).total_seconds())
        if min_diff is None or diff < min_diff:
            min_diff = diff
            closest_entry = entry
    if min_diff is not None and min_diff < 1800: # within 30 mins
        return closest_entry
    return None

def parse_log_file(filepath):
    events = []
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Format: 2026-06-11 20:24:53,417 | message
            m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \| (.*)$", line)
            if m:
                dt_str, msg = m.groups()
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                
                if "Starting new test" in msg:
                    events.append({
                        "line": line_num,
                        "time": dt,
                        "type": "START_TEST",
                        "level": None,
                        "capacity": None
                    })
                else:
                    m_lvl = re.search(r"Battery level: (\d+)", msg)
                    if m_lvl:
                        lvl = int(m_lvl.group(1))
                        cap = None
                        m_cap = re.search(r"Capacity:\s*(\d+)\s*(mAh|mWh)", msg)
                        if m_cap:
                            cap = int(m_cap.group(1))
                        events.append({
                            "line": line_num,
                            "time": dt,
                            "type": "LEVEL",
                            "level": lvl,
                            "capacity": cap
                        })
    return events

def detect_cycles(events):
    cycles = []
    current_cycle = None
    
    for i, ev in enumerate(events):
        is_start = False
        
        # Check if this event starts a new cycle
        if ev["type"] == "START_TEST":
            is_start = True
        elif ev["type"] == "LEVEL" and ev["level"] == 100:
            if current_cycle is None:
                is_start = True
            else:
                # If battery has dropped significantly, 100% is a new cycle
                levels_in_cycle = [r["level"] for r in current_cycle["readings"] if r["level"] is not None]
                min_lvl = min(levels_in_cycle) if levels_in_cycle else 100
                if min_lvl < 95:
                    is_start = True
        elif ev["type"] == "LEVEL" and current_cycle is not None:
            # Check for big time gap (>30 mins) with an increase in battery level
            prev_ev = events[i-1]
            time_gap = (ev["time"] - prev_ev["time"]).total_seconds()
            if time_gap > 1800 and ev["level"] > prev_ev["level"] + 5:
                if ev["level"] >= 90:
                    is_start = True
                    
        if is_start:
            if current_cycle:
                cycles.append(current_cycle)
            current_cycle = {
                "start_time": ev["time"],
                "start_line": ev["line"],
                "start_level": ev["level"] if ev["level"] is not None else 100,
                "start_capacity": ev.get("capacity"),
                "readings": [ev],
                "end_time": None,
                "end_level": None,
                "end_line": None,
                "status": "active"
            }
        else:
            if current_cycle:
                current_cycle["readings"].append(ev)
                if current_cycle["start_level"] is None and ev["level"] is not None:
                    current_cycle["start_level"] = ev["level"]
                if current_cycle.get("start_capacity") is None and ev.get("capacity") is not None:
                    current_cycle["start_capacity"] = ev["capacity"]
                    
    if current_cycle:
        cycles.append(current_cycle)
        
    for c in cycles:
        readings = [r for r in c["readings"] if r["type"] == "LEVEL"]
        if not readings:
            c["end_time"] = c["start_time"]
            c["end_level"] = c["start_level"]
            c["end_line"] = c["start_line"]
            c["duration_secs"] = 0
            c["status"] = "No readings"
            continue
            
        # Find minimum before charging starts
        min_val = readings[0]["level"]
        min_idx = 0
        end_idx = len(readings) - 1
        
        for idx, r in enumerate(readings):
            lvl = r["level"]
            if lvl < min_val:
                min_val = lvl
                min_idx = idx
            elif lvl > min_val + 2:
                end_idx = min_idx
                break
                
        # If reached 4%, find last level 4 reading in the discharge phase
        has_four = any(r["level"] == 4 for r in readings[:end_idx+1])
        if has_four:
            for idx in range(end_idx, -1, -1):
                if readings[idx]["level"] == 4:
                    end_idx = idx
                    break
                    
        end_reading = readings[end_idx]
        c["end_time"] = end_reading["time"]
        c["end_level"] = end_reading["level"]
        c["end_line"] = end_reading["line"]
        c["duration_secs"] = (c["end_time"] - c["start_time"]).total_seconds()
        
        # Check if the cycle is the very last one and still in progress
        is_last_reading_in_log = (end_reading == readings[-1]) and (c == cycles[-1])
        if is_last_reading_in_log and end_reading["level"] > 4:
            c["status"] = "Running (In Progress)"
        else:
            c["status"] = "Completed"
            
    return cycles

def _powershell_first_line(cmd):
    """Run a PowerShell command and return the first non-empty output line.

    Used to query system info via Get-CimInstance, which is the supported
    replacement for the deprecated `wmic` command (removed on newer Windows 11).
    """
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True
        )
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.splitlines():
                line = line.strip()
                if line:
                    return line
    except Exception:
        pass
    return ""


def _wmic_first_value(args):
    """Legacy fallback: run `wmic <args>` and return the first data row."""
    try:
        res = subprocess.run(["wmic"] + args, capture_output=True)
        if res.returncode == 0:
            try:
                out = res.stdout.decode('utf-16').strip()
            except Exception:
                out = res.stdout.decode('utf-8', errors='ignore').strip()
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) > 1:
                return lines[1]
    except Exception:
        pass
    return ""


def query_windows_info(cim_cmd, wmic_args):
    """Prefer CIM (future-proof); fall back to wmic on older systems."""
    value = _powershell_first_line(cim_cmd)
    if value:
        return value
    return _wmic_first_value(wmic_args)


def get_device_specs():
    import os
    import platform
    import subprocess
    import re
    import shutil

    system = platform.system()

    # Get total RAM in GB using sysctl (macOS) or CIM/wmic (Windows)
    ram_gb = 0
    if system == "Darwin":
        try:
            res = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
            if res.returncode == 0:
                ram_gb = round(int(res.stdout.strip()) / (1024**3))
        except Exception:
            pass
    elif system == "Windows":
        try:
            ram_bytes = query_windows_info(
                "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory",
                ["computersystem", "get", "totalphysicalmemory"],
            )
            if ram_bytes:
                ram_gb = round(int(re.sub(r'[^\d]', '', ram_bytes)) / (1024**3))
        except Exception:
            pass
            
    # Get total Disk size in GB/TB
    disk_str = ""
    try:
        path = "C:\\" if system == "Windows" else "/"
        total_bytes = shutil.disk_usage(path)[0]
        total_gb = total_bytes / (1024**3)
        standards = [128, 256, 512, 1024, 2048]
        closest = min(standards, key=lambda x: abs(x - total_gb))
        disk_str = f"{closest // 1024}TB" if closest >= 1024 else f"{closest}GB"
    except Exception:
        pass

    ram_disk_str = ""
    if ram_gb > 0:
        ram_disk_str = f"{ram_gb}GB"
        if disk_str:
            ram_disk_str = f"{ram_gb}/{disk_str}"

    if system == "Darwin":
        model = "Macbook"
        cpu = "Apple Chip"
        screen = ""
        
        # Get Model & CPU
        try:
            res = subprocess.run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if "Model Name:" in line:
                        model = line.split(":", 1)[1].strip()
                    elif "Chip:" in line:
                        cpu = line.split(":", 1)[1].strip()
        except Exception:
            pass
            
        # Get screen size from display resolution
        try:
            res = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True)
            if res.returncode == 0:
                m_res = re.findall(r'Resolution:\s*(\d+)\s*x\s*(\d+)', res.stdout)
                for w_str, h_str in m_res:
                    w, h = int(w_str), int(h_str)
                    if w == 3024 and h == 1964: screen = "14 inch"
                    elif w == 3456 and h == 2234: screen = "16 inch"
                    elif w == 2880 and h == 1864: screen = "15 inch"
                    elif (w == 2560 and h == 1664) or (w == 2560 and h == 1600): screen = "13 inch"
        except Exception:
            pass
            
        if model.lower() == "macbook pro":
            model = "Macbook Pro"
        elif model.lower() == "macbook air":
            model = "Macbook Air"
            
        cpu_clean = cpu.replace("Apple ", "")
        
        parts = [model, cpu_clean]
        if screen:
            parts.append(screen)
        if ram_disk_str:
            parts.append(ram_disk_str)
            
        return " ".join(parts)
        
    elif system == "Windows":
        model = "Windows Laptop"
        cpu = ""
        gpu = ""
        
        # Get Model
        try:
            val = query_windows_info(
                '$c = Get-CimInstance Win32_ComputerSystem; "$($c.Manufacturer) $($c.Model)"',
                ["computersystem", "get", "manufacturer,model"],
            )
            if val:
                val = re.sub(r'\s+', ' ', val).strip()
                val = val.replace("ASUSTeK COMPUTER INC.", "ASUS")
                model = val
        except Exception:
            pass

        # Get CPU
        try:
            cpu_raw = query_windows_info(
                "(Get-CimInstance Win32_Processor).Name",
                ["cpu", "get", "name"],
            )
            if cpu_raw:
                cpu = cpu_raw.replace("Intel(R) Core(TM) ", "")
                cpu = cpu.replace("AMD Ryzen ", "")
                cpu = cpu.replace(" CPU", "")
                cpu = re.sub(r'\s+@.*', '', cpu).strip()
        except Exception:
            pass

        # Get GPU
        try:
            gpu_raw = query_windows_info(
                "(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name",
                ["path", "win32_VideoController", "get", "name"],
            )
            if gpu_raw:
                gpu = gpu_raw.replace("NVIDIA GeForce ", "")
                gpu = gpu.replace(" Laptop GPU", "").strip()
        except Exception:
            pass
            
        parts = [model]
        if cpu:
            parts.append(cpu)
        if gpu and not any(igpu in gpu.lower() for igpu in ["intel", "amd", "radeon", "graphics"]):
            parts.append(gpu)
        if ram_disk_str:
            parts.append(ram_disk_str)
            
        return " ".join(parts)
        
    return "Generic Laptop"

def _capacity_values(capacity, battery_unit, voltage_mv):
    if capacity is None:
        return None, None

    try:
        raw_value = int(capacity)
    except (TypeError, ValueError):
        return None, None

    if battery_unit == "mWh":
        wh_value = raw_value / 1000.0
    elif battery_unit == "mAh" and voltage_mv:
        wh_value = (raw_value * voltage_mv) / 1000000.0
    else:
        wh_value = None

    return raw_value, wh_value


def _format_capacity(capacity, battery_unit, voltage_mv):
    raw_value, wh_value = _capacity_values(
        capacity,
        battery_unit,
        voltage_mv,
    )
    if raw_value is None:
        return "Unavailable"
    if wh_value is None:
        return f"{raw_value:,} {battery_unit}"
    return f"{wh_value:.1f} Wh ({raw_value:,} {battery_unit})"


def generate_report(cycles, design_capacity=None, full_charge_capacity=None, recent_usage=None, battery_unit="mWh", voltage_mv=None):
    device_specs = get_device_specs()
    design_raw, design_wh = _capacity_values(
        design_capacity,
        battery_unit,
        voltage_mv,
    )
    full_raw, full_wh = _capacity_values(
        full_charge_capacity,
        battery_unit,
        voltage_mv,
    )

    health = None
    wear = None
    if design_raw and full_raw is not None:
        health = (full_raw / design_raw) * 100.0
        wear = max(0.0, 100.0 - health)

    report_lines = [
        "=========================================================",
        "              LAPTOP BATTERY TEST RESULT",
        "=========================================================",
        f"Model                 : {device_specs}",
        f"Battery specs         : {_format_capacity(design_capacity, battery_unit, voltage_mv)}",
        f"Battery actual        : {_format_capacity(full_charge_capacity, battery_unit, voltage_mv)}",
    ]

    if wear is not None:
        report_lines.append(
            f"Battery wear          : {wear:.1f}% (Health {health:.1f}%)"
        )
    else:
        report_lines.append("Battery wear          : Unavailable")

    for idx, cycle in enumerate(cycles, 1):
        if len(cycles) > 1:
            report_lines.extend(["", f"Session #{idx}"])

        duration_seconds = cycle["duration_secs"]
        duration_minutes = duration_seconds / 60.0
        duration_hours = duration_seconds / 3600.0
        report_lines.extend([
            f"Test started          : {cycle['start_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"Session duration      : {duration_minutes:.1f} minutes ({duration_hours:.2f} hours)",
        ])

    report_lines.extend([
        "=========================================================",
        "DATABASE COPY-PASTE (tab-separated)",
        "\t".join([
            "Test Started",
            "Model",
            "Battery Specs Wh",
            "Battery Actual Wh",
            "Battery Wear %",
            "Session Minutes",
        ]),
    ])

    design_database = f"{design_wh:.1f}" if design_wh is not None else ""
    full_database = f"{full_wh:.1f}" if full_wh is not None else ""
    wear_database = f"{wear:.1f}" if wear is not None else ""

    for cycle in cycles:
        duration_seconds = cycle["duration_secs"]
        report_lines.append("\t".join([
            cycle["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            device_specs,
            design_database,
            full_database,
            wear_database,
            f"{duration_seconds / 60.0:.1f}",
        ]))

    report_lines.append("=========================================================")
    return "\n".join(report_lines)

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    if len(sys.argv) == 3:
        # Manual Mode (Backward Compatibility)
        start_time = sys.argv[1]
        end_time = sys.argv[2]
        try:
            t1 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            delta = t2 - t1
            print('Start time:', t1.time())
            print('End time:', t2.time())
            print(f"Time difference is {delta.total_seconds()} seconds")
            print(f"Total time difference is {convert_seconds_to_hhmmss(delta.total_seconds())} seconds")
        except ValueError as e:
            print(f"Error parsing datetimes. Expected format: YYYY-MM-DD HH:MM:SS. Error: {e}")
            sys.exit(1)
    elif len(sys.argv) == 1:
        # Automatic Log Parsing Mode
        log_file = "logfilename.log"
        if not os.path.exists(log_file):
            # Try to look for it in the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_file = os.path.join(script_dir, "logfilename.log")
            
        if not os.path.exists(log_file):
            print(f"Error: Log file 'logfilename.log' not found in current directory or script directory.")
            print("Please run the script in the directory containing the log file.")
            sys.exit(1)
            
        # Generate battery report on Windows, or get info on macOS
        design_capacity = None
        full_charge_capacity = None
        recent_usage = []
        battery_unit = "mWh"
        voltage_mv = None
        
        if platform.system() == "Windows":
            battery_unit = "mWh"
            print("Generating system battery report (powercfg /batteryreport)...")
            try:
                report_html = "battery-report.html"
                subprocess.run(["powercfg", "/batteryreport", "/output", report_html], capture_output=True, text=True)
                if os.path.exists(report_html):
                    with open(report_html, "r", encoding="utf-8", errors="ignore") as f:
                        html_content = f.read()
                    design_capacity, full_charge_capacity, recent_usage = parse_battery_report(html_content)
            except Exception as e:
                print(f"Warning: Failed to retrieve battery report: {e}")
        elif platform.system() == "Darwin": # macOS
            battery_unit = "mAh"
            print("Retrieving battery capacity information from system registry (ioreg)...")
            try:
                res = subprocess.run(["ioreg", "-rn", "AppleSmartBattery"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout:
                    m_design = re.search(r'"DesignCapacity"\s*=\s*(\d+)', res.stdout)
                    if m_design:
                        design_capacity = m_design.group(1)
                    m_max = re.search(r'"AppleRawMaxCapacity"\s*=\s*(\d+)', res.stdout)
                    if not m_max:
                        m_max = re.search(r'"MaxCapacity"\s*=\s*(\d+)', res.stdout)
                    if m_max:
                        full_charge_capacity = m_max.group(1)
                    m_volt = re.search(r'"Voltage"\s*=\s*(\d+)', res.stdout)
                    if m_volt:
                        voltage_mv = int(m_volt.group(1))
            except Exception as e:
                print(f"Warning: Failed to retrieve battery info on macOS: {e}")
            
        print(f"Reading and analyzing '{log_file}'...")
        events = parse_log_file(log_file)
        if not events:
            print("No valid events found in log file.")
            sys.exit(1)
            
        cycles = detect_cycles(events)
        report = generate_report(cycles, design_capacity, full_charge_capacity, recent_usage, battery_unit=battery_unit, voltage_mv=voltage_mv)
        
        # Print report
        print(report)
        
        # Write report to file
        report_file = "battery_report.txt"
        with open(report_file, "w", encoding="utf-8") as rf:
            rf.write(report)
        print(f"\nReport saved to: {os.path.abspath(report_file)}")
    else:
        print("Usage:")
        print("  Auto log analysis: python datetime_calculator.py")
        print("  Manual calculation: python datetime_calculator.py \"YYYY-MM-DD HH:MM:SS\" \"YYYY-MM-DD HH:MM:SS\"")
        
if __name__ == "__main__":
    main()
