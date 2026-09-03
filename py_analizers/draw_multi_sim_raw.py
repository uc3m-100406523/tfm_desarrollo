#!/usr/bin/env python3
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from draw_sim import *



###################
#                 #
# Parsing methods #
#                 #
###################



# Parse post processing data file

def parse_post_processing(fname: str):

    data = {}

    section=0

    with open(fname, "r") as f:

        for line in f:

            entry = {}
            k, v = line.split(":", 1)

            # This part of the data are single values
            if section == 0:
                try:
                    entry[k] = float(v)
                except ValueError:
                    entry[k] = v
                if np.strings.equal(k, "dl_ase"):
                    section = 1
            # This part of the data are arrays
            else:
                # Obtain and clear the list of strings
                values = str.split(v, ",")
                for i, val in enumerate(values):
                    values[i] = str.strip(val, ", \n")

                entry[k] = np.float128(values)

            data[k] = entry[k]
    return data



############################
#                          #
# Plotting methods for MAC #
#                          #
############################



# Plot instant total throughput and instant average throughput per UE for each simulation. Requires simulation raw data

def draw_time_series_multi(output_dir: str, grid_data_list: str, ue_log: str | None, direction: str, shannon_cfg: ShannonParams, ue_sample_freq=10, mac_sample_freq=10, period=1, figsize=(12, 6)):



    mbps_total_list = []
    mbps_per_ue_list = []
    secs_list = []
    capacity_secs_list = []
    capacity_vals_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):



        # 1. Get data

        SAMPLE_FREQ = mac_sample_freq
        K2M = 1e-3

        ue_lines = {}
        for ue, sec_dict in grid_data.items():
            secs = sorted(sec_dict.keys()) # Time (seconds)
            mbps = [(sec_dict[s] / SAMPLE_FREQ) * K2M for s in secs] # Throughput (Mbps)
            ue_lines[ue] = (secs, mbps)



        # 2. Compute values

        # Shannon Limit (using the same value for all the simulations)
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

        mbps_total_list.append(mbps_total)
        mbps_per_ue_list.append(mbps_per_ue)
        secs_list.append(secs)
        capacity_secs_list.append(capacity_secs)
        capacity_vals_list.append(capacity_vals)



    # 3. Process data for plotting

    max_len1 = 0
    for secs_array in secs_list:
        if len(secs_array) > max_len1:
            max_len1 = len(secs_array)
            secs = secs_array

    max_len2 = 0
    for capacity_secs_array in capacity_secs_list:
        if len(capacity_secs_array) > max_len2:
            max_len2 = len(capacity_secs_array)
            capacity_secs = capacity_secs_array



    # 4. Plot data

    plt.figure(figsize=figsize)
    cmap = plt.get_cmap("tab10")

    for i, mbps_total in enumerate(mbps_total_list):

        # Fix length
        mbps_total = (np.append(np.array(mbps_total), np.zeros([max_len1-len(mbps_total)]))).tolist()

        plt.plot(
            secs, # Time (seconds)
            mbps_total, # Throughput (Mbps)
            linestyle="-", marker="o", linewidth=2, color=cmap(0*len(mbps_total_list)+i % cmap.N), label=f"Total throughput (sim. {i})"
        )

    for i, mbps_per_ue in enumerate(mbps_per_ue_list):

        # Fix length
        mbps_per_ue = (np.append(np.array(mbps_per_ue), np.zeros([max_len1-len(mbps_per_ue)]))).tolist()

        plt.plot(
            secs, # Time (seconds)
            mbps_per_ue, # Throughput (Mbps)
            linestyle="-", marker="o", linewidth=2, color=cmap(1*len(mbps_per_ue_list)+i % cmap.N), label=f"Throughput per UE (sim. {i})"
        )

    # Shannon Limit
    for i, capacity_vals in enumerate(capacity_vals_list):
        if capacity_secs:

            # Fix length
            capacity_vals = (np.append(np.array(capacity_vals), np.zeros([max_len2-len(capacity_vals)]))).tolist()

            plt.plot(
                capacity_secs, # Time (seconds)
                capacity_vals, # Shannon Limit (Mbps)
                "--", linewidth=2, color=cmap(0*len(mbps_total_list)+i % cmap.N), label=f"Modified Shannon Limit (sim. {i})"
            )

    plt.xlabel("Time (seconds)")
    plt.ylabel(f"Throughput {direction} (Mbps)")
    plt.title(f"{direction} Throughput vs Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()



    # 4. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_throughput_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot CDF for each simulation. Requires simulation raw data

def draw_cdf_multi(output_dir: str, grid_files: str, direction: str, figsize=(8, 6)):

    plt.figure(figsize=figsize)

    for i, grid_file in enumerate(grid_files):

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

        plt.plot(sorted_vals, cdf, linewidth=2, label=f"Sim. {i}")

    plt.xlabel("Normalized Average UE Throughput (Mbps per UE)")
    plt.ylabel("CDF")
    plt.title(f"CDF of Normalized UE Throughput ({direction})")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_png = os.path.join(output_dir, f"cdf_throughput_{direction}_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot Jain fairness index for each simulation

def draw_fairness_multi(output_dir: str, grid_data_list: str, direction: str, n_ue_list, mac_sample_freq=10, figsize=(12, 6)):



    # 1. Compute data

    fness_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):

        # Compute fairness
        fness = fairness(grid_data, n_ue_list[i], mac_sample_freq=mac_sample_freq)
        fness_list.append(fness)

        # print(f"Fairness: {fairness}")



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(grid_data_list)), fness_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Fairness (0 - 1)")
    plt.title(f"Fairness for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_fairness_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot aggregate cell throughput for each simulation

def draw_aggregate_throughput_multi(output_dir: str, grid_data_list: str, direction: str, n_ue_list, mac_sample_freq=10, figsize=(12, 6)):



    # 1. Compute data

    agg_throughput_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):

        # Compute data


        agg_throughput = aggregate_throughput(grid_data, mac_sample_freq=mac_sample_freq)
        agg_throughput_list.append(agg_throughput)



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(grid_data_list)), agg_throughput_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Throughput (Mbps)")
    plt.title(f"Aggregate cell throughput for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_aggregate_throughput_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot average user throughput for each simulation

def draw_average_throughput_multi(output_dir: str, grid_data_list: str, direction: str, n_ue_list, mac_sample_freq=10, figsize=(12, 6)):



    # 1. Compute data

    ave_throughput_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):

        # Compute data


        ave_throughput = average_throughput(grid_data, n_ue_list[i], mac_sample_freq=mac_sample_freq)
        ave_throughput_list.append(ave_throughput)



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(grid_data_list)), ave_throughput_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Throughput (Mbps)")
    plt.title(f"Average user throughput for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_average_throughput_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot spectral efficiency for each simulation

def draw_spectral_efficiency_multi(output_dir: str, grid_data_list: str, direction: str, bandwidth_list, mac_sample_freq=10, figsize=(12, 6)):



    # 1. Compute data

    se_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):

        # Compute data


        se = spectral_efficiency(grid_data, bandwidth_list[i], mac_sample_freq=mac_sample_freq)
        se_list.append(se)



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(grid_data_list)), se_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Spectral efficiency ([b/s]/Hz)")
    plt.title(f"Spectral efficiency for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_spectral_efficiency_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot area spectral efficiency for each simulation

def draw_area_spectral_efficiency_multi(output_dir: str, grid_data_list: str, direction: str, bandwidth_list, cell_radius_list, mac_sample_freq=10, figsize=(12, 6)):



    # 1. Compute data

    ase_list = []

    # Iterate along simulations
    for i, grid_data in enumerate(grid_data_list):

        # Compute data


        ase = area_spectral_efficiency(grid_data, bandwidth_list[i], cell_radius_list[i], mac_sample_freq=mac_sample_freq)
        ase_list.append(ase)



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(grid_data_list)), ase_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Area spectral efficiency ([b/s]/[Hz · m^2])")
    plt.title(f"Area spectral efficiency for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_area_spectral_efficiency_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



###########################
#                         #
# Plotting methods for UE #
#                         #
###########################



# Plot an histogram with the data indicated in "key_ul" and "key_dl" for all UE for each simulation

def plot_histograms_ul_dl_all_ue_multi(all_data_list, key_ul, key_dl, title, xlabel, outname, bins, outdir, figsize=(10,10)):
    fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)
    cmap = plt.get_cmap("tab10")

    plot_data_ul = []
    plot_data_dl = []

    for i, all_data in enumerate(all_data_list):

        plot_data_ul_sim = []
        plot_data_dl_sim = []
        for j, data in enumerate(all_data):

            if data[key_ul]:
                plot_data_ul_sim = plot_data_ul_sim + clean_list(data[key_ul])

            if data[key_dl]:
                plot_data_dl_sim = plot_data_dl_sim + clean_list(data[key_dl])

        plot_data_ul = plot_data_ul + plot_data_ul_sim
        plot_data_dl = plot_data_dl + plot_data_dl_sim

    plot_range = (np.min(plot_data_ul+plot_data_dl), np.max(plot_data_ul+plot_data_dl))

    for i, all_data in enumerate(all_data_list):

        plot_data_ul_sim = []
        plot_data_dl_sim = []
        for j, data in enumerate(all_data):

            if data[key_ul]:
                plot_data_ul_sim = plot_data_ul_sim + clean_list(data[key_ul])

            if data[key_dl]:
                plot_data_dl_sim = plot_data_dl_sim + clean_list(data[key_dl])

        color=cmap(i % cmap.N)
        axs[0].hist(plot_data_ul_sim, bins=bins, alpha=0.5, label=f"Sim. {i}", color=color, density=True, edgecolor='black', range=plot_range)
        axs[1].hist(plot_data_dl_sim, bins=bins, alpha=0.5, label=f"Sim. {i}", color=color, density=True, edgecolor='black', range=plot_range)

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



