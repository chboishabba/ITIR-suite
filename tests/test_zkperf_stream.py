from __future__ import annotations

import json
from pathlib import Path

from itir_jmd_bridge.cli import main as cli_main
from itir_jmd_bridge.zkperf_stream import (
    apply_zkperf_stream_retention_policy,
    build_zkperf_stream_bundle,
    build_zkperf_stream_index,
    build_zkperf_stream_latest,
    get_zkperf_stream_index_record,
    load_zkperf_stream_fixture,
    load_remote_zkperf_stream_index_ipfs,
    publish_zkperf_stream_index_to_hf,
    publish_zkperf_stream_to_hf,
    resolve_remote_zkperf_stream_window,
    resolve_remote_zkperf_stream_window_ipfs,
    resolve_remote_zkperf_stream_windows,
    resolve_remote_zkperf_stream_windows_ipfs,
    resolve_zkperf_stream_from_index_hf,
    resolve_zkperf_stream_from_index_ipfs,
    update_zkperf_stream_index,
    write_zkperf_stream_publish_artifacts,
)

FIXTURE = Path('docs/planning/jmd_fixtures/zkperf_stream_v1.example.json')


def test_build_zkperf_stream_bundle() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    assert bundle['streamManifest']['streamId'] == 'zkperf-stream-demo'
    assert len(bundle['streamManifest']['windows']) == 2
    assert bundle['streamManifest']['latestWindowId'] == 'window-0002'
    assert bundle['streamManifest']['observationCount'] == 2
    index = bundle['streamManifest']['observationIndex']
    assert len(index) == 2
    assert index[0]['observationId']
    assert index[0]['runId']
    assert index[0]['traceId']
    assert index[0]['hash']
    assert bundle['tarDigest']
    # Ensure artifact/stream metrics are injected into observations.
    import tarfile
    import io
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(bundle['tarBytes']), mode='r:*') as handle:
        member = handle.getmember('windows/window-0001.json')
        extracted = handle.extractfile(member)
        assert extracted is not None
        payload = json.loads(extracted.read().decode('utf-8'))
    metrics = payload['observations'][0]['metrics']
    metric_keys = {item.get('metric') or item.get('name') for item in metrics}
    assert 'stream_window_count' in metric_keys
    assert 'stream_observation_count' in metric_keys
    assert 'window_observation_count' in metric_keys
    assert 'window_sequence' in metric_keys


def test_publish_zkperf_stream_to_hf(monkeypatch) -> None:
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.upload_hf_file_with_ack',
        lambda **kwargs: {
            'acknowledgedRevision': 'rev-demo',
            'localSha256': build_zkperf_stream_bundle(load_zkperf_stream_fixture(FIXTURE))['tarDigest'],
            'localSizeBytes': len(build_zkperf_stream_bundle(load_zkperf_stream_fixture(FIXTURE))['tarBytes']),
            'hfUri': kwargs['hf_uri'],
            'fetch': {'statusCode': 200},
            'verified': True,
        },
    )
    output = publish_zkperf_stream_to_hf(
        fixture_path=FIXTURE,
        hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.tar',
        commit_message='demo',
    )
    assert output['hfReceipt']['verified'] is True
    assert output['streamManifest']['containerObjectRef']['uri'].startswith('hf://datasets/chbwa/')
    assert output['streamLatest']['latestWindowId'] == 'window-0002'
    assert output['streamLatest']['observationCount'] == output['streamManifest']['observationCount']
    assert output['timings']['streamBuildMs'] >= 0
    assert output['timings']['hfPublishMs'] >= 0


def test_update_zkperf_stream_index_append() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    index = update_zkperf_stream_index(
        existing_index=build_zkperf_stream_index(
            stream_id='zkperf-stream-demo',
            index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
            created_at='2026-03-30T10:00:00Z',
        ),
        stream_manifest=bundle['streamManifest'],
        hf_receipt={'acknowledgedRevision': 'rev-demo', 'verified': True},
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
    )
    assert index['latestRevision'] == 'rev-20260330-a'
    assert index['revisionCount'] == 1
    assert index['revisions'][0]['latestWindowId'] == 'window-0002'
    assert index['revisions'][0]['windows'][1]['windowId'] == 'window-0002'


