// Rebucket a Zelph .bin artifact into fixed-size query-oriented buckets.
//
// Build:
//   g++ -std=c++17 -O2 \
//     -I aur/zelph/build-local/src/lib/io \
//     tools/zelph_bin_v3_bucket_builder.cpp \
//     aur/zelph/build-local/src/lib/io/zelph.capnp.c++ \
//     -lcapnp -lkj -o tools/zelph_bin_v3_bucket_builder

#include <capnp/message.h>
#include <capnp/serialize-packed.h>
#include <kj/io.h>

#include <cassert>
#include <cerrno>
#include <cctype>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <map>
#include <sstream>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

#include <zelph/zelph.capnp.h>

class CountingBufferedInputStream : public kj::BufferedInputStream {
public:
    explicit CountingBufferedInputStream(kj::InputStream& inner)
        : buffered(inner)
    {
    }

    kj::ArrayPtr<const kj::byte> tryGetReadBuffer() override
    {
        return buffered.tryGetReadBuffer();
    }

    size_t tryRead(void* buffer, size_t minBytes, size_t maxBytes) override
    {
        const size_t n = buffered.tryRead(buffer, minBytes, maxBytes);
        count += n;
        return n;
    }

    void skip(size_t bytes) override
    {
        buffered.skip(bytes);
        count += bytes;
    }

    uint64_t bytesRead() const
    {
        return count;
    }

private:
    kj::BufferedInputStreamWrapper buffered;
    uint64_t                      count{0};
};

struct Args {
    std::string bin_path;
    std::string out_root;
    std::string tmp_root;
    uint64_t    left_buckets = 512;
    uint64_t    right_buckets = 512;
    uint64_t    name_buckets = 128;
};

struct BucketChunk {
    uint32_t    chunk_index{};
    uint64_t    length{};
    std::string lang;
};

struct SectionSummary {
    std::vector<BucketChunk> entries;
};

struct HeaderStats {
    uint32_t left_chunk_count{};
    uint32_t right_chunk_count{};
    uint32_t name_of_node_count{};
    uint32_t node_of_name_count{};
    uint64_t header_length_bytes{};
};

static void usage(const char* argv0)
{
    std::cerr << "Usage: " << argv0 << " --bin <source.bin> --out-root <directory> [options]\n"
              << "  --left-buckets <n>       number of buckets for left (default 512)\n"
              << "  --right-buckets <n>      number of buckets for right (default 512)\n"
              << "  --name-buckets <n>       number of buckets for name sections (default 128)\n";
}

static uint64_t parse_u64_arg(const std::string& value)
{
    try
    {
        return std::stoull(value);
    }
    catch (...) {
        throw std::runtime_error("Invalid numeric argument: " + value);
    }
}

static Args parse_args(int argc, char** argv)
{
    Args args;
    for (int i = 1; i < argc; ++i)
    {
        std::string_view arg = argv[i];
        auto take = [&](const char* name) {
            if (i + 1 >= argc)
            {
                throw std::runtime_error(std::string("Missing value for ") + name);
            }
            return std::string(argv[++i]);
        };

        if (arg == "--bin")
        {
            args.bin_path = take("--bin");
        }
        else if (arg == "--out-root")
        {
            args.out_root = take("--out-root");
        }
        else if (arg == "--tmp-root")
        {
            args.tmp_root = take("--tmp-root");
        }
        else if (arg == "--left-buckets")
        {
            args.left_buckets = parse_u64_arg(take("--left-buckets"));
        }
        else if (arg == "--right-buckets")
        {
            args.right_buckets = parse_u64_arg(take("--right-buckets"));
        }
        else if (arg == "--name-buckets")
        {
            args.name_buckets = parse_u64_arg(take("--name-buckets"));
        }
        else
        {
            throw std::runtime_error("Unknown argument: " + std::string(arg));
        }
    }

    if (args.bin_path.empty() || args.out_root.empty())
    {
        throw std::runtime_error("--bin and --out-root are required");
    }
    if (args.left_buckets == 0 || args.right_buckets == 0 || args.name_buckets == 0)
    {
        throw std::runtime_error("Bucket counts must be > 0");
    }
    if (args.tmp_root.empty())
    {
        args.tmp_root = args.out_root + "/.tmp-v3-buckets";
    }

    return args;
}