# Plot a 3D histogram with the data indicated in "key_ul" and "key_dl" for all UE for each simulation

def plot_3d_histograms_ul_dl_all_ue_multi(all_data_list, key_ul, key_dl, title, xlabel, outname, bins, outdir, figsize=(10,10)):

    fig, axs = plt.subplots(1, 2, figsize=figsize, sharex=True, subplot_kw={"projection": "3d"})
    cmap = plt.get_cmap("tab10")

    plot_data_ul = []
    plot_data_dl = []

    for i, all_data in enumerate(all_data_list):

        plot_data_ul_sim = []
        plot_data_dl_sim = []
        for j, data in enumerate(all_data):

            if data[key_ul]:
                plot_data_ul_sim = plot_data_ul_sim + clean_list(data[key_ul])

            if data[key_dl]:
                plot_data_dl_sim = plot_data_dl_sim + clean_list(data[key_dl])

        plot_data_ul = plot_data_ul + plot_data_ul_sim
        plot_data_dl = plot_data_dl + plot_data_dl_sim

    plot_range = (np.min(plot_data_ul+plot_data_dl), np.max(plot_data_ul+plot_data_dl))

    x_ul = np.array([])
    y_ul = np.array([])
    z_ul = np.array([])
    dx_ul = np.array([])
    dy_ul = np.array([])
    dz_ul = np.array([])
    colors_ul = []
    x_dl = np.array([])
    y_dl = np.array([])
    z_dl = np.array([])
    dx_dl = np.array([])
    dy_dl = np.array([])
    dz_dl = np.array([])
    colors_dl = []
    for i, all_data in enumerate(all_data_list):

        plot_data_ul_sim = []
        plot_data_dl_sim = []
        for j, data in enumerate(all_data):

            if data[key_ul]:
                plot_data_ul_sim = plot_data_ul_sim + clean_list(data[key_ul])

            if data[key_dl]:
                plot_data_dl_sim = plot_data_dl_sim + clean_list(data[key_dl])

        color=cmap(i % cmap.N)

        hist, bin_edges = np.histogram(plot_data_ul_sim, bins=bins, range=plot_range, density=True)
        x_ul = np.append(x_ul, bin_edges[:-1])
        y_ul = np.append(y_ul, np.ones([len(hist)])*i-0.25)
        z_ul = np.append(z_ul, np.zeros([len(hist)]))
        dx_ul = np.append(dx_ul, np.diff(bin_edges))
        dz_ul = np.append(dz_ul, hist)
        for j in range(len(hist)):
            colors_ul.append(color)

        hist, bin_edges = np.histogram(plot_data_dl_sim, bins=bins, range=plot_range, density=True)
        x_dl = np.append(x_dl, bin_edges[:-1])
        y_dl = np.append(y_dl, np.ones([len(hist)])*i-0.25)
        z_dl = np.append(z_dl, np.zeros([len(hist)]))
        dx_dl = np.append(dx_dl, np.diff(bin_edges))
        dz_dl = np.append(dz_dl, hist)
        for j in range(len(hist)):
            colors_dl.append(color)

    dy_ul = np.ones_like(x_ul)*0.5
    dy_dl = np.ones_like(x_dl)*0.5

    axs[0].bar3d(x_ul, y_ul, z_ul, dx_ul, dy_ul, dz_ul, color=colors_ul)
    axs[1].bar3d(x_dl, y_dl, z_dl, dx_dl, dy_dl, dz_dl, color=colors_dl)
    axs[0].set_title(f"{title} (UL)")
    axs[1].set_title(f"{title} (DL)")
    axs[0].set_xlabel(xlabel)
    axs[1].set_xlabel(xlabel)
    axs[0].set_ylabel("# sim.")
    axs[1].set_ylabel("# sim.")
    axs[0].grid(True)
    axs[1].grid(True)
    fig.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot a 2D histogram with the data indicated in "key_ul" and "key_dl" for all UE for each simulation

