// Build a bounded exact route receipt for selected Wikidata QID strings.
//
// This producer intentionally does not materialize the global zelph-node-route/v1
// JSON sidecar. It performs two read-only passes over the source .bin:
//   1. resolve exact QID strings through nodeOfName for --lang (default wikidata)
//   2. resolve those numeric node ids to exact left/right/nameOfNode chunk memberships
//
// Build (same generated schema/toolchain as the existing route builder):
//   g++ -std=c++17 -O2 \
//     -I aur/zelph/build-local/src/lib/io \
//     tools/zelph_bin_filtered_route_builder.cpp \
//     aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
//     -lcapnp -lkj -o tools/zelph_bin_filtered_route_builder

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/io.h>

#include <cstdio>
#include <cctype>
#include <stdexcept>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <string_view>

#include <zelph/zelph.capnp.h>

class CountingBufferedInputStream : public kj::BufferedInputStream {
public:
    explicit CountingBufferedInputStream(kj::InputStream& inner) : buffered(inner) {}
    kj::ArrayPtr<const kj::byte> tryGetReadBuffer() override { return buffered.tryGetReadBuffer(); }
    size_t tryRead(void* buffer, size_t minBytes, size_t maxBytes) override {
        const auto n = buffered.tryRead(buffer, minBytes, maxBytes);
        count += n;
        return n;
    }
    void skip(size_t bytes) override { buffered.skip(bytes); count += bytes; }
    uint64_t bytesRead() const { return count; }
private:
    kj::BufferedInputStreamWrapper buffered;
    uint64_t count{0};
};

struct Args {
    std::filesystem::path bin;
    std::filesystem::path output;
    std::string lang{"wikidata"};
    std::set<std::string> qids;
    // Numeric source frontier roots are not fabricated Wikidata QIDs.
    std::set<uint64_t> extra_numeric_nodes;
};

struct Header {
    uint32_t left{};
    uint32_t right{};
    uint32_t name_of_node{};
    uint32_t node_of_name{};
    uint64_t header_length{};
};

// The original .bin pass is the source-local adjacency oracle. The bounded
// payload stays distinct from a full-graph or native Wikibase completeness
// certificate; a high-degree node explicitly reports truncation.
static constexpr size_t kMaxNeighborsPerNodeDirection = 200000;

struct NodeRoute {
    std::set<uint32_t> left;
    std::set<uint32_t> right;
    std::set<uint32_t> name_of_node;
    std::set<uint64_t> left_adjacency;
    std::set<uint64_t> right_adjacency;
    uint64_t left_values_seen{0};
    uint64_t right_values_seen{0};
    bool left_truncated{false};
    bool right_truncated{false};
};

