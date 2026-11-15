// P0 read-only original Zelph packed-header probe.
// Parses ONLY the bounded standalone bytes=0..headerLength-1 from the exact
// original .bin (or a native synthetic fixture). The memory-backed KJ stream
// permits an exact logical unread-tail check, avoiding buffered fd prefetch.
//
// Build with the upstream original generated Zelph Cap'n Proto schema, NOT a
// copy or guessed JSON translation. No whole-graph or source authority.

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/io.h>
#include <zelph/zelph.capnp.h>

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    try {
        if (argc != 3 || std::string(argv[1]) != "--header-file")
            throw std::runtime_error("usage: probe --header-file <one exact packed header>");
        const std::filesystem::path path(argv[2]);
        const auto size = std::filesystem::file_size(path);
        if (size == 0 || size > 1024 * 1024)
            throw std::runtime_error("packed header missing or exceeds 1 MiB budget");
        std::vector<kj::byte> bytes(static_cast<size_t>(size));
        std::ifstream file(path, std::ios::binary);
        if (!file || !file.read(reinterpret_cast<char*>(bytes.data()),
                                static_cast<std::streamsize>(size))) {
            throw std::runtime_error("cannot read full exact packed source header");
        }
        file.close();
        if (!file) throw std::runtime_error("original packed header stream close failed");

        // ArrayInputStream (unlike fd buffered prefetch) owns a logical read
        // cursor over the entire exact header interval. It must outlive the
        // PackedMessageReader, including its deferred multi-segment skips.
        kj::ArrayInputStream input(kj::arrayPtr(bytes.data(), bytes.size()));
        capnp::ReaderOptions opts;
        opts.traversalLimitInWords = 1ull << 20;
        opts.nestingLimit = 32;
        uint32_t left{}, right{}, nameOfNode{}, nodeOfName{};
        {
            capnp::PackedMessageReader message(input, opts);
            const auto impl = message.getRoot<zelph::network::ZelphImpl>();
            left = impl.getLeftChunkCount();
            right = impl.getRightChunkCount();
            nameOfNode = impl.getNameOfNodeChunkCount();
            nodeOfName = impl.getNodeOfNameChunkCount();
        }
        if (input.tryGetReadBuffer().size() != 0)
            throw std::runtime_error("packed original header contains an unread trailer");

        std::cout << "{"
                  << "\"version\":\"itir.zelph.native_original_packed_header_probe.v1\","
                  << "\"header_size_bytes\":" << size << ","
                  << "\"leftChunkCount\":" << left << ","
                  << "\"rightChunkCount\":" << right << ","
                  << "\"nameOfNodeChunkCount\":" << nameOfNode << ","
                  << "\"nodeOfNameChunkCount\":" << nodeOfName << ","
                  << "\"source_upstream_authenticity_proved\":false,"
                  << "\"all_original_shard_bytes_checked\":false,"
                  << "\"edit_authority\":false"
                  << "}\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "zelph original packed-header probe: " << e.what() << "\n";
        return 2;
    }
}