static uint64_t fnv1a64(std::string_view value)
{
    uint64_t hash = 14695981039346656037ULL;
    for (unsigned char byte : value)
    {
        hash ^= byte;
        hash *= 1099511628211ULL;
    }
    return hash;
}

static std::string sanitize_lang(const std::string& input)
{
    std::string out;
    out.reserve(input.size());
    for (char ch : input)
    {
        out += (std::isalnum(static_cast<unsigned char>(ch)) || ch == '-' || ch == '_' || ch == '.') ? ch : '_';
    }
    return out.empty() ? "lang" : out;
}

static std::string chunk_filename(uint32_t chunk_index, const std::string& lang = "")
{
    std::ostringstream out;
    out << "chunk-" << std::setw(6) << std::setfill('0') << chunk_index;
    if (!lang.empty())
    {
        out << "-" << sanitize_lang(lang);
    }
    out << ".capnp-packed";
    return out.str();
}

static std::string bucket_filename(uint32_t bucket_index)
{
    std::ostringstream out;
    out << "bucket-" << std::setw(6) << std::setfill('0') << bucket_index << ".bin";
    return out.str();
}

static std::string json_escape(std::string_view value)
{
    std::string out;
    out.reserve(value.size() + 8);
    for (unsigned char ch : value)
    {
        switch (ch)
        {
        case '"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (ch < 0x20)
            {
                char buf[7];
                std::snprintf(buf, sizeof(buf), "\\u%04x", ch);
                out += buf;
            }
            else
            {
                out += static_cast<char>(ch);
            }
        }
    }
    return out;
}

static void write_u32(std::ofstream& out, uint32_t value)
{
    out.write(reinterpret_cast<const char*>(&value), sizeof(uint32_t));
}

static void write_u64(std::ofstream& out, uint64_t value)
{
    out.write(reinterpret_cast<const char*>(&value), sizeof(uint64_t));
}

static bool read_u32(std::ifstream& in, uint32_t& value)
{
    in.read(reinterpret_cast<char*>(&value), sizeof(value));
    return static_cast<bool>(in);
}

static bool read_u64(std::ifstream& in, uint64_t& value)
{
    in.read(reinterpret_cast<char*>(&value), sizeof(value));
    return static_cast<bool>(in);
}

template <typename AdjReader>
static void append_adj_record(const std::filesystem::path& path, uint64_t node, const AdjReader& adj)
{
    std::ofstream out(path, std::ios::binary | std::ios::app);
    if (!out)
    {
        throw std::runtime_error("Failed to open temp adjacency bucket file: " + path.string());
    }
    write_u64(out, node);
    write_u32(out, static_cast<uint32_t>(adj.size()));
    for (uint64_t value : adj)
    {
        write_u64(out, value);
    }
}

static void append_nameofnode_record(const std::filesystem::path& path, uint64_t node, std::string_view value)
{
    std::ofstream out(path, std::ios::binary | std::ios::app);
    if (!out)
    {
        throw std::runtime_error("Failed to open temp nameOfNode bucket file: " + path.string());
    }
    write_u64(out, node);
    write_u32(out, static_cast<uint32_t>(value.size()));
    out.write(value.data(), static_cast<std::streamsize>(value.size()));
}

static void append_nodeofname_record(const std::filesystem::path& path, std::string_view name, uint64_t node)
{
    std::ofstream out(path, std::ios::binary | std::ios::app);
    if (!out)
    {
        throw std::runtime_error("Failed to open temp nodeOfName bucket file: " + path.string());
    }
    write_u32(out, static_cast<uint32_t>(name.size()));
    out.write(name.data(), static_cast<std::streamsize>(name.size()));
    write_u64(out, node);
}

static void remove_file_if_exists(const std::filesystem::path& path)
{
    if (std::filesystem::exists(path))
    {
        std::error_code ec;
        std::filesystem::remove(path, ec);
    }
}