def test_update_zkperf_stream_index_preserves_prior_revision() -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle_a = build_zkperf_stream_bundle(fixture)
    index = update_zkperf_stream_index(
        existing_index=None,
        stream_manifest=bundle_a['streamManifest'],
        hf_receipt={'acknowledgedRevision': 'rev-a', 'verified': True},
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
    )
    fixture_b = json.loads(json.dumps(fixture))
    fixture_b['streamRevision'] = 'rev-20260330-b'
    fixture_b['createdAtUtc'] = '2026-03-30T11:00:00Z'
    fixture_b['windows'].append({
        'windowId': 'window-0003',
        'sequence': 3,
        'runId': 'run-20260330-b',
        'traceId': 'trace-20260330-0003',
        'observationIds': ['zkperf-obsv-0003'],
        'startedAtUtc': '2026-03-30T11:00:00Z',
        'endedAtUtc': '2026-03-30T11:00:03Z',
        'payload': {'observations': []},
    })
    bundle_b = build_zkperf_stream_bundle(fixture_b)
    updated = update_zkperf_stream_index(
        existing_index=index,
        stream_manifest=bundle_b['streamManifest'],
        hf_receipt={'acknowledgedRevision': 'rev-b', 'verified': True},
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
    )
    assert updated['latestRevision'] == 'rev-20260330-b'
    assert updated['revisionCount'] == 2
    assert [item['streamRevision'] for item in updated['revisions']] == ['rev-20260330-a', 'rev-20260330-b']
    assert updated['revisions'][1]['windows'][-1]['windowId'] == 'window-0003'


def test_apply_zkperf_stream_retention_policy_latest_n() -> None:
    kept = apply_zkperf_stream_retention_policy(
        [
            {'streamRevision': 'rev-a'},
            {'streamRevision': 'rev-b'},
            {'streamRevision': 'rev-c'},
        ],
        {
            'policyVersion': 'zkperf-retention/v1',
            'mode': 'retain-latest-n',
            'maxRevisionCount': 2,
        },
    )
    assert [item['streamRevision'] for item in kept] == ['rev-b', 'rev-c']


def test_update_zkperf_stream_index_enforces_retention() -> None:
    policy = {
        'policyVersion': 'zkperf-retention/v1',
        'mode': 'retain-latest-n',
        'maxRevisionCount': 2,
    }
    base = build_zkperf_stream_index(
        stream_id='zkperf-stream-demo',
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
        created_at='2026-03-30T10:00:00Z',
        retention_policy=policy,
    )
    revisions = []
    for suffix, seq in [('a', 2), ('b', 3), ('c', 4)]:
        fixture = load_zkperf_stream_fixture(FIXTURE)
        fixture['streamRevision'] = f'rev-20260330-{suffix}'
        fixture['windows'] = fixture['windows'][:]
        fixture['windows'][-1]['sequence'] = seq
        fixture['windows'][-1]['windowId'] = f'window-000{seq}'
        bundle = build_zkperf_stream_bundle(fixture)
        base = update_zkperf_stream_index(
            existing_index=base,
            stream_manifest=bundle['streamManifest'],
            hf_receipt={'acknowledgedRevision': f'ack-{suffix}', 'verified': True},
            retention_policy=policy,
        )
        revisions = [item['streamRevision'] for item in base['revisions']]
    assert revisions == ['rev-20260330-b', 'rev-20260330-c']
    assert base['revisionCount'] == 2
    assert base['latestRevision'] == 'rev-20260330-c'


def test_publish_zkperf_stream_index_to_hf(monkeypatch) -> None:
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.upload_hf_file_with_ack',
        lambda **kwargs: {
            'acknowledgedRevision': 'rev-index',
            'localSha256': 'abc',
            'localSizeBytes': 123,
            'hfUri': kwargs['hf_uri'],
            'fetch': {'statusCode': 200},
            'verified': True,
        },
    )
    receipt = publish_zkperf_stream_index_to_hf(
        stream_index={'streamId': 'zkperf-stream-demo', 'latestRevision': 'rev-20260330-a'},
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
    )
    assert receipt['verified'] is True


def test_get_zkperf_stream_index_record_latest() -> None:
    record = get_zkperf_stream_index_record(
        {
            'latestRevision': 'rev-b',
            'revisions': [
                {'streamRevision': 'rev-a'},
                {'streamRevision': 'rev-b'},
            ],
        },
        latest=True,
    )
    assert record['streamRevision'] == 'rev-b'


