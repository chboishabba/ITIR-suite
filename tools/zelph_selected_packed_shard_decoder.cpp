// Read one exact published Zelph packed shard, selecting only requested nodes/names.
// This is a schema adapter, not a second graph index, query engine or authority.
//
// Build with the same generated upstream Cap'n Proto header and C++ sources as
// tools/zelph_bin_filtered_route_builder.cpp:
//   g++ -std=c++17 -O2 -I aur/zelph/build-local/src/lib/io \
//     tools/zelph_selected_packed_shard_decoder.cpp \
//     aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
//     -lcapnp -lkj -o tools/zelph_selected_packed_shard_decoder
//
// Usage:
//   ... --file <shard.capnp-packed> --section left --chunk-index 0 --node 123
//   ... --file <shard.capnp-packed> --section nodeOfName --chunk-index 1 \
//       --lang wikidata --qid Q10403939
//
// Output is a bounded JSON observation; SHA and exact original-bin byte-range
// verification are SEPARATE Python acceptance gates.
#include <capnp/serialize-packed.h>
#include <kj/io.h>
#include <zelph/zelph.capnp.h>

#include <cstdint>
#include <cctype>
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <map>
#include <set>
#include <utility>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {
constexpr size_t kMaxNeighborsDefault = 200000;

struct Args {
    std::filesystem::path file;
    std::string section;
    std::string language{"wikidata"};
    uint32_t chunk_index{0};
    bool chunk_given{false};
    std::set<uint64_t> nodes;
    std::set<std::string> qids;
    size_t max_neighbors{kMaxNeighborsDefault};
    bool stream_name_rows{false};
    uint64_t max_name_rows{10000000};
    bool adjacency_bloom{false};
    uint64_t max_key_rows{2000000};
};

std::string escaped(std::string_view value) {
    std::string output;
    for (unsigned char c : value) {
        switch (c) {
            case '"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (c < 0x20) {
                    char buf[7];
                    std::snprintf(buf, sizeof(buf), "\\u%04x", c);
                    output += buf;
                } else {
                    output += static_cast<char>(c);
                }
        }
    }
    return output;
}

uint64_t parse_number(const std::string& value, const char* label) {
    if (value.empty()) throw std::runtime_error(std::string("empty ") + label);
    for (unsigned char c : value) {
        if (!std::isdigit(c)) throw std::runtime_error(std::string("invalid ") + label);
    }
    size_t used = 0;
    auto n = std::stoull(value, &used, 10);
    if (used != value.size()) throw std::runtime_error(std::string("invalid ") + label);
    return n;
}

Args parse_args(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        std::string flag(argv[i]);
        auto next = [&]() -> std::string {
            if (i + 1 >= argc) throw std::runtime_error("missing argument for " + flag);
            return std::string(argv[++i]);
        };
        if (flag == "--file") args.file = next();
        else if (flag == "--section") args.section = next();
        else if (flag == "--lang") args.language = next();
        else if (flag == "--chunk-index") {
            auto n = parse_number(next(), "chunk-index");
            if (n > UINT32_MAX) throw std::runtime_error("chunk-index overflow");
            args.chunk_index = static_cast<uint32_t>(n);
            args.chunk_given = true;
        }
        else if (flag == "--node") args.nodes.insert(parse_number(next(), "node"));
        else if (flag == "--qid") args.qids.insert(next());
        else if (flag == "--stream-name-rows") args.stream_name_rows = true;
        else if (flag == "--adjacency-bloom") args.adjacency_bloom = true;
        else if (flag == "--max-key-rows") {
            auto n = parse_number(next(), "max-key-rows");
            if (n == 0 || n > 100000000)
                throw std::runtime_error("invalid bounded adjacency key count");
            args.max_key_rows = n;
        }
        else if (flag == "--max-name-rows") {
            auto n = parse_number(next(), "max-name-rows");
            if (n == 0 || n > 100000000)
                throw std::runtime_error("invalid max-name-rows bound");
            args.max_name_rows = n;
        }
        else if (flag == "--max-neighbors") {
            auto n = parse_number(next(), "max-neighbors");
            if (n == 0 || n > 1000000) throw std::runtime_error("invalid neighbor cap");
            args.max_neighbors = static_cast<size_t>(n);
        }
        else throw std::runtime_error("unknown flag: " + flag);
    }
    if (args.file.empty() || !args.chunk_given ||
        (args.section != "left" && args.section != "right" &&
         args.section != "nameOfNode" && args.section != "nodeOfName")) {
        throw std::runtime_error("file, section, and chunk-index required");
    }
    if (!std::filesystem::is_regular_file(args.file))
        throw std::runtime_error("packed shard file absent");
    if (args.stream_name_rows && args.adjacency_bloom)
        throw std::runtime_error("original name streaming and adjacency bloom are disjoint modes");
    if (args.adjacency_bloom) {
        if ((args.section != "left" && args.section != "right")
            || !args.qids.empty() || !args.nodes.empty())
            throw std::runtime_error("native original adjacency bloom requires one whole direction chunk and no selectors");
    } else if (args.stream_name_rows) {
        if ((args.section != "nodeOfName" && args.section != "nameOfNode")
                || !args.qids.empty() || !args.nodes.empty())
            throw std::runtime_error("name-row streaming requires name section and no selectors");
    } else if ((args.section == "nodeOfName" && args.qids.empty()) ||
               (args.section != "nodeOfName" && args.nodes.empty())) {
        throw std::runtime_error("selected QIDs or nodes required for shard section");
    }
    return args;
}