static bool is_empty_file(const std::filesystem::path& path)
{
    return std::filesystem::exists(path) && std::filesystem::is_regular_file(path) && std::filesystem::file_size(path) == 0;
}

static SectionSummary emit_adj_section(const std::string& which,
                                     uint32_t     section_count,
                                     uint64_t     bucket_count,
                                     const capnp::ReaderOptions& options,
                                     uint64_t& bucket_cursor,
                                     CountingBufferedInputStream& counting,
                                     const std::filesystem::path& tmp_root,
                                     const std::filesystem::path& shard_root)
{
    std::filesystem::create_directories(tmp_root);
    std::vector<uint64_t> bucket_counts(bucket_count, 0);

    for (uint32_t i = 0; i < section_count; ++i)
    {
        capnp::PackedMessageReader chunk_message(counting, options);
        auto                         chunk = chunk_message.getRoot<zelph::network::AdjChunk>();
        const auto                   pairs = chunk.getPairs();

        for (auto pair : pairs)
        {
            const uint64_t node   = pair.getNode();
            const uint32_t bucket = static_cast<uint32_t>(node % bucket_count);
            const auto     bucket_file = tmp_root / bucket_filename(bucket);
            append_adj_record(bucket_file, node, pair.getAdj());
            ++bucket_counts[bucket];
        }
    }

    const auto section_dir = shard_root / which;
    std::filesystem::create_directories(section_dir);

    SectionSummary summary;
    for (uint32_t bucket = 0; bucket < bucket_count; ++bucket)
    {
        const auto bucket_path = tmp_root / bucket_filename(bucket);
        if (!std::filesystem::exists(bucket_path))
        {
            continue;
        }
        if (is_empty_file(bucket_path) || bucket_counts[bucket] == 0)
        {
            remove_file_if_exists(bucket_path);
            continue;
        }

        std::ifstream in(bucket_path, std::ios::binary);
        if (!in)
        {
            throw std::runtime_error("Failed to reopen temp bucket file: " + bucket_path.string());
        }

        const uint32_t chunk_index = static_cast<uint32_t>(bucket_cursor++);
        capnp::MallocMessageBuilder message;
        auto                    root = message.initRoot<zelph::network::AdjChunk>();
        root.setWhich(which);
        root.setChunkIndex(chunk_index);
        auto pairs = root.initPairs(bucket_counts[bucket]);

        for (uint32_t pair_idx = 0; pair_idx < bucket_counts[bucket]; ++pair_idx)
        {
            uint64_t node = 0;
            uint32_t adj_count = 0;
            if (!read_u64(in, node) || !read_u32(in, adj_count))
            {
                throw std::runtime_error("Malformed temporary adj bucket file: " + bucket_path.string());
            }

            auto pair = pairs[pair_idx];
            pair.setNode(node);
            auto adj = pair.initAdj(adj_count);
            for (uint32_t j = 0; j < adj_count; ++j)
            {
                uint64_t node_value = 0;
                if (!read_u64(in, node_value))
                {
                    throw std::runtime_error("Malformed temporary adj bucket file: " + bucket_path.string());
                }
                adj.set(j, node_value);
            }
        }
            if (!in || in.peek() != std::char_traits<char>::eof())
            {
                throw std::runtime_error("Malformed temporary adj bucket file (trailing bytes): " + bucket_path.string());
            }

        const auto out_file = section_dir / chunk_filename(chunk_index);
        const int fd = ::open(out_file.c_str(), O_CREAT | O_TRUNC | O_WRONLY, 0644);
        if (fd < 0)
        {
            throw std::runtime_error("Failed to open output shard file: " + out_file.string());
        }
        capnp::writePackedMessageToFd(fd, message);
        ::close(fd);

        summary.entries.push_back({chunk_index, static_cast<uint64_t>(std::filesystem::file_size(out_file)), ""});
        remove_file_if_exists(bucket_path);
    }

    return summary;
}

