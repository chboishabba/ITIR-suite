"""Source-native full Wikibase JSON negative-control checks. Synthetic only."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_wikidata_native_entity_snapshot import verify_native_entity_snapshot

QID = 'Q10403939'
GUID = QID + '$8b41c386-ec2f-41a3-9b64-000000000001'
P = 'P14143'
REV = 1234


def fixture():
    return {'entities': {QID: {
        'id': QID, 'lastrevid': REV, 'claims': {P:[{
            'type':'statement','id':GUID,'rank':'normal',
            'mainsnak':{'property':P,'snaktype':'value','datatype':'quantity',
                        'datavalue':{'type':'quantity','value':{'amount':'+20.6','unit':'http://www.wikidata.org/entity/Q8799','lowerBound':'+20.5','upperBound':'+20.7'}}},
            'qualifiers':{'P585':[{'property':'P585','snaktype':'value','datatype':'time',
                 'datavalue':{'type':'time','value':{'time':'+2024-01-01T00:00:00Z','precision':9,'timezone':0}}}]},
            'references':[{'hash':'ref-1','snaks':{'P854':[{'property':'P854','snaktype':'value','datatype':'url',
                         'datavalue':{'type':'string','value':'https://example.org/primary.pdf'}}]}}]
        }]}
    }}}


def run(tmp_path, data=None, **overrides):
    path = tmp_path / 'entity.json'
    raw = json.dumps(data if data is not None else fixture(), sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(raw)
    params = dict(path=path, expected_sha256=sha256(raw).hexdigest(), qid=QID,
                  statement_guid=GUID, property_id=P, entity_revision=REV)
    params.update(overrides)
    return verify_native_entity_snapshot(**params)


def test_full_quantity_and_native_p854_read_only(tmp_path):
    result = run(tmp_path)
    assert result['statement_guid'] == GUID
    assert result['native_quantity']['amount'] == '+20.6'
    assert result['native_quantity']['upperBound'] == '+20.7'
    assert result['native_statement_rank'] == 'normal'
    assert result['qualifiers'][0]['property'] == 'P585'
    assert result['references'][0]['snaks'][0]['property'] == 'P854'
    assert result['p854_url_candidates'] == ['https://example.org/primary.pdf']
    for key in ['upstream_http_provenance_independently_verified', 'p854_documents_independently_verified',
                'statement_semantics_independently_verified', 'reviewed_source_support_paid',
                'persisted_s29_review_verified', 'creates_world_truth', 'edit_authority']:
        assert result[key] is False


def test_wrong_expected_digest_rejected(tmp_path):
    with pytest.raises(ValueError, match='raw SHA256 differs'):
        run(tmp_path, expected_sha256='f'*64)


@pytest.mark.parametrize('kind', ['wrong_revision','wrong_entity','unknown_guid','missing_property','other_guid_duplicate','rest_schema'])
def test_native_identity_fail_closed(tmp_path, kind):
    data = fixture()
    if kind == 'wrong_revision': data['entities'][QID]['lastrevid'] = 1235
    if kind == 'wrong_entity': data['entities'][QID]['id'] = 'Q9'
    if kind == 'unknown_guid': data['entities'][QID]['claims'][P][0]['id'] = 'Q1$other'
    if kind == 'missing_property': data['entities'][QID]['claims'] = {}
    if kind == 'other_guid_duplicate': data['entities'][QID]['claims'][P].append(copy.deepcopy(data['entities'][QID]['claims'][P][0]))
    if kind == 'rest_schema':
        data['entities'][QID].pop('claims')
        data['entities'][QID]['statements'] = {}
    with pytest.raises(ValueError): run(tmp_path, data=data)


@pytest.mark.parametrize('kind', ['wrong_mainsnak_property','novalue','nonquantity','invalid_amount','invalid_bound','bad_qualifier_property','bad_reference_property','invalid_p854_value'])
def test_native_snak_and_quantity_fail_closed(tmp_path, kind):
    data = fixture()
    st = data['entities'][QID]['claims'][P][0]
    main = st['mainsnak']
    if kind == 'wrong_mainsnak_property': main['property'] = 'P31'
    if kind == 'novalue': main['snaktype'] = 'novalue'; main.pop('datavalue')
    if kind == 'nonquantity': main['datatype'] = 'string'; main['datavalue'] = {'type':'string','value':'20.6'}
    if kind == 'invalid_amount': main['datavalue']['value']['amount'] = 'NaN'
    if kind == 'invalid_bound': main['datavalue']['value']['upperBound'] = 'infinity'
    if kind == 'bad_qualifier_property': st['qualifiers']['P585'][0]['property'] = 'P580'
    if kind == 'bad_reference_property': st['references'][0]['snaks']['P854'][0]['property'] = 'P248'
    if kind == 'invalid_p854_value': st['references'][0]['snaks']['P854'][0]['datavalue']['value'] = 'javascript:alert(1)'
    with pytest.raises(ValueError): run(tmp_path, data=data)


def test_duplicate_json_key_rejected(tmp_path):
    path = tmp_path / 'entity.json'
    raw = b'{"entities":{},"entities":{}}'
    path.write_bytes(raw)
    with pytest.raises(ValueError, match='duplicate original Wikibase JSON key'):
        verify_native_entity_snapshot(path=path, expected_sha256=sha256(raw).hexdigest(), qid=QID,
                                      statement_guid=GUID, property_id=P, entity_revision=REV)


def test_over_budget_and_guid_prefix_rejected(tmp_path):
    with pytest.raises(ValueError, match='budget'):
        run(tmp_path, max_bytes=4)
    with pytest.raises(ValueError, match='GUID'):
        run(tmp_path, statement_guid='Q42$' + GUID.split('$', 1)[1])


def test_non_p14143_nonquantity_preserves_value(tmp_path):
    data = fixture()
    entity = data['entities'][QID]
    st = entity['claims'].pop(P)[0]
    st['mainsnak'] = {'property':'P5991','snaktype':'value','datatype':'string',
                      'datavalue':{'type':'string','value':'https://example.org/nat'}}
    entity['claims']['P5991'] = [st]
    result = run(tmp_path, data=data, property_id='P5991')
    assert result['native_quantity'] is None
    assert result['native_mainsnak']['datavalue']['value'] == 'https://example.org/nat'
