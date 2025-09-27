import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Wedge, FancyBboxPatch, Circle
from typing import Dict, Any
import matplotlib.colors as mcolors
import json

# ==============================================================================
# Plotting Style & Font Configuration
# ==============================================================================
# Using a clean, modern sans-serif font family. Matplotlib will fall back
# through the list if the preferred fonts are not found on the system.


# ==============================================================================
# Data & Configuration
# ==============================================================================

# --- Design Palette (Updated with new blue theme) ---
FIG_BG_COLOR = "#ffffff"          # White background
CARD_BG_COLOR = "#ffffff"         # Clean white cards
SUBTLE_TEXT_COLOR = "#2f2f2f"     # Soft dark grey for text
DIVIDER_COLOR = "#F3F3F3"          # Light grey for dividers
MIN_COLOR = "#8CD2F8"             # Light blue for low values (0%)
MAX_COLOR = "#0A9CEB"             # Strong blue for high values (100%)
TITLE_COLOR = "#0A9CEB"            # Static color for section headers, consistent with theme


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_color_shade(min_hex: str, max_hex: str, value: float) -> str:
    """
    Interpolates between two hex colors based on a value between 0 and 1.
    A value of 1.0 returns the max_color, 0.0 returns the min_color.
    """
    min_rgb = mcolors.to_rgb(min_hex)
    max_rgb = mcolors.to_rgb(max_hex)
    
    # Linearly interpolate between the min and max colors.
    new_rgb = [
        (1 - value) * min_rgb[i] + value * max_rgb[i]
        for i in range(3)
    ]
    
    return mcolors.to_hex(new_rgb)

def get_prob_assessment(prob: float) -> str:
    """Return a qualitative confidence assessment based on probability."""
    if prob > 0.75:
        return "High Confidence Binder"
    if prob > 0.4:
        return "Moderate Confidence Binder"
    return "Low Confidence Binder"


def get_affinity_assessment(aff_val: float) -> str:
    """Return a qualitative binding strength based on the affinity value."""
    if aff_val < -1:
        return "Strong Binder"
    if aff_val < 1:
        return "Moderate Binder"
    return "Weak Binder / Decoy"


# ==============================================================================
# Core Plotting Function
# ==============================================================================

