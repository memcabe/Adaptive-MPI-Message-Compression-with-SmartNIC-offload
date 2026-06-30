// sz3_bluefield.cpp

#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

// DOCA headers
#include <doca_dev.h>
#include <doca_mmap.h>
#include <doca_buf.h>
#include <doca_buf_inventory.h>
#include <doca_workq.h>

// Abstract compressor

std::vector<uint8_t>
sz3_compress(const void* input, size_t bytes)
{
    std::vector<uint8_t> compressed;

    // call SZ3

    return compressed;
}

// BlueField Context

struct BlueFieldContext
{
    doca_dev* dev = nullptr;

    doca_mmap* mmap = nullptr;

    doca_buf_inventory* inventory = nullptr;

    doca_workq* workq = nullptr;
};

// Initialization

bool init_doca(BlueFieldContext& ctx)
{
    doca_error_t result;

    // Open device

    result = doca_dev_open(NULL, &ctx.dev);

    if(result != DOCA_SUCCESS)
        return false;

    // Memory map

    result = doca_mmap_create(&ctx.mmap);

    if(result != DOCA_SUCCESS)
        return false;

    result = doca_mmap_add_dev(ctx.mmap, ctx.dev);

    if(result != DOCA_SUCCESS)
        return false;

    // Buffer inventory

    result =
        doca_buf_inventory_create(
            1024,
            &ctx.inventory);

    if(result != DOCA_SUCCESS)
        return false;

    // Work queue

    result = doca_workq_create(128, &ctx.workq);

    if(result != DOCA_SUCCESS)
        return false;

    return true;
}

// Cleanup

void cleanup_doca(BlueFieldContext& ctx)
{
    if(ctx.workq)
        doca_workq_destroy(ctx.workq);

    if(ctx.inventory)
        doca_buf_inventory_destroy(ctx.inventory);

    if(ctx.mmap)
        doca_mmap_destroy(ctx.mmap);

    if(ctx.dev)
        doca_dev_close(ctx.dev);
}

// Export host memory to DPU

bool register_host_buffer(
    BlueFieldContext& ctx,
    void* ptr,
    size_t bytes)
{
    doca_error_t result;

    result =
        doca_mmap_set_memrange(
            ctx.mmap,
            ptr,
            bytes);

    if(result != DOCA_SUCCESS)
        return false;

    result =
        doca_mmap_start(
            ctx.mmap);

    if(result != DOCA_SUCCESS)
        return false;

    // export mmap so DPU can access host memory

    void* export_desc = nullptr;
    size_t export_size = 0;

    result =
        doca_mmap_export_dpu(
            ctx.mmap,
            ctx.dev,
            &export_desc,
            &export_size);

    if(result != DOCA_SUCCESS)
        return false;

    std::cout
        << "exported mmap: "
        << export_size
        << " bytes\n";

    return true;
}

// Main benchmark

int main(int argc, char** argv)
{
    if(argc != 2)
    {
        std::cerr
            << "usage: "
            << argv[0]
            << " dataset\n";

        return 1;
    }

    // Read dataset

    std::ifstream in(
        argv[1],
        std::ios::binary);

    std::vector<uint8_t> input(
        (std::istreambuf_iterator<char>(in)),
        std::istreambuf_iterator<char>());

    std::cout
        << "input_bytes="
        << input.size()
        << "\n";

    // DOCA startup

    BlueFieldContext ctx;

    if(!init_doca(ctx))
    {
        std::cerr
            << "DOCA init failed\n";

        return 1;
    }

    // Register memory

    if(!register_host_buffer(
            ctx,
            input.data(),
            input.size()))
    {
        std::cerr
            << "buffer registration failed\n";

        return 1;
    }

    // Benchmark region

    auto start =
        std::chrono::high_resolution_clock::now();

    // DPU would execute compression here

    auto compressed =
        sz3_compress(
            input.data(),
            input.size());

    auto stop =
        std::chrono::high_resolution_clock::now();

    // Metrics

    double ms =
        std::chrono::duration<double,
        std::milli>(
            stop - start).count();

    double ratio =
        compressed.empty()
        ? 0.0
        : static_cast<double>(input.size())
          / compressed.size();

    double throughput_mb =
        (input.size() / 1e6)
        / (ms / 1000.0);

    std::cout
        << "compression_time_ms="
        << ms
        << "\n";

    std::cout
        << "compression_ratio="
        << ratio
        << "\n";

    std::cout
        << "throughput_MBps="
        << throughput_mb
        << "\n";

    cleanup_doca(ctx);

    return 0;
}