template <typename Integer>
void print_integer_set(const std::set<Integer>& values) {
    std::cout << "[";
    bool first = true;
    for (auto v : values) {
        if (!first) std::cout << ",";
        std::cout << v;
        first = false;
    }
    std::cout << "]";
}

struct SelectedAdjacency {
    uint64_t node_id{0};
    std::set<uint64_t> neighbours;
    uint64_t values_seen{0};
    bool truncated{false};
};

void print_adj_chunk(
    capnp::PackedMessageReader& reader, const Args& args
) {
    auto chunk = reader.getRoot<zelph::network::AdjChunk>();
    if (std::string(chunk.getWhich().cStr()) != args.section ||
        chunk.getChunkIndex() != args.chunk_index)
        throw std::runtime_error("packed adjacency shard direction/chunk mismatch");
    std::map<uint64_t, SelectedAdjacency> seen;
    for (auto pair : chunk.getPairs()) {
        const uint64_t id = pair.getNode();
        if (args.nodes.count(id) == 0) continue;
        // The original whole-.bin filtered-route builder allows more than
        // one native AdjPair for the same node within or across chunks,
        // unions all neighbour values, and counts every occurrence. Match
        // those SAME original semantics instead of treating a repeated row
        // as a missing/invalid source. Do not silently drop duplicate values
        // or claim exact coverage when the bounded unique set truncates.
        auto& row = seen[id];
        row.node_id = id;
        for (uint64_t other : pair.getAdj()) {
            ++row.values_seen;
            if (row.neighbours.size() < args.max_neighbors ||
                row.neighbours.count(other) != 0) {
                row.neighbours.insert(other);
            } else {
                row.truncated = true;
            }
        }
    }
    std::cout << ",\"rows\":[";
    bool first = true;
    for (const auto& [id, row] : seen) {
        if (!first) std::cout << ",";
        first = false;
        std::cout << "{\"node_id\":" << id << ",\"neighbors\":";
        print_integer_set(row.neighbours);
        std::cout << ",\"values_seen\":" << row.values_seen
                  << ",\"truncated\":" << (row.truncated ? "true" : "false")
                  << "}";
    }
    std::cout << "]";
}

void print_name_of_node(
    capnp::PackedMessageReader& reader, const Args& args
) {
    auto chunk = reader.getRoot<zelph::network::NameChunk>();
    if (chunk.getChunkIndex() != args.chunk_index ||
        std::string(chunk.getLang().cStr()) != args.language)
        throw std::runtime_error("packed nameOfNode language/chunk mismatch");
    std::cout << ",\"language\":\"" << escaped(args.language) << "\",\"rows\":[";
    bool first = true;
    for (auto pair : chunk.getPairs()) {
        auto id = pair.getKey();
        if (args.nodes.count(id) == 0) continue;
        if (!first) std::cout << ",";
        first = false;
        std::cout << "{\"node_id\":" << id
                  << ",\"name\":\"" << escaped(pair.getValue().cStr()) << "\"}";
    }
    std::cout << "]";
}