def test_resolve_remote_zkperf_stream_window(monkeypatch) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.download_hf_object_bytes',
        lambda **kwargs: {
            'bytes': bundle['tarBytes'],
            'metadata': {'statusCode': 200, 'revision': kwargs['revision'], 'sha256': bundle['tarDigest']},
        },
    )
    payload = resolve_remote_zkperf_stream_window(
        stream_manifest=bundle['streamManifest'],
        hf_revision='rev-demo',
        window_id='window-0001',
    )
    assert payload['window']['windowId'] == 'window-0001'
    assert payload['payload']['json']['observations'][0]['zkperf_observation_id'] == 'zkperf-obsv-0001'


def test_resolve_remote_zkperf_stream_windows_latest(monkeypatch) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.download_hf_object_bytes',
        lambda **kwargs: {
            'bytes': bundle['tarBytes'],
            'metadata': {'statusCode': 200, 'revision': kwargs['revision'], 'sha256': bundle['tarDigest']},
        },
    )
    payload = resolve_remote_zkperf_stream_windows(
        stream_manifest=bundle['streamManifest'],
        hf_revision='rev-demo',
        latest=True,
    )
    assert payload['selection']['selectedWindowIds'] == ['window-0002']
    assert payload['windows'][0]['payload']['json']['observations'][0]['zkperf_observation_id'] == 'zkperf-obsv-0002'


def test_resolve_zkperf_stream_from_index_hf(monkeypatch) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    fixture_b = json.loads(json.dumps(fixture))
    fixture_b['streamRevision'] = 'rev-20260330-b'
    fixture_b['windows'].append({
        'windowId': 'window-0003',
        'sequence': 3,
        'runId': 'run-20260330-b',
        'traceId': 'trace-20260330-0003',
        'observationIds': ['zkperf-obsv-0003'],
        'startedAtUtc': '2026-03-30T11:00:00Z',
        'endedAtUtc': '2026-03-30T11:00:03Z',
        'payload': {
            'observations': [{
                'zkperf_observation_id': 'zkperf-obsv-0003',
            }]
        },
    })
    bundle = build_zkperf_stream_bundle(fixture_b)
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.load_remote_zkperf_stream_index',
        lambda *args, **kwargs: {
            'latestRevision': 'rev-20260330-b',
            'revisions': [{
                'streamRevision': 'rev-20260330-b',
                'acknowledgedRevision': 'rev-demo',
                'windowCount': bundle['streamManifest']['windowCount'],
                'latestWindowId': bundle['streamManifest']['latestWindowId'],
                'sequenceRange': bundle['streamManifest']['sequenceRange'],
                'windows': bundle['streamManifest']['windows'],
                'containerObjectRef': bundle['streamManifest']['containerObjectRef'],
            }],
        },
    )
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.download_hf_object_bytes',
        lambda **kwargs: {
            'bytes': bundle['tarBytes'],
            'metadata': {'statusCode': 200, 'revision': kwargs['revision'], 'sha256': bundle['tarDigest']},
        },
    )
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream.load_zkperf_stream_fixture',
        lambda path: fixture,
    )
    payload = resolve_zkperf_stream_from_index_hf(
        fixture_path=FIXTURE,
        index_hf_uri='hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
        latest=True,
    )
    assert payload['streamIndex']['resolvedStreamRevision'] == 'rev-20260330-b'
    assert payload['windows'][0]['window']['windowId'] == 'window-0003'
    assert payload['timings']['indexLoadMs'] >= 0
    assert payload['timings']['fetchAndExtractMs'] >= 0


def test_write_zkperf_stream_publish_artifacts(tmp_path: Path) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    latest = build_zkperf_stream_latest(
        bundle['streamManifest'],
        {'acknowledgedRevision': 'rev-demo', 'verified': True},
    )
    paths = write_zkperf_stream_publish_artifacts(
        output_root=tmp_path,
        publish_payload={
            'streamManifest': bundle['streamManifest'],
            'streamLatest': latest,
            'hfReceipt': {'acknowledgedRevision': 'rev-demo', 'verified': True},
            'streamIndex': {'latestRevision': 'rev-20260330-a'},
            'streamIndexReceipt': {'acknowledgedRevision': 'rev-index', 'verified': True},
        },
    )
    assert Path(paths['streamManifest']).exists()
    assert Path(paths['streamLatest']).exists()
    assert Path(paths['hfReceipt']).exists()
    assert Path(paths['streamIndex']).exists()
    assert Path(paths['streamIndexReceipt']).exists()


