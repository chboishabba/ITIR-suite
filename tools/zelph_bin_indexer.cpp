// Simple sidecar offset indexer for zelph .bin files.
// Produces JSON with offsets/lengths for main header and each chunk section.
// Build: g++ -std=c++17 -O2 tools/zelph_bin_indexer.cpp -lcapnp -lkj -o tools/zelph_bin_indexer

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/debug.h>
#include <kj/io.h>

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

#include <zelph/zelph.capnp.h>

class CountingInputStream : public kj::InputStream {
public:
    explicit CountingInputStream(kj::InputStream& inner) : inner(inner) {}

    size_t tryRead(void* buffer, size_t minBytes, size_t maxBytes) override {
        auto n = inner.tryRead(buffer, minBytes, maxBytes);
        count += n;
        return n;
    }

    void skip(size_t bytes) override {
        inner.skip(bytes);
        count += bytes;
    }

    uint64_t bytesRead() const { return count; }

private:
    kj::InputStream& inner;
    uint64_t         count{0};
};

struct Range {
    uint32_t index;
    uint64_t offset;
    uint64_t length;
    std::string which;  // for adjacency: "left"/"right"; empty otherwise
    std::string lang;   // for name chunks
};

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: zelph_bin_indexer <file.bin>\n";
        return 1;
    }

    const std::filesystem::path path(argv[1]);
    FILE* file = fopen(path.c_str(), "rb");
    if (!file) {
        std::perror("fopen");
        return 1;
    }

    kj::FdInputStream raw(fileno(file));
    CountingInputStream counting(raw);
    kj::BufferedInputStreamWrapper buffered(counting);

    capnp::ReaderOptions options;
    options.traversalLimitInWords = 1ull << 32;
    options.nestingLimit          = 128;

    // Main header
    uint64_t headerOffset = counting.bytesRead();
    capnp::PackedMessageReader mainMessage(buffered, options);
    auto impl = mainMessage.getRoot<zelph::network::ZelphImpl>();
    uint64_t headerLength = counting.bytesRead() - headerOffset;

    uint32_t leftCount       = impl.getLeftChunkCount();
    uint32_t rightCount      = impl.getRightChunkCount();
    uint32_t nameOfNodeCount = impl.getNameOfNodeChunkCount();
    uint32_t nodeOfNameCount = impl.getNodeOfNameChunkCount();

    std::vector<Range> left, right, name, nodeName;
    left.reserve(leftCount);
    right.reserve(rightCount);
    name.reserve(nameOfNodeCount);
    nodeName.reserve(nodeOfNameCount);

    auto readAdjSection = [&](uint32_t count, std::vector<Range>& out, const char* whichTag) {
        for (uint32_t i = 0; i < count; ++i) {
            uint64_t before = counting.bytesRead();
            capnp::PackedMessageReader chunkMessage(buffered, options);
            auto chunk = chunkMessage.getRoot<zelph::network::AdjChunk>();
            Range r;
            r.which  = chunk.getWhich().cStr();
            r.index  = chunk.getChunkIndex();
            r.offset = before;
            r.length = counting.bytesRead() - before;
            out.push_back(r);
        }
    };

    readAdjSection(leftCount, left, "left");
    readAdjSection(rightCount, right, "right");

    for (uint32_t i = 0; i < nameOfNodeCount; ++i) {
        uint64_t before = counting.bytesRead();
        capnp::PackedMessageReader chunkMessage(buffered, options);
        auto chunk = chunkMessage.getRoot<zelph::network::NameChunk>();
        Range r;
        r.index  = chunk.getChunkIndex();
        r.lang   = chunk.getLang().cStr();
        r.offset = before;
        r.length = counting.bytesRead() - before;
        name.push_back(r);
    }

    for (uint32_t i = 0; i < nodeOfNameCount; ++i) {
        uint64_t before = counting.bytesRead();
        capnp::PackedMessageReader chunkMessage(buffered, options);
        auto chunk = chunkMessage.getRoot<zelph::network::NodeNameChunk>();
        Range r;
        r.index  = chunk.getChunkIndex();
        r.lang   = chunk.getLang().cStr();
        r.offset = before;
        r.length = counting.bytesRead() - before;
        nodeName.push_back(r);
    }

    fclose(file);

    // Emit JSON to stdout.
    auto emitRanges = [](const char* name, const std::vector<Range>& v) {
        std::cout << "  \"" << name << "\": [\n";
        for (size_t i = 0; i < v.size(); ++i) {
            const auto& r = v[i];
            std::cout << "    {\"chunkIndex\":" << r.index
                      << ",\"offset\":" << r.offset
                      << ",\"length\":" << r.length;
            if (!r.which.empty()) std::cout << ",\"which\":\"" << r.which << "\"";
            if (!r.lang.empty()) std::cout << ",\"lang\":\"" << r.lang << "\"";
            std::cout << "}" << (i + 1 < v.size() ? "," : "") << "\n";
        }
        std::cout << "  ]";
    };

    std::cout << "{\n";
    std::cout << "  \"file\":\"" << path.string() << "\",\n";
    std::cout << "  \"header\": {\"offset\":0,\"length\":" << headerLength << "},\n";
    emitRanges("left", left); std::cout << ",\n";
    emitRanges("right", right); std::cout << ",\n";
    emitRanges("nameOfNode", name); std::cout << ",\n";
    emitRanges("nodeOfName", nodeName); std::cout << "\n";
    std::cout << "}\n";

    return 0;
}