static std::string json_escape(std::string_view value) {
    std::string out;
    out.reserve(value.size() + 8);
    for (unsigned char ch : value) {
        switch (ch) {
            case '"': out += "\\\""; break;
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

static Args parse_args(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto take = [&](const char* name) -> std::string {
            if (i + 1 >= argc) throw std::runtime_error(std::string("missing value for ") + name);
            return argv[++i];
        };
        if (arg == "--bin") args.bin = take("--bin");
        else if (arg == "--output") args.output = take("--output");
        else if (arg == "--lang") args.lang = take("--lang");
        else if (arg == "--qid") args.qids.insert(take("--qid"));
        else if (arg == "--node") {
            const std::string value = take("--node");
            if (value.empty()) throw std::runtime_error("empty numeric node ID");
            for (unsigned char ch : value) {
                if (!std::isdigit(ch)) throw std::runtime_error("nondecimal numeric frontier ID");
            }
            size_t used = 0;
            const auto parsed = std::stoull(value, &used, 10);
            if (used != value.size()) throw std::runtime_error("invalid numeric frontier ID");
            if (!args.extra_numeric_nodes.insert(parsed).second)
                throw std::runtime_error("duplicate extra numeric frontier ID");
        }
        else throw std::runtime_error("unknown argument: " + arg);
    }
    if (args.bin.empty() || args.output.empty()) throw std::runtime_error("--bin and --output are required");
    if (args.qids.empty()) throw std::runtime_error("at least one --qid is required");
    return args;
}

static Header read_header(CountingBufferedInputStream& counting, const capnp::ReaderOptions& options) {
    const uint64_t before = counting.bytesRead();
    capnp::PackedMessageReader main_message(counting, options);
    const auto impl = main_message.getRoot<zelph::network::ZelphImpl>();
    Header h;
    h.left = impl.getLeftChunkCount();
    h.right = impl.getRightChunkCount();
    h.name_of_node = impl.getNameOfNodeChunkCount();
    h.node_of_name = impl.getNodeOfNameChunkCount();
    h.header_length = counting.bytesRead() - before;
    return h;
}

template <typename Root>
static void discard_messages(CountingBufferedInputStream& counting, const capnp::ReaderOptions& options, uint32_t count) {
    for (uint32_t i = 0; i < count; ++i) {
        capnp::PackedMessageReader message(counting, options);
        (void)message.getRoot<Root>();
    }
}

static std::map<std::string, uint64_t> resolve_qids(
    const Args& args,
    const capnp::ReaderOptions& options,
    Header& header,
    std::map<std::string, uint32_t>& qid_node_of_name_chunk
) {
    FILE* file = std::fopen(args.bin.c_str(), "rb");
    if (!file) throw std::runtime_error("failed to open source bin");
    try {
        kj::FdInputStream raw(fileno(file));
        CountingBufferedInputStream counting(raw);
        header = read_header(counting, options);
        discard_messages<zelph::network::AdjChunk>(counting, options, header.left);
        discard_messages<zelph::network::AdjChunk>(counting, options, header.right);
        discard_messages<zelph::network::NameChunk>(counting, options, header.name_of_node);

        std::map<std::string, uint64_t> resolved;
        for (uint32_t i = 0; i < header.node_of_name; ++i) {
            capnp::PackedMessageReader message(counting, options);
            const auto chunk = message.getRoot<zelph::network::NodeNameChunk>();
            if (std::string(chunk.getLang().cStr()) != args.lang) continue;
            for (auto pair : chunk.getPairs()) {
                const std::string key = pair.getKey().cStr();
                if (args.qids.count(key) != 0) {
                    const uint64_t node = pair.getValue();
                    const auto existing = resolved.find(key);
                    if (existing != resolved.end()) {
                        // A graph may have repeated name rows.  A repeated
                        // key in *another physical chunk* cannot silently
                        // overwrite the shard identity even when its nodeId
                        // happens to be the same.  The single-shard/v1 route
                        // cannot represent that collision fibre, so abstain.
                        const auto first_chunk = qid_node_of_name_chunk.at(key);
                        if (existing->second != node || first_chunk != chunk.getChunkIndex()) {
                            throw std::runtime_error(
                                "QID has ambiguous node/chunk witnesses: " + key);
                        }
                        continue; // exact duplicate within the same chunk
                    }
                    resolved.emplace(key, node);
                    qid_node_of_name_chunk.emplace(key, chunk.getChunkIndex());
                }
            }
        }
        std::fclose(file);
        return resolved;
    } catch (...) {
        std::fclose(file);
        throw;
    }
}

static std::map<uint64_t, NodeRoute> resolve_routes(
    const Args& args,
    const capnp::ReaderOptions& options,
    const std::set<uint64_t>& target_nodes,
    Header& second_header
) {
    FILE* file = std::fopen(args.bin.c_str(), "rb");
    if (!file) throw std::runtime_error("failed to reopen source bin");
    try {
        kj::FdInputStream raw(fileno(file));
        CountingBufferedInputStream counting(raw);
        second_header = read_header(counting, options);
        std::map<uint64_t, NodeRoute> routes;
        for (uint64_t node : target_nodes) routes[node] = NodeRoute{};

        auto scan_adj = [&](uint32_t count, bool left) {
            for (uint32_t i = 0; i < count; ++i) {
                capnp::PackedMessageReader message(counting, options);
                const auto chunk = message.getRoot<zelph::network::AdjChunk>();
                if (std::string(chunk.getWhich().cStr()) != (left ? "left" : "right")) {
                    throw std::runtime_error("adjacency chunk direction mismatches source section");
                }
                for (auto pair : chunk.getPairs()) {
                    const uint64_t node = pair.getNode();
                    if (target_nodes.count(node) == 0) continue;
                    NodeRoute& route = routes.at(node);
                    if (left) route.left.insert(chunk.getChunkIndex());
                    else route.right.insert(chunk.getChunkIndex());
                    auto& neighbors = left ? route.left_adjacency : route.right_adjacency;
                    auto& values_seen = left ? route.left_values_seen : route.right_values_seen;
                    auto& truncated = left ? route.left_truncated : route.right_truncated;
                    for (uint64_t adjacent : pair.getAdj()) {
                        ++values_seen;
                        if (neighbors.size() < kMaxNeighborsPerNodeDirection ||
                            neighbors.count(adjacent) != 0) {
                            neighbors.insert(adjacent);
                        } else {
                            truncated = true;
                        }
                    }
                }
            }
        };
        scan_adj(second_header.left, true);
        scan_adj(second_header.right, false);

        for (uint32_t i = 0; i < second_header.name_of_node; ++i) {
            capnp::PackedMessageReader message(counting, options);
            const auto chunk = message.getRoot<zelph::network::NameChunk>();
            if (std::string(chunk.getLang().cStr()) != args.lang) continue;
            for (auto pair : chunk.getPairs()) {
                const uint64_t node = pair.getKey();
                if (target_nodes.count(node) != 0) routes[node].name_of_node.insert(chunk.getChunkIndex());
            }
        }

        std::fclose(file);
        return routes;
    } catch (...) {
        std::fclose(file);
        throw;
    }
}

template <typename Integer>
static void write_set(std::ostream& out, const std::set<Integer>& values) {
    out << "[";
    bool first = true;
    for (Integer value : values) {
        if (!first) out << ",";
        first = false;
        out << value;
    }
    out << "]";
}

int main(int argc, char** argv) {
    try {
        const Args args = parse_args(argc, argv);
        capnp::ReaderOptions options;
        options.traversalLimitInWords = 1ull << 32;
        options.nestingLimit = 128;

        Header first_header;
        std::map<std::string, uint32_t> node_of_name_chunks;
        const auto qid_to_node = resolve_qids(args, options, first_header, node_of_name_chunks);
        std::set<uint64_t> target_nodes;
        for (const auto& entry : qid_to_node) target_nodes.insert(entry.second);
        target_nodes.insert(args.extra_numeric_nodes.begin(), args.extra_numeric_nodes.end());

        Header second_header;
        const auto routes = resolve_routes(args, options, target_nodes, second_header);
        if (first_header.left != second_header.left || first_header.right != second_header.right ||
            first_header.name_of_node != second_header.name_of_node || first_header.node_of_name != second_header.node_of_name) {
            throw std::runtime_error("source header changed between filtered-route passes");
        }

        const auto parent = args.output.parent_path();
        if (!parent.empty()) std::filesystem::create_directories(parent);
        std::ofstream out(args.output);
        if (!out) throw std::runtime_error("failed to open output");

        out << "{\n";
        out << "  \"routeVersion\": \"zelph-filtered-route/v1\",\n";
        out << "  \"source\": {\"binPath\": \"" << json_escape(args.bin.string()) << "\",\"binSizeBytes\":"
            << std::filesystem::file_size(args.bin) << ",\"headerLengthBytes\":" << first_header.header_length
            << ",\"leftChunkCount\":" << first_header.left << ",\"rightChunkCount\":" << first_header.right
            << ",\"nameOfNodeChunkCount\":" << first_header.name_of_node << ",\"nodeOfNameChunkCount\":" << first_header.node_of_name << "},\n";
        out << "  \"language\": \"" << json_escape(args.lang) << "\",\n";
        out << "  \"requestedQids\": [";
        bool first = true;
        for (const auto& qid : args.qids) { if (!first) out << ","; first = false; out << "\"" << json_escape(qid) << "\""; }
        out << "],\n";
        out << "  \"additionalNumericNodes\": ";
        write_set(out, args.extra_numeric_nodes);
        out << ",\n";
        out << "  \"qidToZelphNodeIds\": {";
        first = true;
        for (const auto& qid : args.qids) {
            if (!first) out << ","; first = false;
            out << "\"" << json_escape(qid) << "\":";
            const auto it = qid_to_node.find(qid);
            if (it == qid_to_node.end()) out << "null"; else out << it->second;
        }
        out << "},\n";
        out << "  \"qidToNodeOfNameChunks\": {";
        first = true;
        for (const auto& qid : args.qids) {
            if (!first) out << ","; first = false;
            out << "\"" << json_escape(qid) << "\":";
            const auto it = node_of_name_chunks.find(qid);
            if (it == node_of_name_chunks.end()) out << "null"; else out << it->second;
        }
        out << "},\n";
        out << "  \"nodeRoutes\": {";
        first = true;
        for (const auto& entry : routes) {
            if (!first) out << ","; first = false;
            out << "\"" << entry.first << "\":{\"left\":"; write_set(out, entry.second.left);
            out << ",\"right\":"; write_set(out, entry.second.right);
            out << ",\"nameOfNode\":"; write_set(out, entry.second.name_of_node); out << "}";
        }
        out << "},\n";
        // Original .bin source-local adjacency, not a published HF chunk
        // replay. Each node/direction has a bounded and reported capture.
        out << "  \"nodeAdjacency\": {";
        first = true;
        for (const auto& entry : routes) {
            if (!first) out << ","; first = false;
            const NodeRoute& route = entry.second;
            out << "\"" << entry.first << "\":{\"left\":";
            write_set(out, route.left_adjacency);
            out << ",\"right\":";
            write_set(out, route.right_adjacency);
            out << ",\"leftValuesSeen\":" << route.left_values_seen;
            out << ",\"rightValuesSeen\":" << route.right_values_seen;
            out << ",\"leftTruncated\":" << (route.left_truncated ? "true" : "false");
            out << ",\"rightTruncated\":" << (route.right_truncated ? "true" : "false");
            out << "}";
        }
        out << "},\n";
        out << "  \"adjacencyOracleScope\": \"bounded-selected-roots-in-source-bin\",\n";
        out << "  \"sourceBinToPublishedHfDatasetIdentityVerified\": false,\n";
        out << "  \"resolvedQidCount\": " << qid_to_node.size() << ",\n";
        out << "  \"completeQidResolution\": " << (qid_to_node.size() == args.qids.size() ? "true" : "false") << ",\n";
        out << "  \"fullRouteMaterializationPerformed\": false\n";
        out << "}\n";
        return qid_to_node.size() == args.qids.size() ? 0 : 2;
    } catch (const std::exception& exc) {
        std::cerr << "zelph_bin_filtered_route_builder: " << exc.what() << "\n";
        return 1;
    }
}
