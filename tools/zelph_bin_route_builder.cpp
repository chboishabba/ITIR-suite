// Build an exact chunk-membership route sidecar for a Zelph .bin file.
// Output is a streaming JSON prototype route artifact built from real chunk payloads.
// Build:
//   g++ -std=c++17 -O2 \
//     -I aur/zelph/build-local/src/lib/io \
//     tools/zelph_bin_route_builder.cpp \
//     aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
//     -lcapnp -lkj \
//     -o tools/zelph_bin_route_builder

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/io.h>

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

#include <zelph.capnp.h>

class CountingBufferedInputStream : public kj::BufferedInputStream {
public:
    explicit CountingBufferedInputStream(kj::InputStream& inner) : buffered(inner) {}

    kj::ArrayPtr<const kj::byte> tryGetReadBuffer() override {
        return buffered.tryGetReadBuffer();
    }

    size_t tryRead(void* buffer, size_t minBytes, size_t maxBytes) override {
        auto n = buffered.tryRead(buffer, minBytes, maxBytes);
        count += n;
        return n;
    }

    void skip(size_t bytes) override {
        buffered.skip(bytes);
        count += bytes;
    }

    uint64_t bytesRead() const { return count; }

private:
    kj::BufferedInputStreamWrapper buffered;
    uint64_t                       count{0};
};

static std::string jsonEscape(const std::string& input) {
    std::string out;
    out.reserve(input.size() + 8);
    for (unsigned char ch : input) {
        switch (ch) {
            case '\"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (ch < 0x20) {
                    char buf[7];
                    std::snprintf(buf, sizeof(buf), "\\u%04x", ch);
                    out += buf;
                } else {
                    out += static_cast<char>(ch);
                }
        }
    }
    return out;
}

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: zelph_bin_route_builder <file.bin> <output.json>\n";
        return 1;
    }

    const std::filesystem::path binPath(argv[1]);
    const std::filesystem::path outPath(argv[2]);

    FILE* file = fopen(binPath.c_str(), "rb");
    if (!file) {
        std::perror("fopen");
        return 1;
    }

    std::ofstream out(outPath);
    if (!out.is_open()) {
        std::cerr << "Failed to open output file '" << outPath.string() << "'\n";
        fclose(file);
        return 1;
    }

    try {
        kj::FdInputStream           raw(fileno(file));
        CountingBufferedInputStream counting(raw);

        capnp::ReaderOptions options;
        options.traversalLimitInWords = 1ull << 32;
        options.nestingLimit          = 128;

        const uint64_t headerOffset = counting.bytesRead();
        capnp::PackedMessageReader mainMessage(counting, options);
        auto impl = mainMessage.getRoot<zelph::network::ZelphImpl>();
        const uint64_t headerLength = counting.bytesRead() - headerOffset;

        const uint32_t leftCount       = impl.getLeftChunkCount();
        const uint32_t rightCount      = impl.getRightChunkCount();
        const uint32_t nameOfNodeCount = impl.getNameOfNodeChunkCount();
        const uint32_t nodeOfNameCount = impl.getNodeOfNameChunkCount();

        out << "{\n";
        out << "  \"routeVersion\": \"zelph-node-route/v1\",\n";
        out << "  \"source\": {\n";
        out << "    \"binPath\": \"" << jsonEscape(binPath.string()) << "\",\n";
        out << "    \"binSizeBytes\": " << std::filesystem::file_size(binPath) << ",\n";
        out << "    \"headerLengthBytes\": " << headerLength << ",\n";
        out << "    \"leftChunkCount\": " << leftCount << ",\n";
        out << "    \"rightChunkCount\": " << rightCount << ",\n";
        out << "    \"nameOfNodeChunkCount\": " << nameOfNodeCount << ",\n";
        out << "    \"nodeOfNameChunkCount\": " << nodeOfNameCount << "\n";
        out << "  },\n";
        out << "  \"routing\": {\n";

        auto writeAdjSection = [&](const char* sectionName, uint32_t count, bool trailingComma) {
            out << "    \"" << sectionName << "\": [\n";
            for (uint32_t i = 0; i < count; ++i) {
                capnp::PackedMessageReader chunkMessage(counting, options);
                auto chunk = chunkMessage.getRoot<zelph::network::AdjChunk>();
                auto pairs = chunk.getPairs();

                out << "      {\"chunkIndex\":" << chunk.getChunkIndex()
                    << ",\"which\":\"" << jsonEscape(chunk.getWhich().cStr()) << "\""
                    << ",\"entryCount\":" << pairs.size()
                    << ",\"nodes\":[";
                for (uint32_t j = 0; j < pairs.size(); ++j) {
                    if (j != 0) out << ",";
                    out << pairs[j].getNode();
                }
                out << "]}";
                if (i + 1 < count) out << ",";
                out << "\n";
            }
            out << "    ]";
            if (trailingComma) out << ",";
            out << "\n";
        };

        auto writeNameSection = [&](const char* sectionName, uint32_t count, bool reverseName, bool trailingComma) {
            out << "    \"" << sectionName << "\": [\n";
            for (uint32_t i = 0; i < count; ++i) {
                capnp::PackedMessageReader chunkMessage(counting, options);
                out << "      ";
                if (!reverseName) {
                    auto pairs = chunkMessage.getRoot<zelph::network::NameChunk>();
                    auto list = pairs.getPairs();
                    out << "{\"lang\":\"" << jsonEscape(pairs.getLang().cStr()) << "\""
                        << ",\"chunkIndex\":" << pairs.getChunkIndex()
                        << ",\"entryCount\":" << list.size()
                        << ",\"nodes\":[";
                    for (uint32_t j = 0; j < list.size(); ++j) {
                        if (j != 0) out << ",";
                        out << list[j].getKey();
                    }
                    out << "]}";
                } else {
                    auto pairs = chunkMessage.getRoot<zelph::network::NodeNameChunk>();
                    auto list = pairs.getPairs();
                    out << "{\"lang\":\"" << jsonEscape(pairs.getLang().cStr()) << "\""
                        << ",\"chunkIndex\":" << pairs.getChunkIndex()
                        << ",\"entryCount\":" << list.size()
                        << ",\"names\":[";
                    for (uint32_t j = 0; j < list.size(); ++j) {
                        if (j != 0) out << ",";
                        out << "\"" << jsonEscape(list[j].getKey().cStr()) << "\"";
                    }
                    out << "]}";
                }
                if (i + 1 < count) out << ",";
                out << "\n";
            }
            out << "    ]";
            if (trailingComma) out << ",";
            out << "\n";
        };

        writeAdjSection("left", leftCount, true);
        writeAdjSection("right", rightCount, true);
        writeNameSection("nameOfNode", nameOfNodeCount, false, true);
        writeNameSection("nodeOfName", nodeOfNameCount, true, false);

        out << "  }\n";
        out << "}\n";

        fclose(file);
        out.close();
        return 0;
    } catch (...) {
        fclose(file);
        throw;
    }
}