def plot_2d_histograms_ul_dl_all_ue_multi(all_data_list, key_ul, key_dl, title, xlabel, outname, bins, outdir, figsize=(10,10)):
    fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)

    sim_id_ul = np.array([])
    sim_id_dl = np.array([])
    plot_data_ul = []
    plot_data_dl = []

    for i, all_data in enumerate(all_data_list):

        plot_data_ul_sim = []
        plot_data_dl_sim = []
        for j, data in enumerate(all_data):

            if data[key_ul]:
                plot_data_ul_sim = plot_data_ul_sim + clean_list(data[key_ul])

            if data[key_dl]:
                plot_data_dl_sim = plot_data_dl_sim + clean_list(data[key_dl])

        plot_data_ul = plot_data_ul + plot_data_ul_sim
        plot_data_dl = plot_data_dl + plot_data_dl_sim
        sim_id_ul = np.append(sim_id_ul, i*np.ones([len(plot_data_ul_sim)]))
        sim_id_dl = np.append(sim_id_dl, i*np.ones([len(plot_data_dl_sim)]))

    axs[0].hist2d(plot_data_ul, sim_id_ul, bins=[bins, len(all_data_list)], alpha=0.5, label=f"{title} (UL)", density=True, edgecolor='black')
    axs[1].hist2d(plot_data_dl, sim_id_dl, bins=[bins, len(all_data_list)], alpha=0.5, label=f"{title} (DL)", density=True, edgecolor='black')
    axs[0].set_title(f"{title} (UL)")
    axs[1].set_title(f"{title} (DL)")
    axs[1].set_xlabel(xlabel)
    axs[0].set_ylabel("# simulation")
    axs[1].set_ylabel("# simulation")
    # axs[0].legend()
    # axs[1].legend()
    axs[0].grid(True)
    axs[1].grid(True)
    fig.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot an histogram with the data indicated in "key" for all UE for each simulation

