#!/usr/bin/env python
# coding: utf-8

# tgb - 11/1/2019 - Making figures for the UW+UCI paper from reduced pkl data

# In[1]:


import sys
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from pylab import *

# from uwnet.spectra import *
from wave.plots.jacobian import plot
from wave import *
import common
import wave

import logging

logging.basicConfig(level=logging.INFO)

# Define custom functions to plot Jacobian and growth rates
def plot_lrf(data):
    # basic plot
    coupler = WaveCoupler.from_tom_data(data)
    p = lrf["base_state"]["p"][::-1]
    plot((coupler.lrf.panes, p))
    plt.suptitle(name)


def plot_spectra(ax, data, **kwargs):
    coupler = WaveCoupler.from_tom_data(data)
    eig = compute_spectrum(coupler)

    scatter_spectra(eig, cbar=False, ax=ax)


def _invert_axes(ax):
    ax.invert_xaxis()
    ax.invert_yaxis()


def _remove_ylabel(axs):
    for ax in axs.flat:
        ax.yaxis.set_visible(False)


def _get_letter(i, j, ncol):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return alphabet[i * ncol + j]


def eig_lrf_plot(plot_data, eig_xlim=(-25, 25), eig_ylim=(-10, 10)):
    """plot_data: dict or (lrf, spectrum) tuples. The plot will show the lrfs as the first row and spectra as the second row
    """

    # Define variables for the plot
    stday = 24 * 3600  # Covert from 1/s to 1/d

    ncol = len(plot_data)
    width = 7.5 * ncol / 4 # was width originally for 4 panel layout
    fig, axs = plt.subplots(
        2, ncol, figsize=(width, 4), gridspec_kw=dict(hspace=0.5, wspace=0.01)
    )

    row_lrf = axs[0, :]
    row_eig = axs[1, :]

    lrf_kwargs = {"norm": SymLogNorm(1.0, vmin=-10, vmax=10), "cmap": "bwr"}

    for k, key in enumerate(plot_data):
        lrf, eigs = plot_data[key]
        p, lrf = lrf["base_state"]["p"], lrf["jacobian"]
        lrf_im = row_lrf[k].pcolormesh(p, p, stday * lrf["q"]["q"], **lrf_kwargs)
        _invert_axes(row_lrf[k])

        eig_im = scatter_spectra(eigs, cbar=False, ax=row_eig[k], s=4)
        row_lrf[k].set_title(_get_letter(0, k, ncol) + ") " + key, loc="left")
        row_eig[k].set_title(_get_letter(1, k, ncol) + ")", loc="left")
        row_eig[k].set_xlim(eig_xlim)
        row_eig[k].set_ylim(eig_ylim)

    # make labels
    _remove_ylabel(axs[:, 1:])
    axs[0, 0].set_ylabel("p (mb)")

    for ax in row_lrf:
        ax.set_xlabel("p (mb)")

    # colorbars
    cb_lrf = fig.colorbar(lrf_im, ax=row_lrf.tolist(), pad=0.01)
    cb_lrf.set_label("1/day")

    cb_eig = common.add_wavelength_colorbar(fig, eig_im, ax=row_eig.tolist(), pad=0.01)
    cb_eig.set_label("Wavenumber (1/k)")

    return fig


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


with open(INPUT) as f:
    lrfs = wave.load(f)

if OUTPUT == 'figs/fig10.pdf':
    items = ["Stable 1%", "Unstable 1%", "Unstable 10%", "Unstable 20%"]
elif OUTPUT == "figs/S2.pdf":
    items = ["Stable", "Unstable"]
    kwargs =  {'eig_xlim': (-300, 300)}
else:
    raise ValueError("Output not allowed.")

print(f"Plotting {items}")
print(f"Saving to {OUTPUT}")

couplers = {key: WaveCoupler.from_tom_data(lrfs[key]) for key in items}
logging.info("Computing the spectra")
plot_data = {
    key: (lrfs[key], compute_spectrum(coupler)) for key, coupler in couplers.items()
}
logging.info("Plotting the spectra")
fig = eig_lrf_plot(plot_data, **kwargs)
fig.savefig(OUTPUT)
