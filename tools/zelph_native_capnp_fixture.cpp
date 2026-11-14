// Original Zelph schema native fixture: four section-global packed messages.
// Used ONLY for offline decoder round-trip regression, not physical HF evidence.
// Build against the same generated upstream zelph.capnp as the decoder.
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
template <typename Callback>
void write_chunk(
    const std::filesystem::path& file, Callback make_chunk
) {
    capnp::MallocMessageBuilder message;
    make_chunk(message);
    FILE* fp = std::fopen(file.c_str(), "wb");
    if (!fp) throw std::runtime_error("failed to create native fixture: " + file.string());
    try {
        {
            kj::FdOutputStream output(fileno(fp));
            capnp::writePackedMessage(output, message);
        }
        if (std::fclose(fp) != 0) throw std::runtime_error("fixture write failed");
    } catch (...) {
        std::fclose(fp);
        throw;
    }
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: zelph_native_fixture <output-directory>");
        const std::filesystem::path root(argv[1]);
        std::filesystem::create_directories(root);

        write_chunk(root / "left.capnp-packed", [](capnp::MallocMessageBuilder& msg) {
            auto chunk = msg.initRoot<zelph::network::AdjChunk>();
            chunk.setWhich("left");
            chunk.setChunkIndex(0);
            auto pairs = chunk.initPairs(1);
            pairs[0].setNode(7);
            auto adj = pairs[0].initAdj(2);
            adj.set(0, 8);
            adj.set(1, 9);
        });
        write_chunk(root / "right.capnp-packed", [](capnp::MallocMessageBuilder& msg) {
            auto chunk = msg.initRoot<zelph::network::AdjChunk>();
            chunk.setWhich("right");
            chunk.setChunkIndex(0);
            auto pairs = chunk.initPairs(1);
            pairs[0].setNode(7);
            auto adj = pairs[0].initAdj(1);
            adj.set(0, 10);
        });
        write_chunk(root / "nameOfNode.capnp-packed", [](capnp::MallocMessageBuilder& msg) {
            auto chunk = msg.initRoot<zelph::network::NameChunk>();
            chunk.setLang("wikidata");
            chunk.setChunkIndex(0);
            auto pairs = chunk.initPairs(1);
            pairs[0].setKey(7);
            pairs[0].setValue("Q1");
        });
        write_chunk(root / "nodeOfName.capnp-packed", [](capnp::MallocMessageBuilder& msg) {
            auto chunk = msg.initRoot<zelph::network::NodeNameChunk>();
            chunk.setLang("wikidata");
            chunk.setChunkIndex(0);
            auto pairs = chunk.initPairs(1);
            pairs[0].setKey("Q1");
            pairs[0].setValue(7);
        });
        std::cout << "four original Zelph schema packed fixtures emitted\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "zelph_native_fixture: " << ex.what() << "\n";
        return 2;
    }
}