static SectionSummary emit_lang_name_section(const std::string& which,
                                           uint32_t        section_count,
                                           bool            is_node_of_name,
                                           uint64_t        bucket_count,
                                           const capnp::ReaderOptions& options,
                                           uint64_t&                  bucket_cursor,
                                           CountingBufferedInputStream& counting,
                                           const std::filesystem::path& tmp_root,
                                           const std::filesystem::path& shard_root)
{
    std::map<std::string, std::vector<uint64_t>> lang_counts;
    std::filesystem::create_directories(tmp_root);

    for (uint32_t i = 0; i < section_count; ++i)
    {
        if (is_node_of_name)
        {
            capnp::PackedMessageReader chunk_message(counting, options);
            auto                         chunk = chunk_message.getRoot<zelph::network::NodeNameChunk>();
            const std::string            lang = std::string(chunk.getLang().cStr());
            auto                         pairs = chunk.getPairs();
            auto&                        counts = lang_counts.try_emplace(lang, std::vector<uint64_t>(bucket_count, 0)).first->second;

            const auto lang_dir = tmp_root / sanitize_lang(lang);
            std::filesystem::create_directories(lang_dir);
            for (auto pair : pairs)
            {
                const std::string name = pair.getKey().cStr();
                const uint32_t    bucket = static_cast<uint32_t>(fnv1a64(name) % bucket_count);
                append_nodeofname_record(lang_dir / bucket_filename(bucket), name, pair.getValue());
                ++counts[bucket];
            }
        }
        else
        {
            capnp::PackedMessageReader chunk_message(counting, options);
            auto                         chunk = chunk_message.getRoot<zelph::network::NameChunk>();
            const std::string            lang = std::string(chunk.getLang().cStr());
            auto                         pairs = chunk.getPairs();
            auto&                        counts = lang_counts.try_emplace(lang, std::vector<uint64_t>(bucket_count, 0)).first->second;

            const auto lang_dir = tmp_root / sanitize_lang(lang);
            std::filesystem::create_directories(lang_dir);
            for (auto pair : pairs)
            {
                const uint64_t node = pair.getKey();
                const uint32_t bucket = static_cast<uint32_t>(node % bucket_count);
                append_nameofnode_record(lang_dir / bucket_filename(bucket), node, pair.getValue().cStr());
                ++counts[bucket];
            }
        }
    }

    const auto section_dir = shard_root / which;
    std::filesystem::create_directories(section_dir);

    SectionSummary summary;
    for (const auto& [lang, counts] : lang_counts)
    {
        const auto lang_dir = tmp_root / sanitize_lang(lang);
        for (uint32_t bucket = 0; bucket < bucket_count; ++bucket)
        {
            const auto tmp_bucket = lang_dir / bucket_filename(bucket);
            if (!std::filesystem::exists(tmp_bucket))
            {
                continue;
            }
            if (is_empty_file(tmp_bucket) || counts[bucket] == 0)
            {
                remove_file_if_exists(tmp_bucket);
                continue;
            }

            std::ifstream in(tmp_bucket, std::ios::binary);
            if (!in)
            {
                throw std::runtime_error("Failed to reopen temp lang bucket file: " + tmp_bucket.string());
            }

            const uint32_t chunk_index = static_cast<uint32_t>(bucket_cursor++);
            capnp::MallocMessageBuilder message;

            if (is_node_of_name)
            {
                auto chunk = message.initRoot<zelph::network::NodeNameChunk>();
                chunk.setLang(lang);
                chunk.setChunkIndex(chunk_index);
                auto pairs = chunk.initPairs(counts[bucket]);

                for (uint32_t pair_idx = 0; pair_idx < counts[bucket]; ++pair_idx)
                {
                    uint32_t  name_length = 0;
                    if (!read_u32(in, name_length))
                    {
                        throw std::runtime_error("Malformed temporary nodeOfName bucket file: " + tmp_bucket.string());
                    }
                    std::string name(name_length, '\0');
                    in.read(name.data(), static_cast<std::streamsize>(name_length));
                    if (!in)
                    {
                        throw std::runtime_error("Malformed temporary nodeOfName bucket file: " + tmp_bucket.string());
                    }
                    uint64_t node = 0;
                    if (!read_u64(in, node))
                    {
                        throw std::runtime_error("Malformed temporary nodeOfName bucket file: " + tmp_bucket.string());
                    }

                    auto pair = pairs[pair_idx];
                    pair.setKey(name);
                    pair.setValue(node);
                }
            }
            else
            {
                auto chunk = message.initRoot<zelph::network::NameChunk>();
                chunk.setLang(lang);
                chunk.setChunkIndex(chunk_index);
                auto pairs = chunk.initPairs(counts[bucket]);

                for (uint32_t pair_idx = 0; pair_idx < counts[bucket]; ++pair_idx)
                {
                    uint64_t node = 0;
                    uint32_t value_length = 0;
                    if (!read_u64(in, node) || !read_u32(in, value_length))
                    {
                        throw std::runtime_error("Malformed temporary nameOfNode bucket file: " + tmp_bucket.string());
                    }
                    std::string value(value_length, '\0');
                    in.read(value.data(), static_cast<std::streamsize>(value_length));
                    if (!in)
                    {
                        throw std::runtime_error("Malformed temporary nameOfNode bucket file: " + tmp_bucket.string());
                    }

                    auto pair = pairs[pair_idx];
                    pair.setKey(node);
                    pair.setValue(value);
                }
            }

            const auto out_file = section_dir / chunk_filename(chunk_index, lang);
            const int fd = ::open(out_file.c_str(), O_CREAT | O_TRUNC | O_WRONLY, 0644);
            if (fd < 0)
            {
                throw std::runtime_error("Failed to open output shard file: " + out_file.string());
            }
            capnp::writePackedMessageToFd(fd, message);
            ::close(fd);

            summary.entries.push_back({chunk_index, static_cast<uint64_t>(std::filesystem::file_size(out_file)), lang});
            remove_file_if_exists(tmp_bucket);
        }
    }

    return summary;
}

