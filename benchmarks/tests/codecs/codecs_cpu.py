import os
import glob

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import *

def discover_datasets(root):
    datasets = []

    for entry in os.scandir(root):
        if entry.is_file():
            datasets.append(entry.path)

        elif entry.is_dir():
            for dirpath, _, filenames in os.walk(entry.path):
                for f in filenames:
                    datasets.append(
                        os.path.join(dirpath, f)
                    )

    return sorted(datasets)

CODEC_DIR = os.path.join(
    os.path.dirname(__file__),
    'src',
    'codecs'
)

DATASET_DIR = "/home/memcabe/compression/benchmarks/datasets"

compressor_scripts = sorted(glob.glob(f'{CODEC_DIR}/*.sh'))
dataset_files = discover_datasets(DATASET_DIR)

if not compressor_scripts:
    compressor_scripts = ['__missing_codec__']

if not dataset_files:
    dataset_files = ['__missing_dataset__']


@rfm.simple_test
class CompressionBenchmark(rfm.RunOnlyRegressionTest):

    compressor = parameter(compressor_scripts)
    dataset = parameter(dataset_files)

    valid_systems = ['*']
    valid_prog_environs = ['*']

    executable = 'bash'

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

    def compression_time(self):
        return sn.extractsingle(
        r'time:compress_many <uint32> = ([0-9.]+)',
        self.stderr,
        1,
        float
    )

    @performance_function('s')
    def decompression_time(self):
        return sn.extractsingle(
            r'decompression_time:\s*([0-9.]+)',
            self.stderr,
            1,
            float
        )

    @performance_function('')
    def compression_ratio(self):
        return sn.extractsingle(
            r'compression_ratio:\s*([0-9.]+)',
            self.stderr,
            1,
            float
        )

    @performance_function('MB/s')
    def throughput(self):
        return sn.extractsingle(
            r'throughput:\s*([0-9.]+)',
            self.stdout,
            1,
            float
        )
