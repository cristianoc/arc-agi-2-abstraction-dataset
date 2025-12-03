#!/usr/bin/env python

'''
Adapted from https://www.kaggle.com/code/allegich/arc-agi-2025-visualization-all-1000-120-tasks
'''

import argparse
import json
from os import path
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colors

# 0:black, 1:blue, 2:red, 3:green, 4:yellow, # 5:gray, 6:magenta, 7:orange, 8:sky, 9:brown
cmap = colors.ListedColormap([
    '#000000', '#0074D9', '#FF4136', '#2ECC40', '#FFDC00',
    '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'
])
norm = colors.Normalize(vmin=0, vmax=9)

def plot_task(
    json_path: str,
    task,
    save: bool,
    size=2.5,
    w1=0.9
):
    num_train = len(task['train'])
    num_test = len(task['test'])
    wn = num_train + num_test
    has_actual = 'actual' in task['train'][0]
    has_actual = any('actual' in entry for entry in task['train'] + task['test'])
    fig, axs = plt.subplots(
        3 if has_actual else 2,
        wn,
        figsize=(size*wn,2*size)
    )
    for j in range(num_train):     
        plot_one(axs[0, j], j, task, 'train', 'input',  w=w1)
        plot_one(axs[1, j], j, task, 'train', 'output', w=w1)
        if has_actual:
            plot_one(axs[2, j], j, task, 'train', 'actual', w=w1)
    for k in range(num_test):
        plot_one(axs[0, j+k+1], k, task, 'test', 'input', w=w1)
        plot_one(axs[1, j+k+1], k, task, 'test', 'output', w=w1)
        if has_actual:
            plot_one(axs[2, j+k+1], k, task, 'test', 'actual', w=w1)
    axs[1, j+1].set_xticklabels([])
    axs[1, j+1].set_yticklabels([])
    axs[1, j+1] = plt.figure(1).add_subplot(111)
    axs[1, j+1].set_xlim([0, wn])
    
    # Separators
    colorSeparator = 'white'
    for m in range(1, wn):
        axs[1, j+1].plot([m,m],[0,1],'--', linewidth=1, color = colorSeparator)
    axs[1, j+1].plot([num_train,num_train],[0,1],'-', linewidth=3, color = colorSeparator)
    axs[1, j+1].axis("off")

    # Frame and background
    fig.patch.set_linewidth(5)
    fig.patch.set_edgecolor('black')
    fig.patch.set_facecolor('#444444')
    fig.tight_layout()
    if save:
        plt.savefig(path.splitext(json_path)[0] + '.png')
    else:
        fig.canvas.manager.set_window_title(Path(json_path).stem)
        plt.show()  
    plt.close()
   
def plot_one(
    ax,
    i: int,
    task,
    train_or_test: str,
    input_or_output: str,
    solution=None,
    w=0.8
):
    fs = 12
    task[train_or_test][i]
    matrix = task[train_or_test][i].get(input_or_output, None)
    ax.set_title(
        f'{train_or_test} {input_or_output} {i}' + (' (error)' if matrix is None else ''),
        fontsize=fs,
        color='#dddddd'
    )
    if matrix is not None:
        ax.imshow(matrix, cmap=cmap, norm=norm)
        plt.setp(plt.gcf().get_axes(), xticklabels=[], yticklabels=[])
        ax.set_xticks([x-0.5 for x in range(1 + len(matrix[0]))])
        ax.set_yticks([x-0.5 for x in range(1 + len(matrix))])
        ax.grid(visible= True, which = 'both', color = '#666666', linewidth = w)
        ax.tick_params(axis='both', color='none', length=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--save', default=False, action='store_true', help='Save PNG render instead of popup window')
    parser.add_argument('-i', '--id', default=False, action='store_true', help='Provide input by hash ID. If given, json-path can be omitted')
    parser.add_argument('json-path', nargs='+')
    args = parser.parse_args()
    json_paths = getattr(args, 'json-path')
    if args.id:
        for i, json_path in enumerate(json_paths):
            json_paths[i] = path.join('ARC-AGI', 'data', 'training', json_path) + '.json'
    for json_path in json_paths:
        with open(json_path) as f:
            task = json.load(f)
        if len(json_paths) > 1:
            print(json_path)
        plot_task(json_path, task, args.save)
