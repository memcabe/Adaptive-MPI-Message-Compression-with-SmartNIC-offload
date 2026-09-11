#!/usr/bin/env python3

import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


CSV_FILE = "cpu_results.csv"
PLOT_DIR = "plots"

os.makedirs(PLOT_DIR, exist_ok=True)

# Load results
df = pd.read_csv(CSV_FILE)

# Remove ".sh" from compressor names
df["compressor"] = (
    df["compressor"]
      .str.replace(".sh", "", regex=False)
)

# Statistics

stats = (
    df.groupby("compressor")
      .agg(
          samples=("compressor", "size"),

          compression_time_mean=(
              "compression_time_us", "mean"
          ),
          compression_time_median=(
              "compression_time_us", "median"
          ),
          compression_time_std=(
              "compression_time_us", "std"
          ),
          compression_time_min=(
              "compression_time_us", "min"
          ),
          compression_time_max=(
              "compression_time_us", "max"
          ),

          decompression_time_mean=(
              "decompression_time_us", "mean"
          ),
          decompression_time_median=(
              "decompression_time_us", "median"
          ),
          decompression_time_std=(
              "decompression_time_us", "std"
          ),
          decompression_time_min=(
              "decompression_time_us", "min"
          ),
          decompression_time_max=(
              "decompression_time_us", "max"
          ),

          compression_ratio_mean=(
              "compression_ratio", "mean"
          ),
          compression_ratio_median=(
              "compression_ratio", "median"
          ),
          compression_ratio_std=(
              "compression_ratio", "std"
          ),
          compression_ratio_min=(
              "compression_ratio", "min"
          ),
          compression_ratio_max=(
              "compression_ratio", "max"
          ),

          compression_throughput_mean=(
              "compression_throughput_MBps", "mean"
          ),
          compression_throughput_median=(
              "compression_throughput_MBps", "median"
          ),
          compression_throughput_std=(
              "compression_throughput_MBps", "std"
          ),
          compression_throughput_min=(
              "compression_throughput_MBps", "min"
          ),
          compression_throughput_max=(
              "compression_throughput_MBps", "max"
          ),

          decompression_throughput_mean=(
              "decompression_throughput_MBps", "mean"
          ),
          decompression_throughput_median=(
              "decompression_throughput_MBps", "median"
          ),
          decompression_throughput_std=(
              "decompression_throughput_MBps", "std"
          ),
          decompression_throughput_min=(
              "decompression_throughput_MBps", "min"
          ),
          decompression_throughput_max=(
              "decompression_throughput_MBps", "max"
          ),
      )
      .reset_index()
)

# Coefficient of variation
# CV = standard deviation / mean

stats["compression_time_cv"] = (
    stats["compression_time_std"]
    / stats["compression_time_mean"]
)

stats["decompression_time_cv"] = (
    stats["decompression_time_std"]
    / stats["decompression_time_mean"]
)

stats["compression_ratio_cv"] = (
    stats["compression_ratio_std"]
    / stats["compression_ratio_mean"]
)

stats["compression_throughput_cv"] = (
    stats["compression_throughput_std"]
    / stats["compression_throughput_mean"]
)

stats["decompression_throughput_cv"] = (
    stats["decompression_throughput_std"]
    / stats["decompression_throughput_mean"]
)

# 95% confidence interval
# mean ± 1.96 * (std / sqrt(n))

for metric in [
    "compression_time_us",
    "decompression_time_us",
    "compression_ratio",
    "compression_throughput_MBps",
    "decompression_throughput_MBps"
]:

    mean = (
        df.groupby("compressor")[metric]
          .mean()
    )

    std = (
        df.groupby("compressor")[metric]
          .std()
    )

    count = (
        df.groupby("compressor")[metric]
          .count()
    )

    ci = 1.96 * std / count.pow(0.5)

    stats[f"{metric}_ci95"] = (
        stats["compressor"].map(ci)
    )


# Save statistics table
stats = stats.sort_values("compressor")

stats.to_csv(
    os.path.join(PLOT_DIR, "statistics.csv"),
    index=False
)

# Seaborn configuration

sns.set_theme(
    style="whitegrid",
    context="talk"
)

# Metrics to plot

metrics = [
    (
        "compression_time_us",
        "Compression Time",
        "µs"
    ),
    (
        "decompression_time_us",
        "Decompression Time",
        "µs"
    ),
    (
        "compression_ratio",
        "Compression Ratio",
        ""
    ),
    (
        "compression_throughput_MBps",
        "Compression Throughput",
        "MB/s"
    ),
    (
        "decompression_throughput_MBps",
        "Decompression Throughput",
        "MB/s"
    )
]

# Generate plots

for column, title, unit in metrics:

    # Bar plot

    plt.figure(figsize=(12, 7))

    ax = sns.barplot(
        data=df,
        x="compressor",
        y=column,
        estimator="mean",
        errorbar="sd",
        capsize=0.15
    )

    sns.stripplot(
        data=df,
        x="compressor",
        y=column,
        color="black",
        alpha=0.5,
        jitter=0.15,
        size=5
    )

    ax.set_title(
        f"{title}: Mean +- Standard Deviation"
    )

    ax.set_xlabel("Compressor")
    ax.set_ylabel(
        f"{title} ({unit})" if unit else title
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            PLOT_DIR,
            f"{column}_mean.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # Box plot

    plt.figure(figsize=(12, 7))

    ax = sns.boxplot(
        data=df,
        x="compressor",
        y=column
    )

    sns.stripplot(
        data=df,
        x="compressor",
        y=column,
        color="black",
        alpha=0.35,
        jitter=0.15,
        size=4
    )

    ax.set_title(
        f"{title}: Distribution"
    )

    ax.set_xlabel("Compressor")
    ax.set_ylabel(
        f"{title} ({unit})" if unit else title
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            PLOT_DIR,
            f"{column}_distribution.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


print("Plots written to ./plots/")
print("Statistics written to ./plots/statistics.csv")
