"""Fail-closed conductor tests; mock only the existing physical functions."""
from hashlib import sha256
import json
from pathlib import Path
import stat
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import run_zelph_local_physical_maxcut as runner


REV = 'a' * 40


def setup(tmp_path, monkeypatch):
    source = tmp_path / 'original.bin'
    source.write_bytes(b'physical original bytes')
    manifest = tmp_path / 'manifest.json'
    # A full packed original consists of one header and all four section
    # messages. Mock only physical byte decoding, NOT the partition verifier.
    source_size = source.stat().st_size
    header_size = source_size - 4 * 5
    assert header_size > 0
    sections = {}
    offset = header_size
    artifact = 'wikidata-20260309-all'
    for section in ('left', 'right', 'nameOfNode', 'nodeOfName'):
        filename = ('chunk-000000.capnp-packed' if section in ('left', 'right')
                    else 'chunk-000000-wikidata.capnp-packed')
        entry = {
            'chunkIndex': 0, 'offset': offset, 'length': 5,
            'objectPath': f'hf://datasets/acrion/zelph/{artifact}/shards/{section}/{filename}',
        }
        entry['which' if section in ('left', 'right') else 'lang'] = (
            section if section in ('left', 'right') else 'wikidata'
        )
        sections[section] = {'chunks': [entry]}
        offset += 5
    manifest.write_text(json.dumps({
        'manifestVersion': 2,
        'storageMode': 'split-by-direction-and-section',
        'source': {'artifactName': artifact, 'binSizeBytes': source_size},
        'sections': sections,
    }, sort_keys=True))
    route_template = tmp_path / 'route-template.json'
    route_template.write_text(json.dumps({
        'routeVersion': 'zelph-filtered-route/v1',
        'source': {
            'headerLengthBytes': header_size, 'binSizeBytes': source_size,
            'leftChunkCount': 1, 'rightChunkCount': 1,
            'nameOfNodeChunkCount': 1, 'nodeOfNameChunkCount': 1,
        },
    }, sort_keys=True))
    shard = tmp_path / 'shards'
    shard.mkdir()
    producer = tmp_path / 'producer'
    producer.write_text(
        '#!/usr/bin/env python3\nimport pathlib,sys\n'
        'pathlib.Path(sys.argv[sys.argv.index("--output")+1]).write_bytes('
        'pathlib.Path(sys.argv[sys.argv.index("--bin")+1]).parent.joinpath('
        '"route-template.json").read_bytes())\n'
    )
    producer.chmod(producer.stat().st_mode | stat.S_IXUSR)
    decoder = tmp_path / 'decoder'
    decoder.touch()

    def verify(**kwargs):
        assert kwargs['source_bin'] == source
        assert kwargs['manifest_sha256'] == sha256(manifest.read_bytes()).hexdigest()
        assert kwargs['route_path'].is_file()
        return {
            'version': 'itir.zelph.exact_original_bin_selected_hf_ranges.v1',
            'physical_receipts': [],
        }

    def native(**kwargs):
        assert kwargs['source_bin'] == source
        assert kwargs['range_receipt_path'].is_file()
        return {
            'source_bin_range_equality_reverified_in_this_run': True,
            'selected_root_one_hop_bidirectional_adjacency_equal_original_bin': True,
            'selected_object_count': 4,
            'root_adjacency': [],
        }

    def closure(**kwargs):
        return {
            'all_declared_words_closed': False,
            'missing_boundaries': [
                {'node_id': 23, 'direction': 'right', 'required_for_queries': ['q1']}
            ],
        }

    monkeypatch.setattr(runner, 'verify_selected_source_ranges', verify)
    monkeypatch.setattr(runner, 'verify_native_selected_shard_answer', native)
    monkeypatch.setattr(runner, 'finite_relation_word_closure', closure)
    return dict(
        source_bin=source, manifest=manifest, shard_root=shard,
        producer=producer, decoder=decoder, output_dir=tmp_path / 'out',
        dataset_revision=REV, manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        qids=['Q1'], extra_nodes=[8],
    )


