"""Check incident contract fixture boundaries (not a production scanner)."""
import json
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / 'docs/planning/jmd_fixtures/cursor_claude_extension_20261029_v1.json'

def test_advisory_scope():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    assert data['schema'] == 'supply-chain-incident-evidence/v1'
    assert set(data['advisory']['versions']) == {'2.1.312', '2.1.313'}
    assert 'linux-x64' not in data['advisory']['confirmed_targets']
    assert data['advisory']['publisher_compromise_confirmed'] is False
    assert len(data['known_modified_vsix_sha256']) == 2

def test_no_promoted_conclusions_without_independent_evidence():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    cases = {case['id']: case for case in data['cases']}
    for case_id in ('version-window-candidate', 'loaded-is-not-proven-executed'):
        assert cases[case_id]['expected']['execution'] == 'unknown'
    for case_id in ('key-does-not-prove-remote-access', 'tunnel-does-not-prove-login'):
        assert cases[case_id]['expected']['remote_access'] != 'authentication_observed'
    for case_id in ('updated-extension-is-not-cleanup', 'no-marker-does-not-prove-clean'):
        assert cases[case_id]['expected']['recovery'] == 'not_assessed'
    assert cases['linux-payload-not-linux-publication']['expected']['release'] == 'unknown'
    assert cases['different-channel-not-proven-exposed']['expected']['release'] == 'unknown'

def test_distinct_package_hashes():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    hashes = [value for variants in data['known_modified_vsix_sha256'].values() for value in variants.values()]
    assert len(hashes) == 4 and len(set(hashes)) == 4
    assert all(len(value) == 64 for value in hashes)