def create_analysis_card(ax: plt.Axes, title: str, prob: float, aff_val: float, color: str):
    """
    Draws a single, self-contained analysis card with a top-down layout.
    """
    ax.axis("off")
    ax.set_aspect('equal', adjustable='box')

    # --- Card Background with Rounded Border ---
    # We use FancyBboxPatch to create rounded corners for the card.
    ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
        facecolor=CARD_BG_COLOR,
        edgecolor=MAX_COLOR,
        boxstyle="round,pad=0,rounding_size=0.04",
        transform=ax.transAxes,
        linewidth=1))

    # --- Main Card Title ---
    ax.text(0.5, 0.94, title, ha="center", fontsize=14, fontweight="bold", transform=ax.transAxes)

    # --- Horizontal Divider ---
    ax.plot([0.05, 0.90], [0.5, 0.5], color=DIVIDER_COLOR, linestyle="--", linewidth=1.5, transform=ax.transAxes)

    # ==========================================================================
    # Top Section: Hit Discovery Potential
    # ==========================================================================
    ax.text(0.5, 0.90, "Hit Discovery", ha="center", fontsize=14, color=TITLE_COLOR, transform=ax.transAxes)

    # --- Donut Chart with Rounded Ends ---
    # We now use ax.plot with a thick linewidth and rounded caps to draw the donut.
    donut_center = (0.5, 0.72)
    donut_radius = 0.13
    plot_linewidth = 16 # Calculated based on figure size and desired width

    # Draw the background track
    theta_track = np.linspace(0, 2 * np.pi, 200)
    x_track = donut_center[0] + donut_radius * np.cos(theta_track)
    y_track = donut_center[1] + donut_radius * np.sin(theta_track)
    ax.plot(x_track, y_track, color=DIVIDER_COLOR, linewidth=plot_linewidth, transform=ax.transAxes)
    
    # Draw the value arc
    if prob > 0:
        start_angle = 90
        end_angle = start_angle - (prob * 360)
        theta_value = np.linspace(np.deg2rad(end_angle), np.deg2rad(start_angle), 200)
        x_value = donut_center[0] + donut_radius * np.cos(theta_value)
        y_value = donut_center[1] + donut_radius * np.sin(theta_value)
        ax.plot(x_value, y_value, color=color, linewidth=plot_linewidth, solid_capstyle='round', transform=ax.transAxes)

    ax.text(donut_center[0], donut_center[1], f"{prob:.1%}", ha="center", va="center", fontsize=22, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.53, get_prob_assessment(prob), ha="center", fontsize=11, color=SUBTLE_TEXT_COLOR, style="italic", transform=ax.transAxes)

    # ==========================================================================
    # Bottom Section: Lead Optimization Metrics
    # ==========================================================================
    ax.text(0.5, 0.43, "Lead Optimization", ha="center", fontsize=14, color=TITLE_COLOR, transform=ax.transAxes)

    # --- Calculations ---
    ic50 = 10 ** aff_val
    delta_g = (6 - aff_val) * 1.364

    # --- Metric Labels ---
    ax.text(0.5, 0.33, f"log₁₀(IC₅₀): {aff_val:.3f}", ha="center", fontsize=12, transform=ax.transAxes)
    ax.text(0.5, 0.26, f"Predicted IC₅₀: {ic50:.2f} µM", ha="center", fontsize=13, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.20, f"ΔG: {delta_g:.2f} kcal/mol", ha="center", fontsize=12, transform=ax.transAxes)
    
    # --- Affinity Strength Meter ---
    meter_y_pos = 0.1
    meter_range = [-10, 2]
    
    norm_val = (aff_val - meter_range[0]) / (meter_range[1] - meter_range[0])
    bar_fill = 1 - norm_val
    bar_fill = max(0, min(1, bar_fill))

    ax.add_patch(Rectangle((0.3, meter_y_pos - 0.0001), 0.4, 0.02, facecolor=DIVIDER_COLOR, transform=ax.transAxes, clip_on=False))
    ax.add_patch(Rectangle((0.3, meter_y_pos - 0.0001), 0.4 * bar_fill, 0.02, facecolor=color, transform=ax.transAxes, clip_on=False))

    ax.text(0.3, meter_y_pos - 0.03, "Weak", ha="left", fontsize=9, color=SUBTLE_TEXT_COLOR, transform=ax.transAxes)
    ax.text(0.7, meter_y_pos - 0.03, "Strong", ha="right", fontsize=9, color=SUBTLE_TEXT_COLOR, transform=ax.transAxes)
    ax.text(0.5, 0.05, get_affinity_assessment(aff_val), ha="center", fontsize=11, color=SUBTLE_TEXT_COLOR, style="italic", transform=ax.transAxes)


# ==============================================================================
# Main Execution Block
# ==============================================================================

def main():
    """
    Main function to set up the figure, process data, and generate the dashboard.
    """
    # --- Load Data from External JSON file ---
    try:
        with open('affinity.json', 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print("Error: 'affinity.json' not found. Please ensure the data file is in the same directory.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode 'affinity.json'. Please check if it's a valid JSON file.")
        return
        
    # --- Figure Setup ---
    # Adjusted figsize for a better vertical card layout
    fig, axes = plt.subplots(1, 3, figsize=(22, 9), constrained_layout=True)
    fig.set_facecolor(FIG_BG_COLOR)

    # --- Data Processing ---
    card_data = [
        {
            "title": "Ensemble Model Analysis",
            "prob": json_data["affinity_probability_binary"],
            "aff_val": json_data["affinity_pred_value"],
        },
        {
            "title": "Model 1 Analysis",
            "prob": json_data["affinity_probability_binary1"],
            "aff_val": json_data["affinity_pred_value1"],
        },
        {
            "title": "Model 2 Analysis",
            "prob": json_data["affinity_probability_binary2"],
            "aff_val": json_data["affinity_pred_value2"],
        },
    ]

    # --- Card Creation ---
    # Loop through the data and populate the grid column by column.
    for ax, data in zip(axes, card_data):
        # Dynamically calculate color shade by interpolating between min and max colors
        dynamic_color = get_color_shade(MIN_COLOR, MAX_COLOR, data["prob"])
        create_analysis_card(ax, data["title"], data["prob"], data["aff_val"], dynamic_color)

    # --- Save Figure ---
    output_filename = "molecular_affinity_dashboard_revised.png"
    plt.savefig(
        output_filename,
        dpi=300,
        facecolor=FIG_BG_COLOR,
        bbox_inches="tight"
    )
    print(f"Dashboard saved successfully as '{output_filename}'")


if __name__ == "__main__":
    main()