def test_same_run_route_bytes_native_and_scoped_boundary_outputs(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    family = tmp_path / 'family.json'
    family.write_text('{"version":"synthetic"}')
    result = runner.run_local_physical_maxcut(**dict(args, family_path=family))
    assert result['selected_root_one_hop_equal_original_bin'] is True
    assert result['original_packed_manifest_full_offset_cover_checked_in_this_run'] is True
    assert result['complete_original_name_key_domain_verified'] is False
    assert result['source_bin_ranges_reverified_in_same_native_audit'] is True
    assert result['missing_numeric_source_boundaries'][0]['node_id'] == 23
    assert result['finite_words_complete'] is False
    assert result['upstream_source_origin_independently_authenticated_here'] is False
    assert result['source_support_paid'] is False
    assert result['edit_authority'] is False
    for filename in (
        'route-new.json', 'original-packed-partition.json', 'selected-range-proof.json',
        'native-selected-physical-answer.json',
        'finite-lr-query-closure.json', 'physical-acceptance.json',
    ):
        assert (args['output_dir'] / filename).is_file()


def test_matching_external_hash_is_not_source_origin_proof(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    args['expected_source_bin_sha256'] = sha256(args['source_bin'].read_bytes()).hexdigest()
    result = runner.run_local_physical_maxcut(**args)
    assert result['source_bin_external_digest_matched_in_this_run'] is True
    assert result['upstream_source_origin_independently_authenticated_here'] is False


def test_tampered_original_hash_halts_before_producer(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    args['expected_source_bin_sha256'] = 'b'*64
    with pytest.raises(ValueError, match='externally pinned digest'):
        runner.run_local_physical_maxcut(**args)
    assert not args['output_dir'].exists()


def test_tampered_manifest_halts_before_producer(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    args['manifest'].write_text('{"changed": 7}')
    with pytest.raises(ValueError, match='manifest SHA256 mismatch'):
        runner.run_local_physical_maxcut(**args)


def test_duplicate_numeric_node_and_duplicate_qid_fail(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match='numeric source frontier'):
        runner.run_local_physical_maxcut(**dict(args, extra_nodes=[9,9]))
    with pytest.raises(ValueError, match='QID roots'):
        runner.run_local_physical_maxcut(**dict(args, qids=['Q1','Q1']))


def test_preexisting_evidence_cannot_be_overwritten(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    args['output_dir'].mkdir()
    (args['output_dir'] / 'route-new.json').write_text('historic source')
    with pytest.raises(ValueError, match='refuse overwrite'):
        runner.run_local_physical_maxcut(**args)
    assert (args['output_dir'] / 'route-new.json').read_text() == 'historic source'


def test_forged_manifest_offset_is_rejected_by_full_partition_audit(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    manifest = json.loads(args['manifest'].read_text())
    manifest['sections']['right']['chunks'][0]['offset'] += 1
    args['manifest'].write_text(json.dumps(manifest, sort_keys=True))
    args['manifest_sha256'] = sha256(args['manifest'].read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='discontinuity/overlap'):
        runner.run_local_physical_maxcut(**args)
    assert not (args['output_dir'] / 'selected-range-proof.json').exists()


def test_entire_packed_original_partition_source_geometry_is_recorded(tmp_path, monkeypatch):
    args = setup(tmp_path, monkeypatch)
    result = runner.run_local_physical_maxcut(**args)
    partition = json.loads((args['output_dir'] / 'original-packed-partition.json').read_text())
    assert partition['manifest_offset_cover_gap_free'] is True
    assert partition['manifest_offset_cover_nonoverlapping'] is True
    assert partition['actual_original_bin_size_compared'] is True
    assert partition['upstream_original_bin_authenticated'] is False
    assert partition['complete_original_name_key_domain_verified'] is False
    assert len(result['original_packed_partition_raw_sha256']) == 64
