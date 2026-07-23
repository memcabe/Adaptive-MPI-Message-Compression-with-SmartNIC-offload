import os
import glob
import csv
import re

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *


def discover_datasets(root):
    datasets = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Don't descend into hidden directories
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith('.')
        ]

        for filename in filenames:
            # Ignore hidden files (.gitkeep, .DS_Store, etc.)
            if filename.startswith('.'):
                continue

            path = os.path.join(dirpath, filename)

            if os.path.isfile(path):
                datasets.append(path)

    return sorted(datasets)


CODEC_DIR = os.path.join(
    os.path.dirname(__file__),
    'src',
    'codecs'
)

DATASET_DIR = "/home/memcabe/compression/MPI_Offload/benchmarks/datasets"

compressor_scripts = sorted(glob.glob(f'{CODEC_DIR}/*.sh'))
dataset_files = discover_datasets(DATASET_DIR)

if not compressor_scripts:
    compressor_scripts = ['__missing_codec__']

if not dataset_files:
    dataset_files = ['__missing_dataset__']

CSV_FILE = "benchmk_rslts/cpu_results.csv"


@rfm.simple_test
class CompressionBenchmark(rfm.RunOnlyRegressionTest):

    compressor = parameter(compressor_scripts)
    dataset = parameter(dataset_files)

    valid_systems = ['*']
    valid_prog_environs = ['*']

    executable = 'bash'

    CSV_COLUMNS = [
        (
            "compression_time_us",
            r'time:compress_many\s+<uint32>\s*=\s*([0-9.]+)'
        ),
        (
            "decompression_time_us",
            r'time:decompress_many\s+<uint32>\s*=\s*([0-9.]+)'
        ),
        (
            "compression_ratio",
            r'size:compression_ratio\s+<double>\s*=\s*([0-9.]+)'
        ),
        (
            "compression_throughput_MBps",
            r'composite:compression_rate_many\s+<[^>]+>\s*=\s*([0-9.]+)'
        ),
        (
            "decompression_throughput_MBps",
            r'composite:decompression_rate_many\s+<[^>]+>\s*=\s*([0-9.]+)'
        ),
    ]

    @run_after('init')
    def setup_run(self):

        self.executable_opts = [
            self.compressor,
            self.dataset
        ]

        self.descr = (
            f'{os.path.basename(self.compressor)} '
            f'{os.path.basename(self.dataset)}'
        )

    @sanity_function
    def validate_run(self):
        return sn.assert_found(r'STATUS=PASS', self.stdout)

    @run_after('sanity')
    def append_results_csv(self):

        errfile = os.path.join(self.stagedir, "rfm_job.err")

        with open(errfile, "r") as f:
            err = f.read()

        write_header = not os.path.exists(CSV_FILE)

        row = [
            os.path.basename(self.compressor),
            os.path.basename(self.dataset),
        ]

        for _, regex in self.CSV_COLUMNS:
            match = re.search(regex, err)

            if match:
                row.append(float(match.group(1)))
            else:
                row.append(None)

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            if write_header:
                writer.writerow(
                    ["compressor", "dataset"] +
                    [name for name, _ in self.CSV_COLUMNS]
                )

            writer.writerow(row)
