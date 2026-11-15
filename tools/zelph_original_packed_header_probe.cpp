// P0 read-only original Zelph packed-header probe.
// Takes ONLY the standalone bytes=0..headerLength-1 from the exact original
// .bin or local native fixture. Does NOT open the 82 GiB graph, infer node
// routes, or authenticate upstream HTTP provenance.
//
// Compile with the SAME original generated schema used by native decoder:
// clang++ -fuse-ld=lld -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
//  tools/zelph_original_packed_header_probe.cpp \
//  aur/zelph/build-local/src/lib/io/zelph.capnp.c++ -lcapnp -lkj -o probe

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/io.h>
#include <zelph/zelph.capnp.h>

#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

class CountingBufferedInputStream : public kj::BufferedInputStream {
public:
    explicit CountingBufferedInputStream(kj::InputStream& inner) : buffered(inner) {}
    kj::ArrayPtr<const kj::byte> tryGetReadBuffer() override {
        return buffered.tryGetReadBuffer();
    }
    size_t tryRead(void* buf, size_t minBytes, size_t maxBytes) override {
        const auto n = buffered.tryRead(buf, minBytes, maxBytes);
        bytes += n;
        return n;
    }
    void skip(size_t count) override { buffered.skip(count); bytes += count; }
    size_t bytesRead() const { return bytes; }
private:
    kj::BufferedInputStreamWrapper buffered;
    size_t bytes{0};
};
}

int main(int argc, char** argv) {
    try {
        if (argc != 3 || std::string(argv[1]) != "--header-file")
            throw std::runtime_error("usage: probe --header-file <one exact packed header>");
        const std::filesystem::path path(argv[2]);
        const auto size = std::filesystem::file_size(path);
        if (size == 0 || size > 1024 * 1024)
            throw std::runtime_error("packed header missing or exceeds 1 MiB budget");
        FILE* fp = std::fopen(path.c_str(), "rb");
        if (!fp) throw std::runtime_error("cannot open packed original header");
        try {
            kj::FdInputStream raw(fileno(fp));
            CountingBufferedInputStream buffered(raw);
            capnp::ReaderOptions opts;
            opts.traversalLimitInWords = 1ull << 20;
            opts.nestingLimit = 32;
            // Reader destruction finishes any deferred segments.
            uint32_t left{}, right{}, nameOfNode{}, nodeOfName{};
            {
                capnp::PackedMessageReader message(buffered, opts);
                const auto impl = message.getRoot<zelph::network::ZelphImpl>();
                left = impl.getLeftChunkCount();
                right = impl.getRightChunkCount();
                nameOfNode = impl.getNameOfNodeChunkCount();
                nodeOfName = impl.getNodeOfNameChunkCount();
            }
            if (buffered.bytesRead() != size)
                throw std::runtime_error("packed header contains trailing or unconsumed bytes");
            const int closed = std::fclose(fp);
            fp = nullptr;
            if (closed != 0) throw std::runtime_error("original header close failed");
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
        } catch (...) {
            if (fp) std::fclose(fp);
            throw;
        }
    } catch (const std::exception& e) {
        std::cerr << "zelph original packed-header probe: " << e.what() << "\n";
        return 2;
    }
}