def plot_histograms_all_ue_multi(all_data_list, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):
    plt.figure(figsize=figsize)
    cmap = plt.get_cmap("tab10")

    plot_data = []

    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        plot_data = plot_data + plot_data_sim

    plot_range = (np.min(plot_data), np.max(plot_data))

    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        color=cmap(i % cmap.N)
        plt.hist(plot_data_sim, bins=bins, alpha=0.5, label=f"Sim. {i}", density=True, edgecolor='black', color=color, range=plot_range)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot a 2D histogram with the data indicated in "key" for all UE for each simulation

def plot_2d_histograms_all_ue_multi(all_data_list, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):
    plt.figure(figsize=figsize)

    sim_id = np.array([])
    plot_data = []

    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        plot_data = plot_data + plot_data_sim
        sim_id = np.append(sim_id, i*np.ones([len(plot_data_sim)]))
    
    plt.hist2d(plot_data, sim_id, bins=[bins, len(all_data_list)], alpha=0.5, label=title, density=True, edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("# simulation")
    plt.grid(True)
    #plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot several graphs with histograms with the data indicated in "key" for all UE for each simulation

def plot_graph_histograms_all_ue_multi(all_data_list, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):
    #plt.figure(figsize=figsize)

    fig, axs = plt.subplots(len(all_data_list), 1, figsize=figsize, sharex=True)

    sim_id = np.array([])
    plot_data = []

    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        axs[i].hist(plot_data_sim, bins=bins, alpha=0.5, label=title, density=True, edgecolor='black')
        axs[i].set_title(title)
        axs[i].set_ylabel(f"Sim. {i}")
        axs[i].legend()
        axs[i].grid(True)

        # plot_data = plot_data + plot_data_sim
        # sim_id = np.append(sim_id, i*np.ones([len(plot_data_sim)]))
    axs[len(all_data_list)-1].set_xlabel(xlabel)

    fig.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot a 3D histogram with the data indicated in "key" for all UE for each simulation

def plot_3d_histograms_all_ue_multi(all_data_list, key, title, xlabel, outname, outdir, bins, figsize=(10, 6)):

    cmap = plt.get_cmap("tab10")

    plot_data = []

    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        plot_data = plot_data + plot_data_sim

    plot_range = (np.min(plot_data), np.max(plot_data))

    x = np.array([])
    y = np.array([])
    z = np.array([])
    dx = np.array([])
    dy = np.array([])
    dz = np.array([])
    colors = []
    for i, all_data in enumerate(all_data_list):

        plot_data_sim = []
        for j, data in enumerate(all_data):
            if not data[key]:
                continue
            plot_data_sim = plot_data_sim + data[key]

        color=cmap(i % cmap.N)
        hist, bin_edges = np.histogram(plot_data_sim, bins=bins, range=plot_range, density=True)
        # plt.hist(alpha=0.5)

        # values = np.array(bin_edges[:-1]) + ((np.array(bin_edges[1:])-np.array(bin_edges[:-1]))/2)
        # x = np.append(x, values)
        x = np.append(x, bin_edges[:-1])
        y = np.append(y, np.ones([len(hist)])*i-0.25)
        z = np.append(z, np.zeros([len(hist)]))
        dx = np.append(dx, np.diff(bin_edges))
        dz = np.append(dz, hist)
        for j in range(len(hist)):
            colors.append(color)


    dy = np.ones_like(x)*0.5

    fig, axs = plt.subplots(subplot_kw={"projection": "3d"}, figsize=figsize, sharex=True)
    axs.bar3d(x, y, z, dx, dy, dz, color=colors)

    axs.set_title(title)
    axs.set_xlabel(xlabel)
    axs.set_ylabel("# sim.")
    axs.set_zlabel("% total")
    axs.grid(True)

    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot average error rate in Mbps for all UE for each simulation

def draw_error_rate_mbps_multi(output_dir: str, all_data_list: str, direction: str, figsize=(12, 6)):



    # 1. Compute data

    ave_er_list = []

    # Iterate along simulations
    for i, all_data in enumerate(all_data_list):

        # Compute data

        er = error_rate_mbps(all_data, direction)
        ave_er_list.append(np.sum(er)/len(er))



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(all_data_list)), ave_er_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Average error rate (Mbps)")
    plt.title(f"Average error rate for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_error_rate_mbps_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot average error rate in as a percentage for all UE for each simulation

def draw_error_rate_ratio_multi(output_dir: str, all_data_list: str, direction: str, figsize=(12, 6)):



    # 1. Compute data

    perc_er_list = []

    # Iterate along simulations
    for i, all_data in enumerate(all_data_list):

        # Compute data

        er = error_rate_ratio(all_data, direction)
        perc_er_list.append(100*np.sum(er)/len(er))



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(all_data_list)), perc_er_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Average error rate (%)")
    plt.title(f"Average error rate for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_error_rate_perc_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot average success rate in as a percentage for all UE for each simulation

def draw_success_rate_ratio_multi(output_dir: str, all_data_list: str, direction: str, figsize=(12, 6)):



    # 1. Compute data

    perc_er_list = []

    # Iterate along simulations
    for i, all_data in enumerate(all_data_list):

        # Compute data

        er = success_rate_ratio(all_data, direction)
        perc_er_list.append(100*np.sum(er)/len(er))



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(all_data_list)), perc_er_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Average success rate (%)")
    plt.title(f"Average success rate for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_success_rate_perc_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot average latency for all UE for each simulation

def draw_average_latency_multi(output_dir: str, all_data_list: str, direction: str, figsize=(12, 6)):



    # 1. Compute data

    perc_er_list = []

    # Iterate along simulations
    for i, all_data in enumerate(all_data_list):

        # Compute data

        er = average_latency(all_data, direction)
        perc_er_list.append(np.sum(er)/len(er))



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(all_data_list)), perc_er_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Average latency (s)")
    plt.title(f"Average latency for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_average_latency_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



# Plot average latency for all UE for each simulation

def draw_average_ip_latency_multi(output_dir: str, all_data_list: str, direction: str, figsize=(12, 6)):



    # 1. Compute data

    perc_er_list = []

    # Iterate along simulations
    for i, all_data in enumerate(all_data_list):

        # Compute data

        er = average_ip_latency(all_data, direction)
        perc_er_list.append(np.sum(er)/len(er))



    # 2. Plot data

    plt.figure(figsize=figsize)

    plt.bar(np.arange(len(all_data_list)), perc_er_list)



    plt.xlabel(f"# sim.")
    plt.ylabel(f"Average IP latency (s)")
    plt.title(f"Average IP latency for {direction}")
    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    out_png = os.path.join(output_dir, f"{direction.lower()}_average_ip_latency_multi_sim.png")
    plt.savefig(out_png)
    print(f"[SAVED] {out_png}")



def main():



    # 0. Previous steps

    # Print help
    if(len(sys.argv)>0):
        if str.find(sys.argv[1], "--help") == 0:
            print("Expected arguments: <results directory> <list of logs directories containing a \"ue\" directory and a \"mac\" directory>")
            exit()

    # Script directory
    script_dir_ue = os.path.dirname(os.path.realpath(sys.argv[0]))
    script_dir_mac = os.path.dirname(os.path.abspath(__file__))



    # 1. Logs managing

    # UE log data
    all_data_list = []

    # MAC log data
    ul_data_list = []
    dl_data_list = []
    ul_file_list = []
    dl_file_list = []

    # Post processing data
    ppd_path_list = []
    post_processing_list = []

    for logs_dir in sys.argv[2:]:

        print("Processing simulation in {}".format(logs_dir))



        # Logs managing for UE

        # UE logs directory
        ue_dir_ue = os.path.join(logs_dir, 'ue')

        # UE logs
        log_files = sorted(glob(os.path.join(ue_dir_ue, 'ue_log_*.txt')))

        # Logs directory (normalized)
        # log_folder_ue = os.path.basename(os.path.dirname(ue_dir_ue))

        if len(log_files)==0:
            print(f"[ERROR] UE logs not found at {ue_dir_ue}")
            sys.exit(1)
        else:
            # Get UE data
            all_data = [parse_log_file_with_tx(f) for f in log_files]
            all_data_list.append(all_data)



        # Logs managing for MAC

        # MAC logs directory
        mac_dir = os.path.join(logs_dir, "mac")

        # UE logs directory
        ue_dir_mac = os.path.join(logs_dir, "ue")

        # UE logs (ue_log)
        ue_log = find_latest_ue_log(ue_dir_mac) if os.path.isdir(ue_dir_mac) else None

        # MAC logs
        ul_file = os.path.join(mac_dir, "grid_log_ul.txt")
        dl_file = os.path.join(mac_dir, "grid_log_dl.txt")
        if not (os.path.exists(ul_file) or os.path.exists(dl_file)):
            print(f"[ERROR] UL or DL grid logs not found at {mac_dir}")
            sys.exit(1)
        else:
            ul_file_list.append(ul_file)
            dl_file_list.append(dl_file)

            # Get MAC data
            ul_data = parse_grid_log(ul_file)
            dl_data = parse_grid_log(dl_file)
            ul_data_list.append(ul_data)
            dl_data_list.append(dl_data)



    # 2. Results managing

    results_dir = sys.argv[1]

    # UE results directory
    out_dir = os.path.join(results_dir, "ue")
    os.makedirs(out_dir, exist_ok=True)

    # MAC results directory
    results_base = os.path.join(results_dir, "mac")
    os.makedirs(results_base, exist_ok=True)



    # 3. Configuration data

    # From configuration file
    period=1
    ue_log_freq=1000
    mac_log_freq=1000
    mimo_layers = 1
    frequency = 2000000000.0
    bandwidth = 20000000
    ue_speed = 30*1e3/3600

    # Shannon parameters
    shannon_cfg = ShannonParams(
        bandwidth_mhz=bandwidth/1e6,
        mimo_layers=mimo_layers,
        bw_efficiency=0.67,
        sinr_offset_db=0,
        ul_divisor=2,
        sinr_sample_rate=int(ue_log_freq/period)
    )

    # Number of simulations
    n_sim = len(all_data_list)

    # Number of UEs (list)
    n_ue_list = []
    for all_data in all_data_list:
        n_ue_list.append(len(all_data))



    # 4. Generate graphs for UE

    # plot_histograms_ul_dl_all_ue_multi(all_data_list, 'sinr_ul', 'sinr_dl', 'SINR Histogram', 'SINR (dB)', 'sinr_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 10))
    # plot_histograms_ul_dl_all_ue_multi(all_data_list, 'rsrp_ul', 'rsrp_dl', 'RSRP Histogram', 'RSRP (dBm)', 'rsrp_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 10))
    # plot_histograms_ul_dl_all_ue_multi(all_data_list, 'cqi_ul', 'cqi_dl', 'CQI Histogram', 'CQI', 'cqi_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 10))
    # plot_histograms_ul_dl_all_ue_multi(all_data_list, 'mcs_ul', 'mcs_dl', 'MCS Histogram', 'MCS', 'mcs_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 10))
    #
    # plot_3d_histograms_ul_dl_all_ue_multi(all_data_list, 'sinr_ul', 'sinr_dl', 'SINR Histogram', 'SINR (dB)', 'sinr_3d_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 12))
    # plot_3d_histograms_ul_dl_all_ue_multi(all_data_list, 'rsrp_ul', 'rsrp_dl', 'RSRP Histogram', 'RSRP (dBm)', 'rsrp_3d_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 12))
    # plot_3d_histograms_ul_dl_all_ue_multi(all_data_list, 'cqi_ul', 'cqi_dl', 'CQI Histogram', 'CQI', 'cqi_3d_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 12))
    # plot_3d_histograms_ul_dl_all_ue_multi(all_data_list, 'mcs_ul', 'mcs_dl', 'MCS Histogram', 'MCS', 'mcs_3d_hist_ul_dl_all_ue_multi.png', bins=40, outdir=out_dir, figsize=(20, 12))
    #
    # plot_histograms_all_ue_multi(all_data_list, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 6))
    # plot_histograms_all_ue_multi(all_data_list, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 6))
    # plot_histograms_all_ue_multi(all_data_list, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_hist_all_ue_multi.png', outdir=out_dir, bins=np.arange(0.5, 5.5, 1))
    #
    # plot_3d_histograms_all_ue_multi(all_data_list, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_3d_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 20))
    # plot_3d_histograms_all_ue_multi(all_data_list, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_3d_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 20))
    # plot_3d_histograms_all_ue_multi(all_data_list, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_3d_hist_all_ue_multi.png', outdir=out_dir, bins=np.arange(0.5, 5.5, 1))

    # plot_graph_histograms_all_ue_multi(all_data_list, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_graph_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 30))
    # plot_graph_histograms_all_ue_multi(all_data_list, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_graph_hist_all_ue_multi.png', outdir=out_dir, bins=30, figsize=(20, 30))
    # plot_graph_histograms_all_ue_multi(all_data_list, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_graph_hist_all_ue_multi.png', outdir=out_dir, bins=np.arange(0.5, 5.5, 1))

    # draw_error_rate_mbps_multi(out_dir, all_data_list, "UL", figsize=(12, 6))
    # draw_error_rate_mbps_multi(out_dir, all_data_list, "DL", figsize=(12, 6))
    # draw_error_rate_ratio_multi(out_dir, all_data_list, "UL", figsize=(12, 6))
    # draw_error_rate_ratio_multi(out_dir, all_data_list, "DL", figsize=(12, 6))
    # draw_success_rate_ratio_multi(out_dir, all_data_list, "UL", figsize=(12, 6))
    # draw_success_rate_ratio_multi(out_dir, all_data_list, "DL", figsize=(12, 6))
    # draw_average_latency_multi(out_dir, all_data_list, "UL", figsize=(12, 6))
    # draw_average_latency_multi(out_dir, all_data_list, "DL", figsize=(12, 6))
    # draw_average_ip_latency_multi(out_dir, all_data_list, "UL", figsize=(12, 6))
    # draw_average_ip_latency_multi(out_dir, all_data_list, "DL", figsize=(12, 6))



    # 4. Generate graphs for MAC

    # Draw UL
    direction = "UL"

    # Plots that require simulation raw data
    # draw_time_series_multi(results_base, ul_data_list, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period, figsize=(48, 24))
    # draw_cdf_multi(results_base, ul_file_list, direction, figsize=(8, 6))

    # Plots that do not require simulation raw data
    # draw_fairness_multi(results_base, ul_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))
    # draw_aggregate_throughput_multi(results_base, ul_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))
    # draw_average_throughput_multi(results_base, ul_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))

    # Draw DL
    direction = "DL"

    # Plots that require simulation raw data
    # draw_time_series_multi(results_base, dl_data_list, ue_log, direction, shannon_cfg=shannon_cfg, ue_sample_freq=ue_log_freq, mac_sample_freq=mac_log_freq, period=period, figsize=(48, 24))
    # draw_cdf_multi(results_base, dl_file_list, direction, figsize=(8, 6))

    # Plots that do not require simulation raw data
    # draw_fairness_multi(results_base, dl_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))
    # draw_aggregate_throughput_multi(results_base, dl_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))
    # draw_average_throughput_multi(results_base, dl_data_list, direction, n_ue_list, mac_sample_freq=mac_log_freq, figsize=(12, 6))



if __name__ == "__main__":
    main()
