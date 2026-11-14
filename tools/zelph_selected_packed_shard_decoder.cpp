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
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <map>
#include <set>
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
    if ((args.section == "nodeOfName" && args.qids.empty()) ||
        (args.section != "nodeOfName" && args.nodes.empty()))
        throw std::runtime_error("selected QIDs or nodes required for shard section");
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
        if (seen.count(id))
            throw std::runtime_error("duplicate same-node row in packed adjacency shard");
        SelectedAdjacency row;
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
        seen.emplace(id, std::move(row));
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
} // namespace

int main(int argc, char** argv) {
    try {
        const auto args = parse_args(argc, argv);
        FILE* fp = std::fopen(args.file.c_str(), "rb");
        if (!fp) throw std::runtime_error("failed to open packed shard");
        try {
            kj::FdInputStream raw(fileno(fp));
            capnp::ReaderOptions options;
            options.traversalLimitInWords = 1ull << 32;
            options.nestingLimit = 128;
            capnp::PackedMessageReader message(raw, options);
            std::cout << "{\"version\":\"itir.zelph.selected_native_capnp_decode.v1\""
                      << ",\"section\":\"" << escaped(args.section) << "\""
                      << ",\"chunk_index\":" << args.chunk_index;
            if (args.section == "left" || args.section == "right")
                print_adj_chunk(message, args);
            else if (args.section == "nameOfNode")
                print_name_of_node(message, args);
            else
                print_node_of_name(message, args);
            std::cout << ",\"candidate_only\":true,\"authority\":false}\n";
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
