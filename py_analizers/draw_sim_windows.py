#!/usr/bin/env python3
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from glob import glob



###########
#         #
# Classes #
#         #
###########



class ShannonParams:
    def __init__(self, bandwidth_mhz, mimo_layers=1, bw_efficiency=0.67,
                 sinr_offset_db=1.0, ul_divisor=2, sinr_sample_rate=100):
        self.bandwidth_mhz = bandwidth_mhz
        self.mimo_layers = mimo_layers
        self.bw_efficiency = bw_efficiency
        self.sinr_offset_db = sinr_offset_db
        self.ul_divisor = ul_divisor
        self.sinr_sample_rate = sinr_sample_rate

    def compute_capacity(self, sinr_db: np.ndarray, is_ul: bool = False) -> np.ndarray:
        adjusted_sinr = 10 ** ((sinr_db - self.sinr_offset_db) / 10.0)
        capacity = self.mimo_layers * self.bandwidth_mhz * self.bw_efficiency * np.log2(1 + adjusted_sinr)
        if is_ul:
            capacity /= self.ul_divisor
        return capacity



###################
#                 #
# Parsing methods #
#                 #
###################



# Parse MAC log (original method)

def parse_grid_log(fname: str) -> dict[int, dict[int, float]]:
    data = {}
    with open(fname, "r") as f:
        for line in f:
            tokens = [t for t in line.strip().split() if ":" in t]
            entry = {}
            for token in tokens:
                k, v = token.split(":", 1)
                try:
                    entry[k] = float(v)
                except ValueError:
                    entry[k] = v
            if {"ts", "id", "tp"} <= entry.keys():
                ue = int(entry["id"])
                sec = int(float(entry["ts"]))
                tp = entry["tp"]
                data.setdefault(ue, {}).setdefault(sec, 0.0)
                data[ue][sec] += tp
    return data



# Parse MAC log (all grid data)

def parse_grid_log_full(fname: str) -> dict[
    int, # id
    dict[
        int, # ts
        dict[
            str, # key
            float, # tp
            float, # e_tp
            float, # ts_float
            bool, # tx
            int, # f
            int, # t
            int, # m
        ]]]:
    data = {}
    with open(fname, "r") as f:
        for line in f:
            tokens = [t for t in line.strip().split() if ":" in t]
            entry = {}
            for token in tokens:
                k, v = token.split(":", 1)
                try:
                    entry[k] = float(v)
                except ValueError:
                    entry[k] = v
            if {"ts", "id", "tp"} <= entry.keys():
                ue = int(entry["id"])
                sec = int(float(entry["ts"]))
                tp = float(entry["tp"])
                e_tp = float(entry["e_tp"])
                ts_float = float(entry["ts"])
                tx = True if int(entry["tx"])==1 else False
                freq = int(entry["f"])
                time = int(entry["t"])
                m = int(entry["m"])
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("tp", 0.0)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("e_tp", 0.0)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("ts_float", 0.0)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("tx", True)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("f", 0)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("t", 0)
                data.setdefault(ue, {}).setdefault(sec, {}).setdefault("m", 0)
                data[ue][sec]["tp"] = tp
                data[ue][sec]["e_tp"] = e_tp
                data[ue][sec]["ts_float"] = ts_float
                data[ue][sec]["tx"] = tx
                data[ue][sec]["f"] = freq
                data[ue][sec]["t"] = time
                data[ue][sec]["m"] = m
    return data



# Parse SINR from UE log

def parse_sinr(fname: str) -> np.ndarray:
    sinr_vals = []
    with open(fname, "r") as f:
        for token in f.read().split():
            if token.startswith("sinr:"):
                try:
                    sinr_vals.append(float(token.split(":", 1)[1]))
                except ValueError:
                    pass
    return np.asarray(sinr_vals)



# Parse UE log

def parse_log_file_with_tx(file_path):
    data = {
        'x': [], 'y': [],

        'rsrp_ul': [], 'rsrp_dl': [],
        'sinr_ul': [], 'sinr_dl': [],

        'rul': [], 'rdl': [], 'lul': [], 'ldl': [], 'ilul': [], 'ildl': [], 'eul': [], 'edl': [], 'gul': [], 'gdl': [], 'ri': [],

        'cqi_ul': [], 'cqi_dl': [],
        'mcs_ul': [], 'mcs_dl': [],
        'eff_ul': [], 'eff_dl': [],

        'ts': [],
    }

    with open(file_path, 'r') as f:
        tx_flag = None
        for line in f:
            tokens = line.split()
            temp = {}
            for token in tokens:
                if ':' in token:
                    k, v = token.split(':', 1)
                    try:
                        temp[k] = float(v)
                    except ValueError:
                        pass
            if 'tx' in temp:
                tx_flag = int(temp['tx'])
            # The following data fields must be separated between UL and DL
            if 'sinr' in temp and tx_flag is not None:
                if tx_flag == 1:
                    data['sinr_ul'].append(temp['sinr'])
                else:
                    data['sinr_dl'].append(temp['sinr'])
            if 'rsrp' in temp and tx_flag is not None:
                if tx_flag == 1:
                    data['rsrp_ul'].append(temp['rsrp'])
                else:
                    data['rsrp_dl'].append(temp['rsrp'])

            # Coded with GitHub Copilot, may contain errors. Please review and test before use
            # (
            if 'cqi' in temp and tx_flag is not None:
                if tx_flag == 1:
                    data['cqi_ul'].append(temp['cqi'])
                else:
                    data['cqi_dl'].append(temp['cqi'])
            if 'mcs' in temp and tx_flag is not None:
                if tx_flag == 1:
                    data['mcs_ul'].append(temp['mcs'])
                else:
                    data['mcs_dl'].append(temp['mcs'])
            if 'eff' in temp and tx_flag is not None:
                if tx_flag == 1:
                    data['eff_ul'].append(temp['eff'])
                else:
                    data['eff_dl'].append(temp['eff'])
            # )

            # The following data fields does not need to be separated between UL and DL
            for key in ['x', 'y', 'rul', 'rdl', 'lul', 'ldl', 'ilul', 'ildl', 'eul', 'edl', 'gul', 'gdl', 'ri', 'ts']:
                if key in temp:
                    data[key].append(temp[key])
    return data



# Parse configuration data
# Data can be recovered in the way:
#   conf_data = parse_conf_data("<configuration file name>")
#   data = float(conf_data["<data field name>"])

