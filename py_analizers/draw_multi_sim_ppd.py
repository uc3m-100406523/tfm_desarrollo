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



####################
#                  #
# Plotting methods #
#                  #
####################



################################################################################
# NOTE: Types of data to be plotted                                            #
#   - Simulation single data: Post processing data.                            #
#   It is a single real number per simulation.                                 #
#   - Per UE data: Post processing data.                                       #
#   It is an array of real numbers per simulation                              #
#   where each number belongs to a single UE of the simulation.                #
#   - Simulation histogram data: Post processing data.                         #
#   It is an array of real numbers per simulation.                             #
################################################################################



# Plot an bar graph with the data indicated in "key" for each simulation. Use only with simulation single data

def plot_data_all_ue_multi(post_processing_list, key, title, xlabel, ylabel, outdir, figsize=(10, 6), colorMask=[], title_size=20.0, label_size=20.0, tick_size=20.0):



    # 1. Compute data

    plot_data = []

    # Iterate along simulations
    for i, data in enumerate(post_processing_list):

        plot_data.append(data[key])



    # 2. Plot data

    cmap = plt.get_cmap("tab10")
    color = []
    if len(colorMask) > 0:
        i = 0
        # A different color for each set of simulations
        for nSim in colorMask:
            # Append the same color for simulations belonging to the same set
            for j in range(nSim):
                color.append(cmap(i % cmap.N))
            i = i+1
    else:
        i = 0
        # The same color for all simulations
        for j in range(len(plot_data)):
            color.append(cmap(i % cmap.N))

    # Labels to avoid decimal numbers
    x = []
    for label in np.arange(len(plot_data)).tolist():
        x.append(str(label))

    plt.figure(figsize=figsize)
    plt.bar(x, plot_data, color=color)

    plt.xlabel(xlabel, size=label_size)
    plt.ylabel(ylabel, size=label_size)

    plt.title(title, size=title_size)

    plt.tick_params("x", labelsize=tick_size)
    plt.tick_params("y", labelsize=tick_size)

    plt.grid(True)
    plt.tight_layout()



    # 3. Save figure

    path = os.path.join(outdir, key+"_multi_sim.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot bar graph with the data indicated in "key" for each UE for each simulation. Use only with per UE data

def plot_data_per_ue_multi(post_processing_list, key, title, ylabel, outdir, figsize=(10, 6), colorMask=[], title_size=20.0, label_size=20.0, tick_size=20.0):

    plt.figure(figsize=figsize)
    cmap = plt.get_cmap("tab10")

    max_len=0
    for i, ppd in enumerate(post_processing_list):

        if len(ppd[key]) > max_len:
            max_len = len(ppd[key])

    for i, ppd in enumerate(post_processing_list):

        plot_data_sim = np.concat([ppd[key], np.zeros([max_len-len(ppd[key])])])

        color=cmap(i % cmap.N)

        plt.bar(np.arange(max_len), plot_data_sim, alpha=0.5, label=f"Sim. {i}", edgecolor='black', color=color, width=0.1)

    plt.title(title, size=title_size)

    plt.xlabel("# UE", size=label_size)
    plt.ylabel(ylabel, size=label_size)

    plt.tick_params("x", labelsize=tick_size)
    plt.tick_params("y", labelsize=tick_size)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, key+"_multi_sim.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot 3D bar graph with the data indicated in "key" for each UE for each simulation. Use only with per UE data

def plot_3d_data_per_ue_multi(post_processing_list, key, title, ylabel, outdir, figsize=(10, 6), colorMask=[], title_size=20.0, label_size=20.0, tick_size=20.0):

    cmap = plt.get_cmap("tab10")

    max_len=0
    for i, ppd in enumerate(post_processing_list):

        if len(ppd[key]) > max_len:
            max_len = len(ppd[key])

    x = np.array([])
    y = np.array([])
    z = np.array([])
    dx = np.array([])
    dy = np.array([])
    dz = np.array([])
    colors = []
    for i, ppd in enumerate(post_processing_list):

        hist = np.concat([ppd[key], np.zeros([max_len-len(ppd[key])])])

        # bin_edges = ppd[key+"_bin_edges"]

        color=cmap(i % cmap.N)

        x = np.append(x, np.arange(len(hist)))
        y = np.append(y, np.ones([len(hist)])*i-0.25)
        z = np.append(z, np.zeros([len(hist)]))
        dx = np.append(dx, np.ones([len(hist)]))
        dz = np.append(dz, hist)
        for j in range(len(hist)):
            colors.append(color)
    dy = np.ones_like(x)*0.5

    fig, axs = plt.subplots(subplot_kw={"projection": "3d"}, figsize=figsize, sharex=True)
    axs.bar3d(x, y, z, dx, dy, dz, color=colors)

    axs.set_title(title, size=title_size)

    axs.set_xlabel("# UE", size=label_size)
    axs.set_ylabel("# sim.", size=label_size)
    axs.set_zlabel(ylabel, size=label_size)

    axs.tick_params("x", labelsize=tick_size)
    axs.tick_params("y", labelsize=tick_size)
    axs.tick_params("z", labelsize=tick_size)

    axs.grid(True)

    path = os.path.join(outdir, key+"_3d_multi_sim.png")
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot an histogram with the data indicated in "key" for all UE for each simulation. Use only with simulation histogram data

def plot_histograms_all_ue_multi(post_processing_list, key, title, xlabel, outname, outdir, figsize=(10, 6), title_size=20.0, label_size=20.0, tick_size=20.0):

    plt.figure(figsize=figsize)
    cmap = plt.get_cmap("tab10")

    for i, ppd in enumerate(post_processing_list):

        plot_data_sim = ppd[key]

        bin_edges = ppd[key+"_bin_edges"]

        color=cmap(i % cmap.N)

        plt.bar(bin_edges[0:-1]+np.diff(bin_edges)/2, plot_data_sim, alpha=0.5, label=f"Sim. {i}", edgecolor='black', color=color, width=np.diff(bin_edges)[0])

    plt.title(title, size=title_size)

    plt.xlabel(xlabel, size=label_size)

    plt.tick_params("x", labelsize=tick_size)
    plt.tick_params("y", labelsize=tick_size)

    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



# Plot a 3D histogram with the data indicated in "key" for all UE for each simulation. Use only with simulation histogram data

def plot_3d_histograms_all_ue_multi(post_processing_list, key, title, xlabel, outname, outdir, figsize=(10, 6), colorMask=[], title_size=20.0, label_size=20.0, tick_size=20.0):

    cmap = plt.get_cmap("tab10")
    simColor = []
    if len(colorMask) > 0:
        i = 0
        # A different color for each set of simulations
        for nSim in colorMask:
            # Append the same color for simulations belonging to the same set
            for j in range(nSim):
                simColor.append(cmap(i % cmap.N))
            i = i+1
    else:
        # A different color for each simulation
        for i in range(len(post_processing_list)):
            simColor.append(cmap(i % cmap.N))

    x = np.array([])
    y = np.array([])
    z = np.array([])
    dx = np.array([])
    dy = np.array([])
    dz = np.array([])
    colors = []
    for i, ppd in enumerate(post_processing_list):

        hist = ppd[key]

        bin_edges = ppd[key+"_bin_edges"]

        color=simColor[i]

        x = np.append(x, bin_edges[0:-1]+np.diff(bin_edges)/2)
        y = np.append(y, np.ones([len(hist)])*i-0.25)
        z = np.append(z, np.zeros([len(hist)]))
        dx = np.append(dx, np.diff(bin_edges))
        dz = np.append(dz, hist)
        for j in range(len(hist)):
            colors.append(color)
    dy = np.ones_like(x)*0.5

    fig, axs = plt.subplots(subplot_kw={"projection": "3d"}, figsize=figsize, sharex=True)
    axs.bar3d(x, y, z, dx, dy, dz, color=colors)

    axs.set_title(title, size=title_size)

    axs.set_xlabel(xlabel, size=label_size)
    axs.set_ylabel("# sim.", size=label_size)
    axs.set_zlabel("% total", size=label_size)

    axs.tick_params("x", labelsize=tick_size)
    axs.tick_params("y", labelsize=tick_size)
    axs.tick_params("z", labelsize=tick_size)

    axs.grid(True)

    path = os.path.join(outdir, outname)
    plt.savefig(path)
    print(f"[SAVED] {path}")



def main():



    # 0. Previous steps

    # Print help
    if(len(sys.argv)>0):
        if str.find(sys.argv[1], "--help") == 0:
            print("Expected arguments: <results directory> <list of logs directories containing a \"ue\" directory and a \"mac\" directory>")
            exit()

    # # Script directory
    # script_dir_ue = os.path.dirname(os.path.realpath(sys.argv[0]))
    # script_dir_mac = os.path.dirname(os.path.abspath(__file__))
    #
    #
    #
    # # 1. Logs managing
    #
    # # UE log data
    # all_data_list = []
    #
    # # MAC log data
    # ul_data_list = []
    # dl_data_list = []
    # ul_file_list = []
    # dl_file_list = []

    # Post processing data
    ppd_path_list = []
    post_processing_list = []

    colorMask = []

    # For each simulation
    for logs_dir in sys.argv[2:]:

        # Check if a color mask is given
        if "colorMask:" in logs_dir:
            print("Caught color mask: {}".format(logs_dir))
            colorMask = np.int32(str.split(logs_dir, ":")[1:])
        else:

            print("Processing simulation in {}".format(logs_dir))



            # # Logs managing for UE
            #
            # # UE logs directory
            # ue_dir_ue = os.path.join(logs_dir, 'ue')
            #
            # # UE logs
            # log_files = sorted(glob(os.path.join(ue_dir_ue, 'ue_log_*.txt')))
            #
            # # Logs directory (normalized)
            # # log_folder_ue = os.path.basename(os.path.dirname(ue_dir_ue))
            #
            # if len(log_files)==0:
            #     print(f"[WARNING] UE logs not found at {ue_dir_ue}. Working only with processed data.")
            # else:
            #     # Get UE data
            #     all_data = [parse_log_file_with_tx(f) for f in log_files]
            #     all_data_list.append(all_data)
            #
            #
            #
            # # Logs managing for MAC
            #
            # # MAC logs directory
            # mac_dir = os.path.join(logs_dir, "mac")
            #
            # # UE logs directory
            # ue_dir_mac = os.path.join(logs_dir, "ue")
            #
            # # UE logs (ue_log)
            # ue_log = find_latest_ue_log(ue_dir_mac) if os.path.isdir(ue_dir_mac) else None
            #
            # # MAC logs
            # ul_file = os.path.join(mac_dir, "grid_log_ul.txt")
            # dl_file = os.path.join(mac_dir, "grid_log_dl.txt")
            # if not (os.path.exists(ul_file) or os.path.exists(dl_file)):
            #     print(f"[WARNING] UL or DL grid logs not found at {mac_dir}. Working only with processed data.")
            # else:
            #     ul_file_list.append(ul_file)
            #     dl_file_list.append(dl_file)
            #
            #     # Get MAC data
            #     ul_data = parse_grid_log(ul_file)
            #     dl_data = parse_grid_log(dl_file)
            #     ul_data_list.append(ul_data)
            #     dl_data_list.append(dl_data)



            # Post processing data

            unchecked_ppd_path_list = [os.path.join(logs_dir, "post_processing.txt"),
            os.path.join(logs_dir, "post_processing2.txt"),
            os.path.join(logs_dir, "post_processing3.txt"),
            os.path.join(logs_dir, "post_processing4.txt"),
            os.path.join(logs_dir, "post_processing5.txt"),
            os.path.join(logs_dir, "post_processing6.txt"),
            os.path.join(logs_dir, "post_processing7.txt"),
            os.path.join(logs_dir, "post_processing8.txt"),
            os.path.join(logs_dir, "post_processing9.txt"),
            os.path.join(logs_dir, "post_processing10.txt")
            ]

            # Merge data from different post processing files
            first_ppd = 0
            for ppd_path in unchecked_ppd_path_list:
                if os.path.exists(ppd_path):
                    print(f"[INFO] Getting data from {ppd_path}")
                    ppd_path_list.append(ppd_path)
                    if first_ppd == 0:
                        post_processing = parse_post_processing(ppd_path)
                        first_ppd = 1
                        # print(post_processing)
                    else:
                        post_processing_i = parse_post_processing(ppd_path)

                        # print(post_processing_i)

                        # Copy data
                        # Alredy existing
                        for key in post_processing.keys():
                            if key in post_processing_i.keys():
                                post_processing[key] = post_processing_i[key]
                        # New features
                        for key in post_processing_i.keys():
                            if key not in post_processing.keys():
                                post_processing[key] = post_processing_i[key]

            # print(post_processing)

            if len(ppd_path_list) == 0:
                print(f"[ERROR] Post processing data not found at {unchecked_ppd_path_list[0]}, ..., {unchecked_ppd_path_list[9]}")
                sys.exit(1)

            # ppd_path = os.path.join(logs_dir, "post_processing.txt")
            # ppd_path2 = os.path.join(logs_dir, "post_processing2.txt")
            #
            # if os.path.exists(ppd_path2):
            #     ppd_path_list.append(ppd_path2)
            #     post_processing = parse_post_processing(ppd_path2)
            # elif os.path.exists(ppd_path):
            #     ppd_path_list.append(ppd_path)
            #     post_processing = parse_post_processing(ppd_path)
            # else:
            #     print(f"[ERROR] Post processing data not found at {ppd_path}, {ppd_path2}")
            #     sys.exit(1)

            # Post processing data of current simulation are added to the list
            post_processing_list.append(post_processing)


    # 2. Results managing

    results_dir = sys.argv[1]

    # UE results directory
    out_dir = os.path.join(results_dir, "ue")
    os.makedirs(out_dir, exist_ok=True)

    # MAC results directory
    # results_base = os.path.join(results_dir, "mac")
    # os.makedirs(results_base, exist_ok=True)



    # 3. Configuration data

    # # From configuration file
    # period=1
    # ue_log_freq=1000
    # mac_log_freq=1000
    # mimo_layers = 1
    # frequency = 2000000000.0
    # bandwidth = 20000000
    # ue_speed = 30*1e3/3600
    #
    # # Shannon parameters
    # shannon_cfg = ShannonParams(
    #     bandwidth_mhz=bandwidth/1e6,
    #     mimo_layers=mimo_layers,
    #     bw_efficiency=0.67,
    #     sinr_offset_db=0,
    #     ul_divisor=2,
    #     sinr_sample_rate=int(ue_log_freq/period)
    # )
    #
    # # Number of simulations
    # n_sim = len(all_data_list)
    # if n_sim == 0:
    #     n_sim = len(post_processing_list)
    # if n_sim == 0:
    #     print(f"[ERROR] Void data.")
    #     sys.exit(1)
    #
    # # Number of UEs (list)
    # n_ue_list = []
    # if len(all_data_list) != 0:
    #     for all_data in all_data_list:
    #         n_ue_list.append(len(all_data))
    # elif len(post_processing_list) != 0:
    #     for ppd in post_processing_list:
    #         n_ue_list.append(ppd["n_ue"])



    # 4. Generate graphs

    try: plot_data_all_ue_multi(post_processing_list, "period", "Period", "# sim.", "Period", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ue_log_freq", "Logging frequency (UE)", "# sim.", "Logging frequency", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "mac_log_freq", "Logging frequency (MAC)", "# sim.", "Logging frequency", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "mimo_layers", "Mimo layers", "# sim.", "Mimo layers", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "frequency", "Frequency", "# sim.", "Frequency", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "bandwidth", "Bandwidth", "# sim.", "Bandwidth", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ue_speed", "UE speed", "# sim.", "UE speed", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "max_distance", "Max. distance", "# sim.", "Max. distance", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_bandwidth_mhz", "Bandwidth", "# sim.", "Bandwidth", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_mimo_layers", "Mimo layers", "# sim.", "Mimo layers", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_bw_efficiency", "Bandwidth eff.", "# sim.", "Bandwidth eff.", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_sinr_offset_db", "Period", "# sim.", "Period", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_ul_divisor", "UL divisor", "# sim.", "UL divisor", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "shannon_cfg_sinr_sample_rate", "SINR sample rate", "# sim.", "SINR sample rate", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "n_ue", "Number of UE", "# sim.", "Number of UE", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "sinr_period", "SINR period", "# sim.", "SINR period", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "sinr_rate", "SINR rate", "# sim.", "SINR rate", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ul_fairness", "UL fairness", "# sim.", "UL fairness", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "dl_fairness", "DL fairness", "# sim.", "DL fairness", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ul_agg_throughput", "UL aggregated throughput", "# sim.", "UL aggregated throughput", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "dl_agg_throughput", "DL aggregated throughput", "# sim.", "DL aggregated throughput", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ul_ave_throughput", "UL average throughput", "# sim.", "UL average throughput", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "dl_ave_throughput", "DL average throughput", "# sim.", "DL average throughput", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ul_se", "UL spectral eff.", "# sim.", "UL spectral eff.", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "dl_se", "DL spectral eff.", "# sim.", "DL spectral eff.", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "ul_ase", "UL ASE", "# sim.", "UL ASE", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_all_ue_multi(post_processing_list, "dl_ase", "DL ASE", "# sim.", "DL ASE", outdir=out_dir, figsize=(12, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")

    try: plot_data_per_ue_multi(post_processing_list, "ul_gr", "UL generation rate", "Rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_gr", "UL generation rate", "Rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_gr", "DL generation rate", "Rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_gr", "DL generation rate", "Rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "ul_tr", "UL throughput", "Rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_tr", "UL throughput", "Rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_tr", "DL throughput", "Rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_tr", "DL throughput", "Rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "ul_er", "UL error rate", "Error rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_er", "UL error rate", "Error rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_er", "DL error rate", "Error rate (Mbps)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_er", "DL error rate", "Error rate (Mbps)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "ul_er_ratio", "UL error rate (ratio)", "Error rate (ratio)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_er_ratio", "UL error rate (ratio)", "Error rate (ratio)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_er_ratio", "DL error rate (ratio)", "Error rate (ratio)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_er_ratio", "DL error rate (ratio)", "Error rate (ratio)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "ul_er_perc", "UL error rate (%)", "Error rate (%)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_er_perc", "UL error rate (%)", "Error rate (%)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_er_perc", "DL error rate (%)", "Error rate (%)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_er_perc", "DL error rate (%)", "Error rate (%)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")

    try: plot_data_per_ue_multi(post_processing_list, "ul_l", "UL latency", "Latency (s)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_l", "UL latency", "Latency (s)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_l", "DL latency", "Latency (s)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_l", "DL latency", "Latency (s)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "ul_il", "UL IP latency", "Latency (s)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "ul_il", "UL IP latency", "Latency (s)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_data_per_ue_multi(post_processing_list, "dl_il", "DL IP latency", "Latency (s)", outdir=out_dir, figsize=(50, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_data_per_ue_multi(post_processing_list, "dl_il", "DL IP latency", "Latency (s)", outdir=out_dir, figsize=(10, 6), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")

    try: plot_histograms_all_ue_multi(post_processing_list, 'sinr_ul', 'UL SINR Histogram', 'SINR (dB)', 'sinr_ul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'sinr_ul', 'UL SINR Histogram', 'SINR (dB)', 'sinr_ul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'sinr_dl', 'DL SINR Histogram', 'SINR (dB)', 'sinr_dl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'sinr_dl', 'DL SINR Histogram', 'SINR (dB)', 'sinr_dl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'rsrp_ul', 'UL RSRP Histogram', 'RSRP (dB)', 'rsrp_ul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'rsrp_ul', 'UL RSRP Histogram', 'RSRP (dB)', 'rsrp_ul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'rsrp_dl', 'DL RSRP Histogram', 'RSRP (dB)', 'rsrp_dl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'rsrp_dl', 'DL RSRP Histogram', 'RSRP (dB)', 'rsrp_dl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'cqi_ul', 'UL CQI Histogram', 'CQI', 'cqi_ul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'cqi_ul', 'UL CQI Histogram', 'CQI', 'cqi_ul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'cqi_dl', 'DL CQI Histogram', 'CQI', 'cqi_dl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'cqi_dl', 'DL CQI Histogram', 'CQI', 'cqi_dl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'mcs_ul', 'UL MCS Histogram', 'MCS', 'mcs_ul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'mcs_ul', 'UL MCS Histogram', 'MCS', 'mcs_ul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'mcs_dl', 'DL MCS Histogram', 'MCS', 'mcs_dl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'mcs_dl', 'DL MCS Histogram', 'MCS', 'mcs_dl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'eff_ul', 'UL MCS Efficiency Histogram', 'MCS Efficiency', 'eff_ul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'eff_ul', 'UL MCS Efficiency Histogram', 'MCS Efficiency', 'eff_ul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'eff_dl', 'DL MCS Efficiency Histogram', 'MCS Efficiency', 'eff_dl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'eff_dl', 'DL MCS Efficiency Histogram', 'MCS Efficiency', 'eff_dl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'rul', 'UL Throughput Histogram', 'Throughput (Mbps)', 'rul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'rdl', 'DL Throughput Histogram', 'Throughput (Mbps)', 'rdl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'lul', 'UL Latency Histogram', 'Latency (s)', 'lul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'lul', 'UL Latency Histogram', 'Latency (s)', 'lul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'ldl', 'DL Latency Histogram', 'Latency (s)', 'ldl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'ldl', 'DL Latency Histogram', 'Latency (s)', 'ldl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'ilul', 'UL IP Latency Histogram', 'Latency (s)', 'ilul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'ilul', 'UL IP Latency Histogram', 'Latency (s)', 'ilul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'ildl', 'DL IP Latency Histogram', 'Latency (s)', 'ildl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'ildl', 'DL IP Latency Histogram', 'Latency (s)', 'ildl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'eul', 'UL Error Rate Histogram', 'Error Rate (Mbps)', 'eul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'eul', 'UL Error Rate Histogram', 'Error Rate (Mbps)', 'eul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'edl', 'DL Error Rate Histogram', 'Error Rate (Mbps)', 'edl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'edl', 'DL Error Rate Histogram', 'Error Rate (Mbps)', 'edl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'gul', 'UL Generation Rate Histogram', 'Rate (Mbps)', 'gul_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'gul', 'UL Generation Rate Histogram', 'Rate (Mbps)', 'gul_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'gdl', 'DL Generation Rate Histogram', 'Rate (Mbps)', 'gdl_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 6), title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'gdl', 'DL Generation Rate Histogram', 'Rate (Mbps)', 'gdl_3d_hist_all_ue_multi.png', outdir=out_dir, figsize=(20, 20), colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")
    try: plot_histograms_all_ue_multi(post_processing_list, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_hist_all_ue_multi.png', outdir=out_dir)
    except: print("[INFO]: Error while plotting.")
    try: plot_3d_histograms_all_ue_multi(post_processing_list, 'ri', 'Rank Indicator Histogram', 'Rank', 'ri_3d_hist_all_ue_multi.png', outdir=out_dir, colorMask=colorMask, title_size=20.0, label_size=20.0, tick_size=20.0)
    except: print("[INFO]: Error while plotting.")



if __name__ == "__main__":
    main()