def test_cli_build_zkperf_stream(tmp_path: Path) -> None:
    output_path = tmp_path / 'zkperf-stream.json'
    rc = cli_main([
        'build-zkperf-stream',
        '--fixture',
        str(FIXTURE),
        '--output',
        str(output_path),
    ])
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['streamManifest']['streamId'] == 'zkperf-stream-demo'


def test_cli_publish_zkperf_stream_hf(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        'itir_jmd_bridge.cli.publish_zkperf_stream_to_hf',
        lambda **kwargs: {
            'streamManifest': {'streamId': 'zkperf-stream-demo'},
            'streamLatest': {'latestWindowId': 'window-0002'},
            'hfReceipt': {'acknowledgedRevision': 'rev-demo', 'verified': True},
            'streamIndex': {'latestRevision': 'rev-20260330-a'},
            'streamIndexReceipt': {'acknowledgedRevision': 'rev-index', 'verified': True},
        },
    )
    output_path = tmp_path / 'zkperf-publish.json'
    rc = cli_main([
        'publish-zkperf-stream-hf',
        '--fixture',
        str(FIXTURE),
        '--hf-uri',
        'hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.tar',
        '--index-hf-uri',
        'hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
        '--retain-latest-n',
        '2',
        '--output',
        str(output_path),
    ])
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['hfReceipt']['verified'] is True


def test_cli_resolve_zkperf_stream_window_hf(monkeypatch, tmp_path: Path) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream_transport.download_hf_object_bytes',
        lambda **kwargs: {
            'bytes': bundle['tarBytes'],
            'metadata': {'statusCode': 200, 'revision': kwargs['revision'], 'sha256': bundle['tarDigest']},
        },
    )
    output_path = tmp_path / 'zkperf-window.json'
    rc = cli_main([
        'resolve-zkperf-stream-window-hf',
        '--fixture',
        str(FIXTURE),
        '--hf-uri',
        'hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.tar',
        '--revision',
        'rev-demo',
        '--window-id',
        'window-0002',
        '--output',
        str(output_path),
    ])
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['window']['windowId'] == 'window-0002'


def test_cli_resolve_zkperf_stream_range_hf(monkeypatch, tmp_path: Path) -> None:
    fixture = load_zkperf_stream_fixture(FIXTURE)
    bundle = build_zkperf_stream_bundle(fixture)
    monkeypatch.setattr(
        'itir_jmd_bridge.zkperf_stream_transport.download_hf_object_bytes',
        lambda **kwargs: {
            'bytes': bundle['tarBytes'],
            'metadata': {'statusCode': 200, 'revision': kwargs['revision'], 'sha256': bundle['tarDigest']},
        },
    )
    output_path = tmp_path / 'zkperf-range.json'
    rc = cli_main([
        'resolve-zkperf-stream-range-hf',
        '--fixture',
        str(FIXTURE),
        '--hf-uri',
        'hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.tar',
        '--revision',
        'rev-demo',
        '--latest',
        '--output',
        str(output_path),
    ])
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['selection']['selectedWindowIds'] == ['window-0002']


def test_cli_resolve_zkperf_stream_from_index_hf(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        'itir_jmd_bridge.cli.resolve_zkperf_stream_from_index_hf',
        lambda **kwargs: {
            'streamIndex': {'resolvedStreamRevision': 'rev-20260330-b'},
            'windows': [{'window': {'windowId': 'window-0003'}}],
        },
    )
    output_path = tmp_path / 'zkperf-from-index.json'
    rc = cli_main([
        'resolve-zkperf-stream-from-index-hf',
        '--fixture',
        str(FIXTURE),
        '--index-hf-uri',
        'hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/zkperf-stream-demo.index.json',
        '--latest',
        '--output',
        str(output_path),
    ])
    assert rc == 0
    payload = json.loads(output_path.read_text(encoding='utf-8'))
    assert payload['windows'][0]['window']['windowId'] == 'window-0003'