void print_node_of_name(
    capnp::PackedMessageReader& reader, const Args& args
) {
    auto chunk = reader.getRoot<zelph::network::NodeNameChunk>();
    if (chunk.getChunkIndex() != args.chunk_index ||
        std::string(chunk.getLang().cStr()) != args.language)
        throw std::runtime_error("packed nodeOfName language/chunk mismatch");
    std::cout << ",\"language\":\"" << escaped(args.language) << "\",\"rows\":[";
    bool first = true;
    for (auto pair : chunk.getPairs()) {
        const std::string key = pair.getKey().cStr();
        if (args.qids.count(key) == 0) continue;
        if (!first) std::cout << ",";
        first = false;
        std::cout << "{\"name\":\"" << escaped(key)
                  << "\",\"node_id\":" << pair.getValue() << "}";
    }
    std::cout << "]";
}

// Emit EVERY upstream packed name row as bounded NDJSON, preserving duplicate
// name/node fibres, original row order and exact native key/value types.
// The consumer MUST require the terminal frame emitted only AFTER the exact
// packed message trailer check and process exit 0. A truncated stream cannot
// become a complete original name-domain witness.
uint64_t stream_all_native_name_rows(
    capnp::PackedMessageReader& reader, const Args& args
) {
    uint64_t count = 0;
    auto emit = [&](const std::string& name, uint64_t node_id) {
        if (count >= args.max_name_rows)
            throw std::runtime_error("native name-row count exceeds explicit bound");
        std::cout << "{\"version\":\"itir.zelph.native_original_name_row.v1\""
                  << ",\"section\":\"" << escaped(args.section) << "\""
                  << ",\"chunk_index\":" << args.chunk_index
                  << ",\"language\":\"" << escaped(args.language) << "\""
                  << ",\"row_index\":" << count
                  << ",\"name\":\"" << escaped(name) << "\""
                  << ",\"node_id\":" << node_id << "}\n";
        ++count;
    };
    if (args.section == "nodeOfName") {
        auto chunk = reader.getRoot<zelph::network::NodeNameChunk>();
        if (chunk.getChunkIndex() != args.chunk_index
                || std::string(chunk.getLang().cStr()) != args.language)
            throw std::runtime_error("native nodeOfName section/language/chunk mismatch");
        for (auto pair : chunk.getPairs()) {
            auto key = pair.getKey();
            emit(std::string(key.begin(), key.end()), pair.getValue());
        }
    } else if (args.section == "nameOfNode") {
        auto chunk = reader.getRoot<zelph::network::NameChunk>();
        if (chunk.getChunkIndex() != args.chunk_index
                || std::string(chunk.getLang().cStr()) != args.language)
            throw std::runtime_error("native nameOfNode section/language/chunk mismatch");
        for (auto pair : chunk.getPairs()) {
            auto name = pair.getValue();
            emit(std::string(name.begin(), name.end()), pair.getKey());
        }
    } else {
        throw std::runtime_error("cannot exhaustively stream a non-name chunk");
    }
    return count;
}


constexpr uint64_t kAdjBloomBits = 1ull << 24;
constexpr uint64_t kAdjBloomMask = kAdjBloomBits - 1;
constexpr size_t kAdjBloomBytes = static_cast<size_t>(kAdjBloomBits / 8);

uint64_t adjacency_bloom_mix(uint64_t input) {
    input += 0x9e3779b97f4a7c15ull;
    input = (input ^ (input >> 30)) * 0xbf58476d1ce4e5b9ull;
    input = (input ^ (input >> 27)) * 0x94d049bb133111ebull;
    return input ^ (input >> 31);
}

void write_le_u32(uint32_t number) {
    for (int shift = 0; shift < 32; shift += 8)
        std::cout.put(static_cast<char>((number >> shift) & 0xff));
}
void write_le_u64(uint64_t number) {
    for (int shift = 0; shift < 64; shift += 8)
        std::cout.put(static_cast<char>((number >> shift) & 0xff));
}