static void write_json_section(std::ofstream& out,
                              const char* section_name,
                              const SectionSummary& summary,
                              bool is_last)
{
    out << "  \"" << section_name << "\":[\n";
    for (size_t i = 0; i < summary.entries.size(); ++i)
    {
        const auto& entry = summary.entries[i];
        if (i)
        {
            out << ",\n";
        }
        out << "  {\"chunkIndex\":" << entry.chunk_index << ",\"offset\":0,\"length\":" << entry.length;
        if (!entry.lang.empty())
        {
            out << ",\"lang\":" << '"' << json_escape(entry.lang) << '"';
        }
        out << "}";
    }
    out << "]";
    if (!is_last)
    {
        out << ",\n";
    }
}

static void write_json_index(const std::filesystem::path& output,
                            const std::filesystem::path& source_bin,
                            uint64_t                      header_length,
                            const SectionSummary& left,
                            const SectionSummary& right,
                            const SectionSummary& name_of_node,
                            const SectionSummary& node_of_name)
{
    std::ofstream out(output);
    if (!out)
    {
        throw std::runtime_error("Failed to write index JSON: " + output.string());
    }

    out << "{\n";
    out << "  \"file\":\"" << json_escape(source_bin.string()) << "\",";
    out << "\n  \"header\":{\"offset\":0,\"length\":" << header_length << "},\n";

    write_json_section(out, "left", left, false);
    write_json_section(out, "right", right, false);
    write_json_section(out, "nameOfNode", name_of_node, false);
    write_json_section(out, "nodeOfName", node_of_name, true);
    out << "\n}\n";
}

