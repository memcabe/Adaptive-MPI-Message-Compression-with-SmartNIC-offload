#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "cpu_results.csv"

df = pd.read_csv(CSV_FILE)

avg = (
    df.groupby("compressor", as_index=False)
      .mean(numeric_only=True)
)

avg["compressor"] = (
    avg["compressor"]
       .str.replace(".sh", "", regex=False)
)

avg = avg.sort_values("compressor")

os.makedirs("plots", exist_ok=True)

metrics = [
    ("compression_time_us", "Compression Time (µs)"),
    ("decompression_time_us", "Decompression Time (µs)"),
    ("compression_ratio", "Compression Ratio"),
    ("compression_throughput_MBps", "Compression Throughput (MB/s)"),
    ("decompression_throughput_MBps", "Decompression Throughput (MB/s)")
]

for column, ylabel in metrics:

    plt.figure(figsize=(10, 6))

    bars = plt.bar(avg["compressor"], avg[column])

    plt.title(f"Average {ylabel}")
    plt.xlabel("Compressor")
    plt.ylabel(ylabel)

    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()

    plt.savefig(
        os.path.join("plots", f"{column}.png"),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

print("Plots written to ./plots/")