def parse_conf_data(fname: str):
    conf_data = {}
    with open(fname, "r") as f:
        for line in f:
            if(str.find(line, "[UE]") > -1):
                break
            if(str.find(line, ": ") > -1):
                pair = str.split(line, ": ")
                conf_data[pair[0]] = pair[1]
    return conf_data



#########################
#                       #
# Logs managing methods #
#                       #
#########################



# Get UE log files paths list

def find_latest_ue_log(ue_dir_mac: str) -> str | None:
    files = glob(os.path.join(ue_dir_mac, "ue_log_*.txt"))
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]



# Get path to directory containing latest logs

def latest_log_dir(base_path: str) -> str:
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    if not dirs:
        print(f"[ERROR] No log directories found in {base_path}")
        sys.exit(1)
    dirs.sort(key=lambda d: os.path.getmtime(os.path.join(base_path, d)), reverse=True)
    return os.path.join(base_path, dirs[0])



# Get UE log files paths list and path to directory containing latest logs

def find_ue_logs(base_path):
    ue_dir_ues = glob(os.path.join(base_path, '*', 'ue'))
    if not ue_dir_ues:
        print(f"[ERROR] No UE log directories found in {base_path}")
        sys.exit(1)
    latest_dir = max(ue_dir_ues, key=os.path.getmtime)
    log_files = sorted(glob(os.path.join(latest_dir, 'ue_log_*.txt')))
    return latest_dir, log_files



######################
#                    #
# Processing methods #
#                    #
######################



# This method returns a the same list without NaN values

def clean_list(nan_list):
    return np.array(nan_list)[~np.isnan(nan_list)].tolist()



# Mobile mean
def mobile_mean(array, window_size):
    return np.convolve(array, np.ones(window_size) / window_size, mode='valid')



# This method returns the minimum SINR update period, which depends on Doppler effect

def sinr_update_period(freq, ue_speed): # Frequency (Hz), UE speed (m/s)

    LIGHTSPEED = 299792458 # Lightspeed (m/s)
    doppler_f = freq * ue_speed / LIGHTSPEED
    if doppler_f == 0:
        tc = np.inf
    else:
        tc = 0.423 / doppler_f
    min_sinr_update = tc / 0.001

    return min_sinr_update



# Compute Jain fairness index

def fairness(grid_data: str, n_ue, mac_sample_freq=10):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute fairness

    throughput_array = np.array([0])

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        throughput_array = np.append(throughput_array, np.sum(np.array(mbps))/len(secs))

    if np.sum(throughput_array) > 0:
        fairness = np.square(np.sum(throughput_array)) / (n_ue * np.sum(np.square(throughput_array)))
    else:
        fairness = np.nan

    return fairness



# Compute aggregate cell throughput

def aggregate_throughput(grid_data: str, mac_sample_freq=10):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute throughput

    throughput_array = np.array([0])

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        throughput_array = np.append(throughput_array, np.sum(np.array(mbps))/len(secs))

    agg_throughput = np.sum(throughput_array)

    return agg_throughput



# Compute average user throughput

def average_throughput(grid_data: str, n_ue, mac_sample_freq=10):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute throughput

    throughput_array = np.array([0])

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        throughput_array = np.append(throughput_array, np.sum(np.array(mbps))/len(secs))

    ave_throughput = np.sum(throughput_array)/n_ue

    return ave_throughput



# Compute spectral efficiency

def spectral_efficiency(grid_data: str, bandwidth=20e6, mac_sample_freq=10):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute area spectral efficiency

    throughput_array = np.array([0])

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        throughput_array = np.append(throughput_array, np.sum(np.array(mbps))/len(secs))

    agg_throughput = np.sum(throughput_array)

    se = agg_throughput*1e6/bandwidth

    return se



# Compute area spectral efficiency

def area_spectral_efficiency(grid_data: str, bandwidth=20e6, cell_radius=1e3, mac_sample_freq=10):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute area spectral efficiency

    cell_area = np.pi*np.square(cell_radius)

    throughput_array = np.array([0])

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        throughput_array = np.append(throughput_array, np.sum(np.array(mbps))/len(secs))

    agg_throughput = np.sum(throughput_array)

    ase = agg_throughput*1e6/(bandwidth*cell_area)

    return ase



# Compute generation rate

def generation_rate(all_data, direction):

    if str.find("UL", direction) == 0:
        gen_key = "gul"
    elif str.find("DL", direction) == 0:
        gen_key = "gdl"
    else:
        gen_key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    gr_list = []

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[gen_key]:
            continue

        gr = np.sum(data[gen_key])/len(data[gen_key])

        gr_list.append(float(gr))

    return gr_list



# Compute throughput rate

def throughput_rate(all_data, direction):

    if str.find("UL", direction) == 0:
        key = "rul"
    elif str.find("DL", direction) == 0:
        key = "rdl"
    else:
        key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    tr_list = []

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        tr = np.sum(data[key])/len(data[key])

        tr_list.append(float(tr))

    return tr_list



# Compute error rate (Mbps)

def error_rate_mbps(all_data, direction):

    if str.find("UL", direction) == 0:
        key = "eul"
    elif str.find("DL", direction) == 0:
        key = "edl"
    else:
        key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    er_list = []

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        er = np.sum(data[key])/len(data[key])

        er_list.append(float(er))

    return er_list



# Compute error rate (ratio)

def error_rate_ratio(all_data, direction):

    er = np.array(error_rate_mbps(all_data, direction))
    tr = np.array(throughput_rate(all_data, direction))

    er_plus_tr = er+tr

    # Avoid division by 0. We suppose that when traffic is 0, error rate is also 0, so the result will always be 0
    er_plus_tr[np.argwhere(er_plus_tr==0)]=1

    err = np.divide(er, er_plus_tr)

    return err.tolist()



# Compute success rate (ratio)

def success_rate_ratio(all_data, direction):

    er = np.array(error_rate_mbps(all_data, direction))
    tr = np.array(throughput_rate(all_data, direction))

    er_plus_tr = er+tr

    # Avoid division by 0. We suppose that when traffic is 0, error rate is also 0, so the result will always be 0
    er_plus_tr[np.argwhere(er_plus_tr==0)]=1
    err = np.divide(tr, er_plus_tr)
    err[np.argwhere(er_plus_tr==0)] = 1

    return err.tolist()



# Compute average latency

def average_latency(all_data, direction):

    if str.find("UL", direction) == 0:
        key = "lul"
    elif str.find("DL", direction) == 0:
        key = "ldl"
    else:
        key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    l_list = []

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        ave_l = np.sum(data[key])/len(data[key])

        l_list.append(float(ave_l))

    return l_list