static void write_v3_route(const std::filesystem::path& output,
                          const std::filesystem::path& source_bin,
                          uint64_t                      source_size,
                          const HeaderStats&            header,
                          const SectionSummary&         left,
                          const SectionSummary&         right,
                          const SectionSummary&         name_of_node,
                          const SectionSummary&         node_of_name,
                          const std::filesystem::path&  shard_root)
{
    std::ofstream out(output);
    if (!out)
    {
        throw std::runtime_error("Failed to write route JSON: " + output.string());
    }

    out << "{\n";
    out << "  \"routeVersion\": \"zelph-node-route/v1\",\n";
    out << "  \"source\": {\"binPath\": \"" << json_escape(source_bin.string()) << "\",\"binSizeBytes\":" << source_size
        << ",\"headerLengthBytes\":" << header.header_length_bytes << ",\"leftChunkCount\":" << header.left_chunk_count
        << ",\"rightChunkCount\":" << header.right_chunk_count << ",\"nameOfNodeChunkCount\":" << header.name_of_node_count
        << ",\"nodeOfNameChunkCount\":" << header.node_of_name_count << "},\n";
    out << "  \"routing\": {\n";

    bool first = true;
    auto write_section = [&](const char* section_name, const SectionSummary& section) {
        if (!first)
        {
            out << ",\n";
        }
        first = false;
        out << "    \"" << section_name << "\": [\n";

        for (size_t i = 0; i < section.entries.size(); ++i)
        {
            const auto& entry = section.entries[i];
            if (i)
            {
                out << ",\n";
            }

            const bool is_left = std::string(section_name) == "left";
            const bool is_right = std::string(section_name) == "right";
            const bool is_name_of_node = std::string(section_name) == "nameOfNode";
            const std::filesystem::path chunk_path = shard_root / section_name / chunk_filename(entry.chunk_index, entry.lang);
            FILE* file = std::fopen(chunk_path.c_str(), "rb");
            if (!file)
            {
                throw std::runtime_error("Cannot open rebucketed chunk for route generation: " + chunk_path.string());
            }

            try
            {
                kj::FdInputStream             raw(fileno(file));
                kj::BufferedInputStreamWrapper buffered(raw);
                capnp::ReaderOptions           route_options;
                route_options.traversalLimitInWords = 1ULL << 32;
                route_options.nestingLimit = 128;
                capnp::PackedMessageReader chunk_message(buffered, route_options);

                if (is_left || is_right)
                {
                    auto chunk = chunk_message.getRoot<zelph::network::AdjChunk>();
                    auto pairs = chunk.getPairs();
                    out << "      {\"chunkIndex\":" << entry.chunk_index << ",\"which\":\"" << section_name
                        << "\",\"entryCount\":" << pairs.size() << ",\"nodes\":[";
                    size_t idx = 0;
                    for (auto pair : pairs)
                    {
                        if (idx++) out << ',';
                        out << pair.getNode();
                    }
                    out << "]}";
                }
                else if (is_name_of_node)
                {
                    auto chunk = chunk_message.getRoot<zelph::network::NameChunk>();
                    auto pairs = chunk.getPairs();
                    out << "      {\"chunkIndex\":" << entry.chunk_index << ",\"lang\":\"" << json_escape(entry.lang)
                        << "\",\"entryCount\":" << pairs.size() << ",\"nodes\":[";
                    size_t idx = 0;
                    for (auto pair : pairs)
                    {
                        if (idx++) out << ',';
                        out << pair.getKey();
                    }
                    out << "]}";
                }
                else
                {
                    auto chunk = chunk_message.getRoot<zelph::network::NodeNameChunk>();
                    auto pairs = chunk.getPairs();
                    out << "      {\"chunkIndex\":" << entry.chunk_index << ",\"lang\":\"" << json_escape(entry.lang)
                        << "\",\"entryCount\":" << pairs.size() << ",\"names\":[";
                    size_t idx = 0;
                    for (auto pair : pairs)
                    {
                        if (idx++) out << ',';
                        out << '\"' << json_escape(pair.getKey().cStr()) << '\"';
                    }
                    out << "]}";
                }
            }
            catch (...)
            {
                std::fclose(file);
                throw;
            }
            std::fclose(file);
        }
        out << "\n    ]";
    };

    write_section("left", left);
    write_section("right", right);
    write_section("nameOfNode", name_of_node);
    write_section("nodeOfName", node_of_name);
    out << "\n  }\n}\n";
}

static void cleanup(const std::filesystem::path& tmp_root)
{
    std::error_code ec;
    std::filesystem::remove_all(tmp_root, ec);
}

static void reset_tmp_root(const std::filesystem::path& tmp_root)
{
    std::error_code ec;
    std::filesystem::remove_all(tmp_root, ec);
    std::filesystem::create_directories(tmp_root, ec);
    if (ec)
    {
        throw std::runtime_error("Failed to initialize temp bucket root: " + tmp_root.string());
    }
}

