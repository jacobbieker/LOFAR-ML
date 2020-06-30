import json
import matplotlib.pyplot as plt



experiment_folder = "/home/jacob/Development/lofarnn/analysis/fixed_fast_all_size400_prop4096_depth101_batchSize4_anchorSize[[1, 2, 3, 4]]"
experiment_metrics_tiny = experiment_folder + '_frac0.1recall.npy'
experiment_metrics_small = experiment_folder + '_frac0.25recall.npy'
experiment_metrics_medium = experiment_folder + '_frac0.5recall.npy'
#experiment_metrics_large = experiment_folder + '_frac0.75recall.npy'
#experiment_metrics_all = experiment_folder + '_frac1.0recall.npy'

iteration = list(range(0,400000,1000))

import numpy as np

precision_tiny = np.load(experiment_metrics_tiny, allow_pickle=True)
precision_small = np.load(experiment_metrics_small, allow_pickle=True)
precision_medium = np.load(experiment_metrics_medium, allow_pickle=True)
#precision_large = np.load(experiment_metrics_large, allow_pickle=True)
#precision = np.load(experiment_metrics_all, allow_pickle=True)


plt.plot(
    iteration,
    precision_tiny, label='0.1')
plt.plot(
    iteration,
    precision_small, label='0.25')
plt.plot(
    iteration,
    precision_medium, label='0.5')
#plt.plot(
#    iteration,
#    precision_large, label='0.75')
#plt.plot(
#    iteration,
#    precision, label='1.0')
plt.legend(loc='upper right')
plt.title("Evaluation AR (Fixed Size) Batch Size 4")
plt.xlabel("Iteration")
plt.ylabel("Average Recall")
plt.savefig("Fixed_Eval_AR_Batch4.png", dpi=300)
plt.clf()
plt.cla()

experiment_folder = '/home/jacob/fixed_metrics'

def load_json_arr(json_path):
    lines = []
    with open(json_path, 'r') as f:
        for line in f:
            lines.append(json.loads(line))
    return lines

experiment_metrics_tiny = load_json_arr(experiment_folder + '/metrics0.1.json')
experiment_metrics_small = load_json_arr(experiment_folder + '/metrics0.25.json')
experiment_metrics_medium = load_json_arr(experiment_folder + '/metrics0.5.json')
experiment_metrics_large = load_json_arr(experiment_folder + '/metrics0.75.json')
experiment_metrics_all = load_json_arr(experiment_folder + '/metrics1.0.json')

precision_tiny = []
for x in experiment_metrics_tiny:
    try:
        precision_tiny.append(x['validation_loss'])
    except:
        continue
precision_small = []
for x in experiment_metrics_small:
    try:
        precision_small.append(x['validation_loss'])
    except:
        continue
precision_medium = []
for x in experiment_metrics_medium:
    try:
        precision_medium.append(x['validation_loss'])
    except:
        continue
precision_large = []
for x in experiment_metrics_large:
    try:
        precision_large.append(x['validation_loss'])
    except:
        continue
precision_huge = []
for x in experiment_metrics_all:
    try:
        precision_huge.append(x['validation_loss'])
    except:
        continue

plt.plot(
    [x['iteration'] for x in experiment_metrics_tiny],
    [x['total_loss'] for x in experiment_metrics_tiny], label='0.1')
plt.plot(
    [x['iteration'] for x in experiment_metrics_small],
    [x['total_loss'] for x in experiment_metrics_small], label='0.25')
plt.plot(
    [x['iteration'] for x in experiment_metrics_medium],
    [x['total_loss'] for x in experiment_metrics_medium], label='0.5')
plt.plot(
    [x['iteration'] for x in experiment_metrics_large],
    [x['total_loss'] for x in experiment_metrics_large], label='0.75')
plt.plot(
    [x['iteration'] for x in experiment_metrics_all],
    [x['total_loss'] for x in experiment_metrics_all], label='1.0')
plt.plot(
    list(range(0,400000,1000)),
    precision_tiny, label='0.1 Val')
plt.plot(
    list(range(0,400000,1000)),
    precision_small, label='0.25 Val')
plt.plot(
    list(range(0,400000,1000)),
    precision_medium, label='0.5 Val')
plt.plot(
    list(range(0,400000,1000)),
    precision_large, label='0.75 Val')
plt.plot(
    list(range(0,400000,1000)),
    precision_huge, label='1.0 Val')