# Compute average IP latency

def average_ip_latency(all_data, direction):

    if str.find("UL", direction) == 0:
        key = "ilul"
    elif str.find("DL", direction) == 0:
        key = "ildl"
    else:
        key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    il_list = []

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        ave_il = np.sum(data[key])/len(data[key])

        il_list.append(float(ave_il))

    return il_list



# Get the aggregate data

def aggregate_data(all_data, key):

    agg_data = []
    for i, data in enumerate(all_data):
        if not data[key]:
            continue
        agg_data = agg_data + data[key]

    return agg_data



# Get the data for an histogram with the data indicated in "key" for all UE

def histograms_all_ue(all_data, key, bins):
    plot_data = aggregate_data(all_data, key)

    return np.histogram(plot_data, bins=bins, density=True)



############################
#                          #
# Plotting methods for MAC #
#                          #
############################



# Plot instant throughput per UE

def draw_time_series(output_dir: str, grid_data: str, ue_log: str | None, direction: str, shannon_cfg: ShannonParams, ue_sample_freq=10, mac_sample_freq=10, period=1):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute values

    # Shannon Limit
    capacity_vals, capacity_secs = [], []
    if ue_log:
        sinr_all = parse_sinr(ue_log)
        if sinr_all.size:
            sinr_dir = sinr_all[0::2] if direction == "DL" else sinr_all[1::2]
            C_samples = shannon_cfg.compute_capacity(sinr_dir, is_ul=(direction == "UL"))
            n_seconds = len(C_samples) // shannon_cfg.sinr_sample_rate
            capacity_vals = [np.mean(C_samples[i*shannon_cfg.sinr_sample_rate:(i+1)*shannon_cfg.sinr_sample_rate])
                             for i in range(n_seconds)]
            capacity_secs = list(range(n_seconds))



    # 3. Plot data

    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap("tab10")

    # Iterate along UEs
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):
        plt.plot(
            secs, # Time (seconds)
            mbps, # Throughput (Mbps)
            linestyle="-", marker="o", linewidth=2, color=cmap(idx % cmap.N), label=f"UE {ue}"
        )

    # Shannon Limit
    # if capacity_secs:
    #     plt.plot(
    #         capacity_secs, # Time (seconds)
    #         capacity_vals, # Shannon Limit (Mbps)
    #         "k--", linewidth=2, label="Modified Shannon Limit"
    #     )

    plt.xlabel("Time (seconds)")
    plt.ylabel(f"Throughput {direction} (Mbps)")
    plt.title(f"{direction} Throughput vs Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()



    # 4. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_throughput.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot instant total throughput and instant average throughput per UE

def draw_time_series_all(output_dir: str, grid_data: str, ue_log: str | None, direction: str, shannon_cfg: ShannonParams, ue_sample_freq=10, mac_sample_freq=10, period=1):



    # 1. Get data

    SAMPLE_FREQ = mac_sample_freq
    K2M = 1e-3

    ue_lines = {}
    for ue, sec_dict in grid_data.items():
        secs = sorted(sec_dict.keys()) # Time (seconds)
        mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
        ue_lines[ue] = (secs, mbps)



    # 2. Compute values

    # Shannon Limit
    capacity_vals, capacity_secs = [], []
    if ue_log:
        sinr_all = parse_sinr(ue_log)
        if sinr_all.size:
            sinr_dir = sinr_all[0::2] if direction == "DL" else sinr_all[1::2]
            C_samples = shannon_cfg.compute_capacity(sinr_dir, is_ul=(direction == "UL"))
            n_seconds = len(C_samples) // shannon_cfg.sinr_sample_rate
            capacity_vals = [np.mean(C_samples[i*shannon_cfg.sinr_sample_rate:(i+1)*shannon_cfg.sinr_sample_rate])
                             for i in range(n_seconds)]
            capacity_secs = list(range(n_seconds))

    # Total throughput and throughput per ue
    np_mbps_total = np.array([])
    np_secs = np.array([])
    n_ue = len(ue_lines.items())
    # for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):
    #     np_mbps_total = np.zeros([len(mbps)])
    #     np_secs = np.array(secs)
    #     break
    for idx, (ue, (secs, mbps)) in enumerate(ue_lines.items()):

        # Get UE throughput
        np_mbps = np.array(mbps)

        # Fix throughput array length
        if len(np_mbps_total) < len(np_mbps):
            np_mbps_total = np.append(np_mbps_total, np.zeros([len(np_mbps)-len(np_mbps_total)]))
        if len(np_mbps_total) > len(np_mbps):
            np_mbps = np.append(np_mbps, np.zeros([len(np_mbps_total)-len(mbps)]))

        # Add throughput
        np_mbps_total = np_mbps_total + np_mbps

        # Fix seconds array length
        if len(np_secs) < len(secs):
            np_secs = np.array(secs)

    mbps_total = np_mbps_total.tolist()
    mbps_per_ue = (np_mbps_total/n_ue).tolist()
    secs = np_secs.tolist()



    # 3. Plot data

    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap("tab10")

    plt.plot(
        secs, # Time (seconds)
        mbps_total, # Throughput (Mbps)
        linestyle="-", marker="o", linewidth=2, color=cmap(0 % cmap.N), label="Total throughput"
    )
    plt.plot(
        secs, # Time (seconds)
        mbps_per_ue, # Throughput (Mbps)
        linestyle="-", marker="o", linewidth=2, color=cmap(1 % cmap.N), label="Throughput per UE"
    )

    # Shannon Limit
    # if capacity_secs:
    #     plt.plot(
    #         capacity_secs, # Time (seconds)
    #         capacity_vals, # Shannon Limit (Mbps)
    #         "k--", linewidth=2, label="Modified Shannon Limit"
    #     )

    plt.xlabel("Time (seconds)")
    plt.ylabel(f"Throughput {direction} (Mbps)")
    plt.title(f"{direction} Throughput vs Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()



    # 4. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_throughput_all.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot cummulative distribution function (CDF) of normalized average UE throughput

def draw_cdf(output_dir: str, grid_file: str, direction: str):
    ue_totals, ue_seconds = {}, {}
    with open(grid_file, "r") as f:
        for line in f:
            tokens = [t for t in line.strip().split() if ":" in t]
            entry = {}
            for token in tokens:
                k, v = token.split(":", 1)
                try:
                    entry[k] = float(v)
                except ValueError:
                    entry[k] = v
            if {"id", "tp", "ts"} <= entry.keys():
                ue = int(entry["id"])
                tp = float(entry["tp"])
                sec = int(float(entry["ts"]))
                ue_totals.setdefault(ue, 0.0)
                ue_seconds.setdefault(ue, set()).add(sec)
                ue_totals[ue] += tp

    ue_avg = {ue: (tp / len(ue_seconds[ue])) * 1e-3 for ue, tp in ue_totals.items() if len(ue_seconds[ue]) > 0}

    if len(ue_avg) == 0:
        print("[WARN] No valid UE data for CDF.")
        return

    norm_avg = np.array(list(ue_avg.values()))
    if len(ue_avg) > 1:
        norm_avg /= (len(ue_avg) * 30)

    sorted_vals = np.sort(norm_avg)
    cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

    plt.figure(figsize=(8, 6))
    plt.plot(sorted_vals, cdf, linewidth=2)
    plt.xlabel("Normalized Average UE Throughput (Mbps per UE)")
    plt.ylabel("CDF")
    plt.title(f"CDF of Normalized UE Throughput ({direction})")
    plt.grid(True)
    plt.tight_layout()

    out_png = os.path.join(output_dir, f"cdf_throughput_{direction}.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



###########################
#                         #
# Plotting methods for UE #
#                         #
###########################



# Encode a "i" color for a space of size "N"

def cmapNcolors(i, N):
    side = int(np.cbrt(N))+1
    #n_colors = np.pow(side, 3)
    count=0
    for R in range(side):
        for G in range(side):
            for B in range(side):
                if(count == i):
                    return tuple((np.array((R, G, B))/N).tolist())
                count = count+1
    return (-1, -1, -1)



# Plot an histogram with the data indicated in "key_ul" and "key_dl" for each UE

def plot_histograms_ul_dl_per_ue(all_data, key_ul, key_dl, title, xlabel, outname, bins, outdir, figsize=(10,10)):
    fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)
    cmap = plt.get_cmap("tab20")
    for i, data in enumerate(all_data):
        color=cmap(i % cmap.N)
        #color=cmapNcolors(i, 20)
        if data[key_ul]:
            axs[0].hist(
                clean_list(data[key_ul]),
                bins=bins, alpha=0.5, label=f"UE {i}", color=color, density=True, edgecolor='black')
        if data[key_dl]:
            axs[1].hist(
                clean_list(data[key_dl]),
                bins=bins, alpha=0.5, label=f"UE {i}", color=color, density=True, edgecolor='black')
    axs[0].set_title(f"{title} (UL)")
    axs[1].set_title(f"{title} (DL)")
    axs[1].set_xlabel(xlabel)
    axs[0].legend()
    axs[1].legend()
    axs[0].grid(True)
    axs[1].grid(True)
    fig.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot an histogram with the data indicated in "key_ul" and "key_dl" for all UE

def plot_histograms_ul_dl_all_ue(all_data, key_ul, key_dl, title, xlabel, outname, bins, outdir, figsize=(10,10)):
    fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)

    plot_data_ul = aggregate_data(all_data, key_ul)
    plot_data_dl = aggregate_data(all_data, key_dl)
    axs[0].hist(plot_data_ul, bins=bins, alpha=0.5, label=f"{title} (UL)", density=True, edgecolor='black')
    axs[1].hist(plot_data_dl, bins=bins, alpha=0.5, label=f"{title} (DL)", density=True, edgecolor='black')

    # (hist_data_ul, x_ul) = histograms_all_ue(all_data, key_ul, bins)
    # (hist_data_dl, x_dl) = histograms_all_ue(all_data, key_dl, bins)
    # axs[0].bar(x_ul, hist_data_ul, alpha=0.5, label=f"{title} (UL)", edgecolor='black')
    # axs[1].bar(x_dl, hist_data_dl, alpha=0.5, label=f"{title} (DL)", edgecolor='black')

    axs[0].set_title(f"{title} (UL)")
    axs[1].set_title(f"{title} (DL)")
    axs[1].set_xlabel(xlabel)
    axs[0].legend()
    axs[1].legend()
    axs[0].grid(True)
    axs[1].grid(True)
    fig.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot an histogram with the data indicated in "key" for each UE

def plot_histograms_per_ue(all_data, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):
    plt.figure(figsize=figsize)
    cmap = plt.get_cmap("tab20")
    for i, data in enumerate(all_data):
        if not data[key]:
            continue
        color=cmap(i % cmap.N)
        #color=cmapNcolors(i, 20)
        plt.hist(data[key], bins=bins, alpha=0.5, label=f"UE {i}", density=True, edgecolor='black', color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot an histogram with the data indicated in "key" for all UE

def plot_histograms_all_ue(all_data, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):
    plt.figure(figsize=figsize)

    plot_data = aggregate_data(all_data, key)
    plt.hist(plot_data, bins=bins, alpha=0.5, label=title, density=True, edgecolor='black')

    # (hist_data, x) = histograms_all_ue(all_data, key, bins)
    # plt.bar(x, hist_data, alpha=0.5, label=title, edgecolor='black')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot instantaneous trajectory per UE

def plot_combined_trajectory(all_data, outdir):
    plt.figure(figsize=(10, 10))
    cmap = plt.get_cmap("tab10")
    for i, data in enumerate(all_data):
        x, y = data['x'], data['y']
        if not x or not y:
            continue
        plt.plot(x, y, label=f"UE {i}", alpha=0.6, color=cmap(i % cmap.N))
        plt.plot(x[0], y[0], 'o', color=cmap(i % cmap.N))
        plt.plot(x[-1], y[-1], 's', color=cmap(i % cmap.N))
    plt.plot(0, 0, 'kp', label='Base Station', markersize=10)
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.title("UE Trajectories")
    plt.tight_layout()
    path = os.path.join(outdir, "trajectory.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot instantaneous speed per UE

def plot_speed(all_data, outdir, step=3):
    
    plt.figure(figsize=(10, 10))
    cmap = plt.get_cmap("tab10")
    for i, data in enumerate(all_data):
        x, y = data['x'], data['y']
        if not x or not y:
            continue
        # step = int(len(data['ts'])/len(x))
        ts = np.array(data['ts'][0::step]) # Position timestampt is one of each set, depending on logged information

        # Fix arrays
        if len(x) < len(y) and len(x) < len(ts):
            x_fixed = x
            y_fixed = y[0:len(x)]
            ts_fixed = ts[0:len(x)]
        elif len(y) < len(x) and len(y) < len(ts):
            x_fixed = x[0:len(y)]
            y_fixed = y
            ts_fixed = ts[0:len(y)]
        else:
            x_fixed = x[0:len(ts)]
            y_fixed = y[0:len(ts)]
            ts_fixed = ts

        distance = np.sqrt(np.diff(x_fixed)**2 + np.diff(y_fixed)**2)
        speed = distance / np.diff(ts_fixed)  # Speed = distance / time
        plt.plot(ts_fixed[:-1], speed, label=f"UE {i}", alpha=0.6, color=cmap(i % cmap.N))
    plt.title("UE Speed Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (m/s)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, "speed.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot instantaneous acceleration per UE

def plot_acceleration(all_data, outdir, step=3):
    plt.figure(figsize=(10, 10))
    cmap = plt.get_cmap("tab10")
    for i, data in enumerate(all_data):
        x, y = data['x'], data['y']
        if not x or not y:
            continue
        # step = int(len(data['ts'])/len(x))
        ts = np.array(data['ts'][0::step]) # Position timestampt is one of each set, depending on logged information

        # Fix arrays
        if len(x) < len(y) and len(x) < len(ts):
            x_fixed = x
            y_fixed = y[0:len(x)]
            ts_fixed = ts[0:len(x)]
        elif len(y) < len(x) and len(y) < len(ts):
            x_fixed = x[0:len(y)]
            y_fixed = y
            ts_fixed = ts[0:len(y)]
        else:
            x_fixed = x[0:len(ts)]
            y_fixed = y[0:len(ts)]
            ts_fixed = ts

        speed = np.sqrt(np.diff(x_fixed)**2 + np.diff(y_fixed)**2) / np.diff(ts_fixed)  # Speed = distance / time
        acceleration = np.diff(speed)
        plt.plot(ts_fixed[:-2], acceleration, label=f"UE {i}", alpha=0.6, color=cmap(i % cmap.N))
    plt.title("UE Acceleration Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s^2)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, "acceleration.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot instantaneous distance to eNB per UE

def plot_distance(all_data, outdir, step=3):
    
    plt.figure(figsize=(10, 10))
    cmap = plt.get_cmap("tab10")
    for i, data in enumerate(all_data):
        x, y = data['x'], data['y']
        if not x or not y:
            continue
        # step = int(len(data['ts'])/len(x))
        ts = np.array(data['ts'][0::step]) # Position timestampt is one of each set, depending on logged information

        # Fix arrays
        if len(x) < len(y) and len(x) < len(ts):
            x_fixed = x
            y_fixed = y[0:len(x)]
            ts_fixed = ts[0:len(x)]
        elif len(y) < len(x) and len(y) < len(ts):
            x_fixed = x[0:len(y)]
            y_fixed = y
            ts_fixed = ts[0:len(y)]
        else:
            x_fixed = x[0:len(ts)]
            y_fixed = y[0:len(ts)]
            ts_fixed = ts

        dist = np.sqrt(np.square(x_fixed) + np.square(y_fixed))
        plt.plot(ts_fixed, dist, label=f"UE {i}", alpha=0.6, color=cmap(i % cmap.N))
    plt.title("UE distance to eNB")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (m)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, "distance.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot instantaneous value of the parameter indicated as a key. This method does not work for the following parameters: sinr, rsrp, cqi, mcs, eff, ri, tx

def plot_instantaneous_value(all_data, outdir, key, step=3, window_size=1000):

    plt.figure(figsize=(10, 10))
    cmap = plt.get_cmap("tab10")
    for i, data in enumerate(all_data):
        val = data[key]
        if not val:
            continue
        # step = int(len(data['ts'])/len(x))
        ts = np.array(data['ts'][0::step]) # Position timestampt is one of each set, depending on logged information

        # Mobile mean
        val = mobile_mean(val, window_size)

        # Fix arrays
        if len(val) < len(ts):
            val_fixed = val
            ts_fixed = ts[0:len(val)]
        else:
            val_fixed = val[0:len(ts)]
            ts_fixed = ts

        plt.plot(ts_fixed, val_fixed, label=f"UE {i}", alpha=0.6, color=cmap(i % cmap.N))
    plt.title(key)
    plt.xlabel("Time (s)")
    plt.ylabel(key)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, key+"_instantaneous.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot cummulative distribution function (CDF) of normalized average UE throughput (alternative way)

def draw_cdf_alt(all_data, outdir, direction):

    if str.find("UL", direction) == 0:
        key = "rul"
    elif str.find("DL", direction) == 0:
        key = "rdl"
    else:
        key = ""
        print(f"[ERROR]: Invalid parameter {direction}")

    tr = np.array([])

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        tr = np.append(tr, np.array(data[key]))

        # ACABAR DESDE AQUÍ
        # sorted_vals = np.sort(norm_avg)
        # cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

    plt.figure(figsize=(8, 6))
    plt.ecdf(tr, weights=None, complementary=False, orientation='vertical', compress=False, data=None)
    # plt.plot(sorted_vals, cdf, linewidth=2)
    plt.xlabel("Normalized Average UE Throughput (Mbps per UE)")
    plt.ylabel("CDF")
    plt.title(f"CDF of Normalized UE Throughput ({direction})")
    plt.grid(True)
    plt.tight_layout()

    out_png = os.path.join(outdir, f"cdf_alt_throughput_{direction}.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot cummulative distribution function (CDF) of the parameter indicated as a key

def draw_cdf_param(all_data, key, outdir):

    val = np.array([])

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        val = np.append(val, np.array(data[key]))

    plt.figure(figsize=(8, 6))
    plt.ecdf(val, weights=None, complementary=False, orientation='vertical', compress=False, data=None)
    plt.xlabel(f"CDF for {key}")
    plt.ylabel("CDF")
    plt.title(f"{key}")
    plt.grid(True)
    plt.tight_layout()

    out_png = os.path.join(outdir, f"cdf_{key}.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot complementary cummulative distribution function (CCDF) of the parameter indicated as a key

def draw_ccdf_param(all_data, key, outdir):

    val = np.array([])

    # Iterate along UEs
    for i, data in enumerate(all_data):

        if not data[key]:
            continue

        val = np.append(val, np.array(data[key]))

    plt.figure(figsize=(8, 6))
    plt.ecdf(val, weights=None, complementary=True, orientation='vertical', compress=False, data=None)
    plt.xlabel(f"CCDF for {key}")
    plt.ylabel("CCDF")
    plt.title(f"{key}")
    plt.grid(True)
    plt.tight_layout()

    out_png = os.path.join(outdir, f"ccdf_{key}.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



def main():



    # 0. Previous steps

    # Print help
    if(len(sys.argv)>1):
        if str.find(sys.argv[1], "--help") == 0:
            print("Expected arguments: <results directory> <logs directory containing a \"ue\" directory and a \"mac\" directory>")
            exit()

    # Script directory
    script_dir_ue = os.path.dirname(os.path.realpath(sys.argv[0]))
    script_dir_mac = os.path.dirname(os.path.abspath(__file__))



    # 1. Logs managing for UE

    # Logs directory
    logs_base_ue = os.path.join(script_dir_ue, '..', 'logs')

    # UE logs directory (ue_dir_ue) and UE logs (log_files)
    logs_dir = sys.argv[2]
    ue_dir_ue = os.path.join(logs_dir, 'ue')
    log_files = sorted(glob(os.path.join(ue_dir_ue, 'ue_log_*.txt')))

    # Logs directory (normalized)
    log_folder_ue = os.path.basename(os.path.dirname(ue_dir_ue))

    # Get UE data
    all_data = [parse_log_file_with_tx(f) for f in log_files]



    # 1. Logs managing for MAC

    # Logs directory
    logs_base_mac = os.path.join(script_dir_mac, "..", "logs")

    # MAC and UE logs directory
    logs_dir = sys.argv[2]
    latest_log = logs_dir

    # Logs directory (normalized)
    log_folder_mac = os.path.basename(os.path.normpath(latest_log))

    # MAC logs directory
    mac_dir = os.path.join(latest_log, "mac")

    # UE logs directory
    ue_dir_mac = os.path.join(latest_log, "ue")

    # UE logs (ue_log)
    ue_log = find_latest_ue_log(ue_dir_mac) if os.path.isdir(ue_dir_mac) else None

    # MAC logs
    ul_file = os.path.join(mac_dir, "grid_log_ul.txt")
    dl_file = os.path.join(mac_dir, "grid_log_dl.txt")
    if not (os.path.exists(ul_file) or os.path.exists(dl_file)):
        print("[ERROR] UL or DL grid logs not found.")
        sys.exit(1)

    # Get MAC data
    dl_data = parse_grid_log(dl_file)
    ul_data = parse_grid_log(ul_file)



    # 2. Results managing for UE

    # UE results directory
    results_dir = sys.argv[1]
    out_dir = os.path.join(results_dir, "ue")
    os.makedirs(out_dir, exist_ok=True)



    # 2. Results managing for MAC

    # MAC results directory
    results_dir = sys.argv[1]
    results_base = os.path.join(results_dir, "mac")
    os.makedirs(results_base, exist_ok=True)



    # 3. Simulation data

    # From configuration file
    if(len(sys.argv)>3): # If data is not indicated as a parameter, default values are used
        # Period
        period=float(sys.argv[3])
        # Logging rate (UE)
        ue_log_freq=int(sys.argv[4])
        # Logging rate (MAC)
        mac_log_freq=int(sys.argv[5])
        # MIMO layers
        mimo_layers=int(sys.argv[6])
        # Frequency
        frequency=float(sys.argv[7])
        # Bandwidth
        bandwidth=float(sys.argv[8])
        # UE speed
        ue_speed=float(sys.argv[9])
        # Max distance
        max_distance=float(sys.argv[10])
        # Shannon parameters
        bw_efficiency=float(sys.argv[11])
        sinr_offset_db=float(sys.argv[12])
        ul_divisor=float(sys.argv[13])
    else:
        # Period
        period=1
        # Logging rate (UE)
        ue_log_freq=1000
        # Logging rate (MAC)
        mac_log_freq=1000
        # MIMO layers
        mimo_layers = 2
        # Frequency
        frequency = 2412000000.0
        # Bandwidth
        bandwidth = 50000000
        # UE speed
        ue_speed = 20*1e3/3600
        # Max distance
        max_distance = 1000
        # Shannon parameters
        bw_efficiency=0.67
        sinr_offset_db=0
        ul_divisor=2
    # Shannon parameters
    shannon_cfg = ShannonParams(
        bandwidth_mhz=bandwidth/1e6,
        mimo_layers=mimo_layers,
        bw_efficiency=bw_efficiency,
        sinr_offset_db=sinr_offset_db,
        ul_divisor=ul_divisor,
        sinr_sample_rate=int(ue_log_freq/period)
    )

    # Computed values
    # Number of UEs
    n_ue = len(all_data)
    # Doppler effect computations
    sinr_period = sinr_update_period(frequency, ue_speed)
    sinr_rate = 1/(sinr_period/1e3)
    # Fairness
    try: ul_fairness = fairness(ul_data, n_ue, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_fairness = fairness(dl_data, n_ue, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    # Aggregate cell throughput
    try: ul_agg_throughput = aggregate_throughput(ul_data, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_agg_throughput = aggregate_throughput(dl_data, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    # Average user throughput
    try: ul_ave_throughput = average_throughput(ul_data, n_ue, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_ave_throughput = average_throughput(dl_data, n_ue, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    # Spectral efficiency
    try: ul_se = spectral_efficiency(ul_data, bandwidth=bandwidth, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_se = spectral_efficiency(dl_data, bandwidth=bandwidth, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    # Area spectral efficiency
    try: ul_ase = area_spectral_efficiency(ul_data, bandwidth=bandwidth, cell_radius=max_distance, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_ase = area_spectral_efficiency(dl_data, bandwidth=bandwidth, cell_radius=max_distance, mac_sample_freq=mac_log_freq)
    except: print("[INFO]: Error in draw_sim.py")
    # Generation rate
    try: ul_gr = generation_rate(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_gr = generation_rate(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    # Throughput rate
    try: ul_tr = throughput_rate(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_tr = throughput_rate(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    # Error rate
    try: ul_er = error_rate_mbps(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_er = error_rate_mbps(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    try: ul_er_ratio = error_rate_ratio(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_er_ratio = error_rate_ratio(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    try: ul_er_perc = (100*np.array(ul_er_ratio)).tolist()
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_er_perc = (100*np.array(dl_er_ratio)).tolist()
    except: print("[INFO]: Error in draw_sim.py")
    # Latency
    try: ul_l = average_latency(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_l = average_latency(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    # IP latency
    try: ul_il = average_ip_latency(all_data, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: dl_il = average_ip_latency(all_data, "DL")
    except: print("[INFO]: Error in draw_sim.py")

    # Values are logged
    if(len(sys.argv)>1): # If output directory is not indicated, it is supposed to be in emulator directory
        results_dir = sys.argv[1]
    else:
        results_dir = os.path.join(script_dir_mac, "..", "results", log_folder_mac)
    post_processing_path = os.path.join(results_dir, "post_processing.txt")
    with open(post_processing_path, 'w') as f:
        try: f.write(f"period:{period}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ue_log_freq:{ue_log_freq}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mac_log_freq:{mac_log_freq}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mimo_layers:{mimo_layers}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"frequency:{frequency}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"bandwidth:{bandwidth}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ue_speed:{ue_speed}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"max_distance:{max_distance}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_bandwidth_mhz:{shannon_cfg.bandwidth_mhz}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_mimo_layers:{shannon_cfg.mimo_layers}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_bw_efficiency:{shannon_cfg.bw_efficiency}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_sinr_offset_db:{shannon_cfg.sinr_offset_db}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_ul_divisor:{shannon_cfg.ul_divisor}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"shannon_cfg_sinr_sample_rate:{shannon_cfg.sinr_sample_rate}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"n_ue:{n_ue}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"sinr_period:{sinr_period}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"sinr_rate:{sinr_rate}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f'ul_fairness:{ul_fairness}\n')
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f'dl_fairness:{dl_fairness}\n')
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_agg_throughput:{ul_agg_throughput}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_agg_throughput:{dl_agg_throughput}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_ave_throughput:{ul_ave_throughput}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_ave_throughput:{dl_ave_throughput}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_se:{ul_se}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_se:{dl_se}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_ase:{ul_ase}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_ase:{dl_ase}\n")
        except: print("[INFO]: Error in draw_sim.py")

        try: f.write(f"ul_gr:{str(ul_gr)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_gr:{str(dl_gr)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_tr:{str(ul_tr)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_tr:{str(dl_tr)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_er:{str(ul_er)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_er:{str(dl_er)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_er_ratio:{str(ul_er_ratio)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_er_ratio:{str(dl_er_ratio)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_er_perc:{str(ul_er_perc)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_er_perc:{str(dl_er_perc)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_l:{str(ul_l)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_l:{str(dl_l)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ul_il:{str(ul_il)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"dl_il:{str(dl_il)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")

        try: f.write(f"sinr_ul:{np.array2string(histograms_all_ue(all_data, 'sinr_ul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"sinr_ul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'sinr_ul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"sinr_dl:{np.array2string(histograms_all_ue(all_data, 'sinr_dl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"sinr_dl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'sinr_dl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rsrp_ul:{np.array2string(histograms_all_ue(all_data, 'rsrp_ul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rsrp_ul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'rsrp_ul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rsrp_dl:{np.array2string(histograms_all_ue(all_data, 'rsrp_dl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rsrp_dl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'rsrp_dl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"cqi_ul:{np.array2string(histograms_all_ue(all_data, 'cqi_ul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"cqi_ul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'cqi_ul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"cqi_dl:{np.array2string(histograms_all_ue(all_data, 'cqi_dl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"cqi_dl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'cqi_dl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mcs_ul:{np.array2string(histograms_all_ue(all_data, 'mcs_ul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mcs_ul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'mcs_ul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mcs_dl:{np.array2string(histograms_all_ue(all_data, 'mcs_dl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"mcs_dl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'mcs_dl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eff_ul:{np.array2string(histograms_all_ue(all_data, 'eff_ul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eff_ul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'eff_ul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eff_dl:{np.array2string(histograms_all_ue(all_data, 'eff_dl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eff_dl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'eff_dl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rul:{np.array2string(histograms_all_ue(all_data, 'rul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'rul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rdl:{np.array2string(histograms_all_ue(all_data, 'rdl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"rdl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'rdl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"lul:{np.array2string(histograms_all_ue(all_data, 'lul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"lul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'lul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ldl:{np.array2string(histograms_all_ue(all_data, 'ldl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ldl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'ldl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ilul:{np.array2string(histograms_all_ue(all_data, 'ilul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ilul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'ilul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ildl:{np.array2string(histograms_all_ue(all_data, 'ildl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ildl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'ildl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eul:{np.array2string(histograms_all_ue(all_data, 'eul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"eul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'eul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"edl:{np.array2string(histograms_all_ue(all_data, 'edl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"edl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'edl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"gul:{np.array2string(histograms_all_ue(all_data, 'gul', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"gul_bin_edges:{np.array2string(histograms_all_ue(all_data, 'gul', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"gdl:{np.array2string(histograms_all_ue(all_data, 'gdl', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"gdl_bin_edges:{np.array2string(histograms_all_ue(all_data, 'gdl', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ri:{np.array2string(histograms_all_ue(all_data, 'ri', bins=40)[0], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")
        try: f.write(f"ri_bin_edges:{np.array2string(histograms_all_ue(all_data, 'ri', bins=40)[1], separator=",", max_line_width=np.inf)[1:-1]}\n")
        except: print("[INFO]: Error in draw_sim.py")

    try:
        # Values are printed
        print(f"Number of UEs: {n_ue}")
        print(f"Minimum SINR update period (ms): {sinr_period}")
        print(f"Minimum SINR update rate (Hz): {sinr_rate}")
        print(f'Fairness (UL): {ul_fairness}')
        print(f'Fairness (DL): {dl_fairness}')
        print(f"Aggregate cell throughput (Mbps, UL): {ul_agg_throughput}")
        print(f"Aggregate cell throughput (Mbps, UL): {dl_agg_throughput}")
        print(f"Average user throughput (Mbps, UL): {ul_ave_throughput}")
        print(f"Average user throughput (Mbps, UL): {dl_ave_throughput}")
        print(f"Spectral efficiency ([b/s]/Hz, UL): {ul_se}")
        print(f"Spectral efficiency ([b/s]/Hz, DL): {dl_se}")
        print(f"Area spectral efficiency ([b/s]/[Hz · m^2], UL): {ul_ase}")
        print(f"Area spectral efficiency ([b/s]/[Hz · m^2], DL): {dl_ase}")
        print(f"Generation rate (Mbps, all UEs, UL): {ul_gr}")
        print(f"Generation rate (Mbps, all UEs, DL): {dl_gr}")
        print(f"Throughput rate (Mbps, all UEs, UL): {ul_tr}")
        print(f"Throughput rate (Mbps, all UEs, DL): {dl_tr}")
        print(f"Error rate (Mbps, all UEs, UL): {ul_er}")
        print(f"Error rate (Mbps, all UEs, DL): {dl_er}")
        print(f"Error rate (ratio, all UEs, UL): {ul_er_ratio}")
        print(f"Error rate (ratio, all UEs, DL): {dl_er_ratio}")
        print(f"Error rate (%, all UEs, UL): {ul_er_perc}")
        print(f"Error rate (%, all UEs, DL): {dl_er_perc}")
        print(f"Average latency (s, all UEs, UL): {ul_l}")
        print(f"Average latency (s, all UEs, DL): {dl_l}")
        print(f"Average IP latency (s, all UEs, UL): {ul_il}")
        print(f"Average IP latency (s, all UEs, DL): {dl_il}")
    except: print("[INFO]: Error in draw_sim.py")



    # 4. Generate graphs for UE

    # These plots use to cause errors for a huge number of UEs
    try: plot_combined_trajectory(all_data, out_dir)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_speed(all_data, out_dir)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_acceleration(all_data, out_dir)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_distance(all_data, out_dir)
    except: print("[INFO]: Error in draw_sim.py")

    frac = 0.5 # Fraction of a second
    window_size = int(frac*1000*1/period)
    try: plot_instantaneous_value(all_data, out_dir, 'rul', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'rdl', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'lul', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'ldl', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'ilul', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'ildl', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'eul', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'edl', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'gul', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_instantaneous_value(all_data, out_dir, 'gdl', window_size=window_size)
    except: print("[INFO]: Error in draw_sim.py")

    try: draw_cdf_alt(all_data, out_dir, "UL")
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_cdf_alt(all_data, out_dir, "DL")
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_cdf_param(all_data, "ildl", out_dir)
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_ccdf_param(all_data, "ildl", out_dir)
    except: print("[INFO]: Error in draw_sim.py")

    try: plot_histograms_ul_dl_per_ue(all_data, 'sinr_ul', 'sinr_dl', 'SINR Histogram', 'SINR (dB)', 'sinr_hist_ul_dl.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_per_ue(all_data, 'rsrp_ul', 'rsrp_dl', 'RSRP Histogram', 'RSRP (dBm)', 'rsrp_hist_ul_dl.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_per_ue(all_data, 'cqi_ul', 'cqi_dl', 'CQI Histogram', 'CQI', 'cqi_hist_ul_dl.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_per_ue(all_data, 'mcs_ul', 'mcs_dl', 'MCS Histogram', 'MCS', 'mcs_hist_ul_dl.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_per_ue(all_data, 'eff_ul', 'eff_dl', 'MCS Efficiency Histogram', 'Efficiency', 'eff_hist_ul_dl.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")

    try: plot_histograms_per_ue(all_data, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'lul', 'UL Latency Histogram', 'Latency (s)', 'lul_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'ldl', 'DL Latency Histogram', 'Latency (s)', 'ldl_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'ilul', 'UL IP Latency Histogram', 'Latency (s)', 'ilul_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'ildl', 'DL IP Latency Histogram', 'Latency (s)', 'ildl_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'eul', 'UL Error Rate Histogram', 'Error Rate (Mbps)', 'eul_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'edl', 'DL Error Rate Histogram', 'Error Rate (Mbps)', 'edl_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'gul', 'UL Gen. Traffic Histogram', 'Gen. Traffic (Mbps)', 'gul_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'gdl', 'DL Gen. Traffic Histogram', 'Gen. Traffic (Mbps)', 'gdl_hist.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_per_ue(all_data, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_hist.png', outdir=out_dir, bins=np.arange(0.5, 5.5, 1))
    except: print("[INFO]: Error in draw_sim.py")

    try: plot_histograms_ul_dl_all_ue(all_data, 'sinr_ul', 'sinr_dl', 'SINR Histogram', 'SINR (dB)', 'sinr_hist_ul_dl_all.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_all_ue(all_data, 'rsrp_ul', 'rsrp_dl', 'RSRP Histogram', 'RSRP (dBm)', 'rsrp_hist_ul_dl_all.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_all_ue(all_data, 'cqi_ul', 'cqi_dl', 'CQI Histogram', 'CQI', 'cqi_hist_ul_dl_all.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_all_ue(all_data, 'mcs_ul', 'mcs_dl', 'MCS Histogram', 'MCS', 'mcs_hist_ul_dl_all.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_ul_dl_all_ue(all_data, 'eff_ul', 'eff_dl', 'MCS Efficiency Histogram', 'Efficiency', 'eff_hist_ul_dl_all.png', bins=40, outdir=out_dir, figsize=(20, 10))
    except: print("[INFO]: Error in draw_sim.py")

    try: plot_histograms_all_ue(all_data, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'lul', 'UL Latency Histogram', 'Latency (s)', 'lul_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'ldl', 'DL Latency Histogram', 'Latency (s)', 'ldl_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'ilul', 'UL IP Latency Histogram', 'Latency (s)', 'ilul_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'ildl', 'DL IP Latency Histogram', 'Latency (s)', 'ildl_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'eul', 'UL Error Rate Histogram', 'Error Rate (Mbps)', 'eul_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'edl', 'DL Error Rate Histogram', 'Error Rate (Mbps)', 'edl_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'gul', 'UL Gen. Traffic Histogram', 'Gen. Traffic (Mbps)', 'gul_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'gdl', 'DL Gen. Traffic Histogram', 'Gen. Traffic (Mbps)', 'gdl_hist_all.png', outdir=out_dir, bins=30, figsize=(20, 6))
    except: print("[INFO]: Error in draw_sim.py")
    try: plot_histograms_all_ue(all_data, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_hist_all.png', outdir=out_dir, bins=np.arange(0.5, 5.5, 1))
    except: print("[INFO]: Error in draw_sim.py")



    # 4. Generate graphs for MAC

    # Draw UL
    direction = "UL"
    try: draw_time_series(results_base, ul_data, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period)
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_time_series_all(results_base, ul_data, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period)
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_cdf(results_base, ul_file, direction)
    except: print("[INFO]: Error in draw_sim.py")

    # Draw DL
    direction = "DL"
    try: draw_time_series(results_base, dl_data, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period)
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_time_series_all(results_base, dl_data, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period)
    except: print("[INFO]: Error in draw_sim.py")
    try: draw_cdf(results_base, dl_file, direction)
    except: print("[INFO]: Error in draw_sim.py")


if __name__ == "__main__":
    main()