int main(int argc, char** argv)
{
    try
    {
        const Args args = parse_args(argc, argv);

        const std::filesystem::path bin_path = std::filesystem::path(args.bin_path);
        const std::filesystem::path out_root = std::filesystem::path(args.out_root);
        const std::filesystem::path tmp_root = std::filesystem::path(args.tmp_root);

        if (!std::filesystem::exists(bin_path))
        {
            throw std::runtime_error("Input bin file not found: " + args.bin_path);
        }

        std::filesystem::create_directories(out_root / "shards");
        reset_tmp_root(tmp_root);

        FILE* file = fopen(bin_path.c_str(), "rb");
        if (!file)
        {
            throw std::runtime_error("Failed to open input bin: " + args.bin_path);
        }

        kj::FdInputStream           raw(fileno(file));
        CountingBufferedInputStream  counting(raw);
        capnp::ReaderOptions         options;
        options.traversalLimitInWords = 1ULL << 32;
        options.nestingLimit          = 128;

        const uint64_t headerOffset = counting.bytesRead();
        capnp::PackedMessageReader mainMessage(counting, options);
        auto impl = mainMessage.getRoot<zelph::network::ZelphImpl>();

        HeaderStats header{};
        header.header_length_bytes = counting.bytesRead() - headerOffset;
        header.left_chunk_count = impl.getLeftChunkCount();
        header.right_chunk_count = impl.getRightChunkCount();
        header.name_of_node_count = impl.getNameOfNodeChunkCount();
        header.node_of_name_count = impl.getNodeOfNameChunkCount();

        uint64_t left_bucket_cursor = 0;
        uint64_t right_bucket_cursor = 0;
        uint64_t name_bucket_cursor = 0;
        uint64_t node_of_name_bucket_cursor = 0;

        SectionSummary left = emit_adj_section("left",
                                             header.left_chunk_count,
                                             args.left_buckets,
                                             options,
                                             left_bucket_cursor,
                                             counting,
                                             tmp_root / "left",
                                             out_root / "shards");

        SectionSummary right = emit_adj_section("right",
                                              header.right_chunk_count,
                                              args.right_buckets,
                                              options,
                                              right_bucket_cursor,
                                              counting,
                                              tmp_root / "right",
                                              out_root / "shards");

        SectionSummary name_of_node = emit_lang_name_section("nameOfNode",
                                                            header.name_of_node_count,
                                                            false,
                                                            args.name_buckets,
                                                            options,
                                                            name_bucket_cursor,
                                                            counting,
                                                            tmp_root / "nameOfNode",
                                                            out_root / "shards");

        SectionSummary node_of_name = emit_lang_name_section("nodeOfName",
                                                            header.node_of_name_count,
                                                            true,
                                                            args.name_buckets,
                                                            options,
                                                            node_of_name_bucket_cursor,
                                                            counting,
                                                            tmp_root / "nodeOfName",
                                                            out_root / "shards");

        fclose(file);

        write_json_index(out_root / "artifact-v3.index.json",
                        bin_path,
                        header.header_length_bytes,
                        left,
                        right,
                        name_of_node,
                        node_of_name);

        write_v3_route(out_root / "artifact-v3.route.json",
                       bin_path,
                       std::filesystem::file_size(bin_path),
                       header,
                       left,
                       right,
                       name_of_node,
                       node_of_name,
                       out_root / "shards");

        cleanup(tmp_root);

        std::cout << "Built v3 bucketed artifact at: " << out_root.string() << "\n";
        std::cout << " left chunks: " << left.entries.size() << "\n";
        std::cout << " right chunks: " << right.entries.size() << "\n";
        std::cout << " nameOfNode chunks: " << name_of_node.entries.size() << "\n";
        std::cout << " nodeOfName chunks: " << node_of_name.entries.size() << "\n";
        std::cout << " index.json: " << (out_root / "artifact-v3.index.json").string() << "\n";
        std::cout << " route.json: " << (out_root / "artifact-v3.route.json").string() << "\n";
    }
    catch (const std::exception& ex)
    {
        std::cerr << ex.what() << "\n";
        return 1;
    }

    return 0;
}
