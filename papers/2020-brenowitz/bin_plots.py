#!/usr/bin/env python
# coding: utf-8

# In `heating_dependence_on_lts_moisture`, I produce plots of varying Q1 and Q2 for the mean within mid-tropospheric moisture (Q) and lower-tropospheric stability (LTS) bins **separately**. Since Q and LTS covary, it is important to study them in a two dimensional phase space. This notebook makes similar plots, but conditioned on a given value of "LTS".

# # Version information

# In[1]:

# # Functions

# In[2]:

# Adjustments to path
import os
import shutil
import xarray as xr
import matplotlib.pyplot as plt
from plots.plot_binned import plot_line_by_key_altair
import argparse

import sys


SP_PATH = sys.argv[1]
CRM_PATH = sys.argv[2]
OUTPUT = "figs/bins.pdf"
Q_LABEL = "Q (mm)"
LTS_LABEL = "LTS (K)"

def colorbar_lims(x):
    m = max(abs(x.min().item()), abs(x.max().item()))
    return {'vmin': -m, 'vmax': m}

def plot_row(binned, axs):
    common_kwargs = {'add_labels': False, 'add_colorbar': False}

    i = 0
    count_im = binned['count'].plot(ax=axs[i], **common_kwargs)
    plt.colorbar(count_im, ax=axs[i])
    i+=1

    lims = colorbar_lims(binned.net_precipitation_src)
    common_kwargs.update(lims)
    im = binned.net_precipitation_nn.plot(cmap='seismic', ax=axs[i], **common_kwargs)
    i+=1

    binned.net_precipitation_src.plot(cmap='seismic', ax=axs[i], **common_kwargs)
    plt.colorbar(im, ax=axs[1:].tolist())

    for ax in axs[1:]:
        ax.set_ylabel('')


def set_row_titles(axs, labels):
    for label, ax in zip(labels, axs):
        ax.set_title(label, loc="left")


def label_axes(axs):

    for ax in axs.flat:
        ax.set_xlabel('')
        ax.set_ylabel('')

    for ax in axs[:, 0]:
        ax.set_ylabel(Q_LABEL)

    for ax in axs[-1, :]:
        ax.set_xlabel(LTS_LABEL)

if __name__ == "__main__":
    datasets = dict(
    SP = xr.open_dataset(SP_PATH),
    CRM = xr.open_dataset(CRM_PATH))

    fig, axs = plt.subplots(2, 3, figsize=(7, 4), constrained_layout=True)
    row1 = axs[0, :]
    row2 = axs[1, :]

    plot_row(datasets['CRM'], axs=row1)
    plot_row(datasets['SP'], axs=row2)

    def label_row(ax, label):
        ax.text(-.5, 0.4, label, transform=ax.transAxes, rotation=90, ha='center', va='center')

    label_row(row1[0], "GRCM")
    label_row(row2[0], "SP-CAM")

    set_row_titles(row1, ["a) Histogram (count) \n", "b) Predicted P-E\n   (mm/day)", "c) Actual P-E\n   (mm/day)"])
    set_row_titles(row2, ["d)", "e)", "f)"])
    label_axes(axs)



    fig.savefig(OUTPUT)