// Complete original source-native AdjChunk membership sketch. A Bloom
// negative is exact (under validated decoder and full original byte witness);
// a positive is only a CANDIDATE and MUST be replayed against the genuine
// original native shard. Because the upstream adjacency map is unordered,
// no guessed numeric node ranges or modulo/ordinal chunk routes are used.
std::pair<std::vector<unsigned char>, uint64_t>
build_native_original_adjacency_bloom(
    capnp::PackedMessageReader& reader, const Args& args
) {
    auto chunk = reader.getRoot<zelph::network::AdjChunk>();
    if (std::string(chunk.getWhich().cStr()) != args.section ||
        chunk.getChunkIndex() != args.chunk_index)
        throw std::runtime_error("original adjacency bloom direction/chunk mismatch");
    std::vector<unsigned char> bitmap(kAdjBloomBytes, 0);
    uint64_t count = 0;
    for (auto pair : chunk.getPairs()) {
        if (++count > args.max_key_rows)
            throw std::runtime_error("original native adjacency bloom row count exceeds bound");
        const uint64_t node = pair.getNode();
        const uint64_t h1 = adjacency_bloom_mix(node ^ 0x243f6a8885a308d3ull);
        const uint64_t h2 = adjacency_bloom_mix(node ^ 0x13198a2e03707344ull) | 1ull;
        for (uint64_t i = 0; i < 7; ++i) {
            const uint64_t bit = (h1 + i * h2) & kAdjBloomMask;
            bitmap[static_cast<size_t>(bit >> 3)] |=
                static_cast<unsigned char>(1u << (bit & 7));
        }
    }
    return {std::move(bitmap), count};
}

} // namespace

int main(int argc, char** argv) {
    try {
        const auto args = parse_args(argc, argv);
        FILE* fp = std::fopen(args.file.c_str(), "rb");
        if (!fp) throw std::runtime_error("failed to open packed shard");
        try {
            kj::FdInputStream raw(fileno(fp));
            kj::BufferedInputStreamWrapper buffered(raw);
            capnp::ReaderOptions options;
            options.traversalLimitInWords = 1ull << 32;
            options.nestingLimit = 128;
            uint64_t rows_streamed = 0;
            std::vector<unsigned char> bloom;
            {
                capnp::PackedMessageReader message(buffered, options);
                if (args.adjacency_bloom) {
                    auto built = build_native_original_adjacency_bloom(message, args);
                    bloom = std::move(built.first);
                    rows_streamed = built.second;
                } else if (args.stream_name_rows) {
                    rows_streamed = stream_all_native_name_rows(message, args);
                } else {
                    std::cout << "{\"version\":\"itir.zelph.selected_native_capnp_decode.v1\""
                              << ",\"section\":\"" << escaped(args.section) << "\""
                              << ",\"chunk_index\":" << args.chunk_index;
                    if (args.section == "left" || args.section == "right")
                        print_adj_chunk(message, args);
                    else if (args.section == "nameOfNode")
                        print_name_of_node(message, args);
                    else
                        print_node_of_name(message, args);
                }
            }
            // The physical object must contain *one exact* packed chunk,
            // not a valid first message followed by ignored bytes.
            kj::byte extra;
            if (buffered.tryRead(&extra, 1, 1) != 0)
                throw std::runtime_error("unexpected trailing bytes after packed shard");
            if (args.adjacency_bloom) {
                // The entire bloom is emitted ONLY after the original packed
                // message passes the exact EOF/zero-trailer verification.
                // Binary v1: magic[8], uint32 chunk LE, 4 option bytes,
                // bitmap[2^21], magic[8], uint64 row_count LE.
                std::cout.write("ZLBLOOM1", 8);
                write_le_u32(args.chunk_index);
                std::cout.put(args.section == "left" ? '\0' : '\1');
                std::cout.put('\7');
                std::cout.put('\30'); // 24 decimal: bitmap size = 2^24 bits
                std::cout.put('\0');
                std::cout.write(reinterpret_cast<const char*>(bloom.data()),
                                static_cast<std::streamsize>(bloom.size()));
                std::cout.write("ZLBEND01", 8);
                write_le_u64(rows_streamed);
                std::cout.flush();
                if (!std::cout)
                    throw std::runtime_error("native original adjacency bloom output failure");
            } else if (args.stream_name_rows) {
                // Only after EXACT packed-message EOF can a caller accept
                // the complete stream as an exhaustive native chunk decode.
                std::cout << "{\"version\":\"itir.zelph.native_original_name_rows_end.v1\""
                          << ",\"section\":\"" << escaped(args.section) << "\""
                          << ",\"chunk_index\":" << args.chunk_index
                          << ",\"language\":\"" << escaped(args.language) << "\""
                          << ",\"rows_emitted\":" << rows_streamed
                          << ",\"candidate_only\":true,\"authority\":false}\n";
            } else {
            std::cout << ",\"candidate_only\":true,\"authority\":false}\n";
            }
            std::fclose(fp);
            return 0;
        } catch (...) {
            std::fclose(fp);
            throw;
        }
    } catch (const std::exception& exc) {
        std::cerr << "zelph_selected_packed_shard_decoder: " << exc.what() << "\n";
        return 2;
    }
}