plt.legend(loc='upper right')
plt.title("Total Training Loss (Fixed Size) Batch Size 4")
plt.xlabel("Iteration")
plt.ylabel("Total Loss")
plt.yscale("log")
plt.savefig("Fixed_Training_Loss_Batch4.png", dpi=300)
plt.clf()
plt.cla()


precision = []
for x in experiment_metrics_all:
    try:
        precision.append(x['bbox/AP'])
    except:
        continue
precision_tiny = []
for x in experiment_metrics_tiny:
    try:
        precision_tiny.append(x['bbox/AP'])
    except:
        continue
precision_small = []
for x in experiment_metrics_small:
    try:
        precision_small.append(x['bbox/AP'])
    except:
        continue
precision_medium = []
for x in experiment_metrics_medium:
    try:
        precision_medium.append(x['bbox/AP'])
    except:
        continue
precision_large = []
for x in experiment_metrics_large:
    try:
        precision_large.append(x['bbox/AP'])
    except:
        continue

iteration = list(range(0,400000,1000))

plt.plot(
    iteration,
    precision_tiny, label='0.1')
plt.plot(
    iteration,
    precision_small, label='0.25')
plt.plot(
    iteration,
    precision_medium, label='0.5')
plt.plot(
    iteration,
    precision_large, label='0.75')
plt.plot(
    iteration,
    precision, label='1.0')
plt.legend(loc='upper right')
plt.title("Evaluation AP (Fixed Size) Batch Size 4")
plt.xlabel("Iteration")
plt.ylabel("Average Precision")
plt.savefig("Fixed_Eval_AP_batch4.png", dpi=300)
plt.clf()
plt.cla()

experiment_folder = '/run/media/jacob/Present_1/reports/variable_all'
experiment_metrics_tiny = load_json_arr(experiment_folder + '/metrics0.1.json')
experiment_metrics_small = load_json_arr(experiment_folder + '/metrics0.25.json')
experiment_metrics_medium = load_json_arr(experiment_folder + '/metrics0.5.json')
experiment_metrics_large = load_json_arr(experiment_folder + '/metrics0.75.json')
experiment_metrics_all = load_json_arr(experiment_folder + '/metrics1.0.json')

plt.plot(
    [x['iteration'] for x in experiment_metrics_tiny],
    [x['total_loss'] for x in experiment_metrics_tiny], label='0.1')
plt.plot(
    [x['iteration'] for x in experiment_metrics_small],
    [x['total_loss'] for x in experiment_metrics_small], label='0.25')
plt.plot(
    [x['iteration'] for x in experiment_metrics_medium],
    [x['total_loss'] for x in experiment_metrics_medium], label='0.5')
plt.plot(
    [x['iteration'] for x in experiment_metrics_large],
    [x['total_loss'] for x in experiment_metrics_large], label='0.75')
plt.plot(
    [x['iteration'] for x in experiment_metrics_all],
    [x['total_loss'] for x in experiment_metrics_all], label='1.0')
plt.legend(loc='upper right')
plt.title("Total Training Loss (Variable Size)")
plt.xlabel("Iteration")
plt.ylabel("Total Loss")
plt.yscale("log")
plt.savefig("Variable_Training_Loss.png", dpi=300)
plt.clf()
plt.cla()


precision = []
for x in experiment_metrics_all:
    try:
        precision.append(x['bbox/AP'])
    except:
        continue
precision_tiny = []
for x in experiment_metrics_tiny:
    try:
        precision_tiny.append(x['bbox/AP'])
    except:
        continue
precision_small = []
for x in experiment_metrics_small:
    try:
        precision_small.append(x['bbox/AP'])
    except:
        continue
precision_medium = []
for x in experiment_metrics_medium:
    try:
        precision_medium.append(x['bbox/AP'])
    except:
        continue
precision_large = []
for x in experiment_metrics_large:
    try:
        precision_large.append(x['bbox/AP'])
    except:
        continue

iteration = list(range(0,400000,10000))

plt.plot(
    iteration,
    precision_tiny, label='0.1')
plt.plot(
    iteration,
    precision_small, label='0.25')
plt.plot(
    iteration,
    precision_medium, label='0.5')
plt.plot(
    iteration,
    precision_large, label='0.75')
plt.plot(
    iteration,
    precision, label='1.0')
plt.legend(loc='upper right')
plt.title("Evaluation AP (Variable Size)")
plt.xlabel("Iteration")
plt.ylabel("Average Precision")
plt.savefig("Variable_Eval_AP.png", dpi=300)
