#!/usr/bin/env python3
"""
Standardized Figure Style Configuration for SCCMU Paper

This module provides consistent matplotlib styling for all figures
to ensure proper alignment, spacing, and professional appearance.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# Set matplotlib style parameters for consistent figures
def configure_figure_style():
    """
    Configure matplotlib for consistent, publication-quality figures
    """
    # Set style parameters
    plt.style.use('default')
    
    # Font settings
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    mpl.rcParams['font.size'] = 12
    mpl.rcParams['axes.titlesize'] = 14
    mpl.rcParams['axes.labelsize'] = 12
    mpl.rcParams['xtick.labelsize'] = 10
    mpl.rcParams['ytick.labelsize'] = 10
    mpl.rcParams['legend.fontsize'] = 11
    
    # Figure settings
    mpl.rcParams['figure.dpi'] = 300
    mpl.rcParams['savefig.dpi'] = 300
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.facecolor'] = 'white'
    mpl.rcParams['savefig.edgecolor'] = 'none'
    
    # Line and marker settings
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['lines.markersize'] = 8
    mpl.rcParams['lines.markeredgewidth'] = 1
    
    # Grid settings
    mpl.rcParams['grid.alpha'] = 0.3
    mpl.rcParams['grid.linewidth'] = 0.5
    
    # Axes settings
    mpl.rcParams['axes.linewidth'] = 1
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.grid'] = True
    
    # Color settings
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler('color', [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # olive
        '#17becf'   # cyan
    ])

def create_standard_figure(nrows=1, ncols=1, figsize=None):
    """
    Create a figure with standard sizing and styling
    
    Args:
        nrows: Number of subplot rows
        ncols: Number of subplot columns
        figsize: Custom figure size (width, height)
    
    Returns:
        fig, axes: Matplotlib figure and axes objects
    """
    if figsize is None:
        # Standard sizes based on subplot layout
        if nrows == 1 and ncols == 1:
            figsize = (12, 6)
        elif nrows == 1 and ncols == 2:
            figsize = (16, 6)
        elif nrows == 1 and ncols == 3:
            figsize = (18, 6)
        elif nrows == 2 and ncols == 1:
            figsize = (12, 10)
        else:
            figsize = (12, 8)
    
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    # Ensure axes is always iterable
    if nrows == 1 and ncols == 1:
        axes = [axes]
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    return fig, axes

def save_figure(fig, filename, **kwargs):
    """
    Save figure with standard settings
    
    Args:
        fig: Matplotlib figure object
        filename: Output filename
        **kwargs: Additional arguments for plt.savefig
    """
    # Default save parameters
    save_params = {
        'dpi': 300,
        'bbox_inches': 'tight',
        'facecolor': 'white',
        'edgecolor': 'none',
        'pad_inches': 0.2
    }
    
    # Update with any provided parameters
    save_params.update(kwargs)
    
    # Apply tight layout with padding
    fig.tight_layout(pad=2.0)
    
    # Save the figure
    fig.savefig(filename, **save_params)
    print(f"📊 Figure saved: {filename}")

def apply_standard_formatting(ax, title=None, xlabel=None, ylabel=None):
    """
    Apply standard formatting to an axis
    
    Args:
        ax: Matplotlib axis object
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
    """
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    
    # Apply standard grid
    ax.grid(True, alpha=0.3, linewidth=0.5)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Set tick parameters
    ax.tick_params(axis='both', which='major', labelsize=10)

# Initialize the style when module is imported
configure_figure_style()

if __name__ == "__main__":
    # Test the configuration
    print("Figure style configuration loaded successfully!")
    print("Use create_standard_figure() and save_figure() for consistent plots.")
