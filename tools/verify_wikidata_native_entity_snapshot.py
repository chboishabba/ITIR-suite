#!/usr/bin/env python3
"""Strict offline full Wikibase JSON snapshot verifier for native statement candidates.

Proves raw local bytes match an independently supplied SHA-256, that a specified
revision/QID/GUID/property is present in a full original Wikibase entity, and
extracts *all* native qualifier and reference snaks. No HTTP/source-document
provenance, semantic truth, P854 citation support or edit rights are inferred.

The accepted schema is Special:EntityData and wbgetentities full Wikibase JSON,
not the differently-shaped Wikibase REST statement format or WDQS SPARQL rows.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any

_QID = re.compile(r'Q[1-9][0-9]*\Z')
_PID = re.compile(r'P[1-9][0-9]*\Z')
_SHA256 = re.compile(r'[0-9a-f]{64}\Z')
_MAX_BYTES = 64 * 1024 * 1024


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError(f'duplicate original Wikibase JSON key: {k}')
        result[k] = v
    return result


def _decode_json(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=_object_no_duplicates,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'invalid number: {x}')))
    if type(value) is not dict:
        raise ValueError('native full entity snapshot must be a JSON object')
    return value


def _snak(snak: Any, property_id: str) -> dict[str, Any]:
    if type(snak) is not dict or snak.get('property') != property_id:
        raise ValueError('Wikibase snak property mismatches its statement/qualifier/reference slot')
    snaktype = snak.get('snaktype')
    if snaktype not in ('value', 'somevalue', 'novalue'):
        raise ValueError('unrecognised Wikibase snak type')
    kind = snak.get('datatype')
    if not isinstance(kind, str) or not kind:
        raise ValueError('native snak datatype absent')
    if snaktype == 'value':
        data = snak.get('datavalue')
        if type(data) is not dict or not isinstance(data.get('type'), str) or 'value' not in data:
            raise ValueError('value snak missing typed datavalue')
        payload = data
    else:
        if 'datavalue' in snak:
            raise ValueError('novalue/somevalue snak must not carry a datavalue')
        payload = None
    return {
        'property': property_id,
        'snaktype': snaktype,
        'datatype': kind,
        'datavalue': payload,
        'hash': snak.get('hash') if isinstance(snak.get('hash'), str) else None,
    }


def _snak_lists(raw: Any, *, reference: bool = False) -> list[dict[str, Any]]:
    """Flatten without losing order, individual snaks or reference grouping."""
    if type(raw) is not dict:
        raise ValueError('expected native qualifier/reference snaks object')
    out = []
    for pid, values in raw.items():
        if not isinstance(pid, str) or not _PID.fullmatch(pid):
            raise ValueError('invalid native qualifier/reference property key')
        if type(values) is not list:
            raise ValueError('Wikibase qualifier/reference snaks must be lists')
        for value in values:
            out.append(_snak(value, pid))
    return out


def _quantity(snak: dict[str, Any]) -> dict[str, Any] | None:
    if snak['snaktype'] != 'value':
        return None
    data = snak['datavalue']
    if snak['datatype'] != 'quantity' or data['type'] != 'quantity':
        return None
    value = data['value']
    if type(value) is not dict:
        raise ValueError('quantity value must have amount and unit')
    amount, unit = value.get('amount'), value.get('unit')
    if not isinstance(amount, str) or not re.fullmatch(r'[+-](?:[0-9]+)(?:\.[0-9]+)?', amount):
        raise ValueError('quantity amount must be exact Wikibase decimal text')
    if not isinstance(unit, str) or not unit:
        raise ValueError('quantity unit URI/text missing')
    for key in ('lowerBound', 'upperBound'):
        if key in value and (not isinstance(value[key], str) or
                             not re.fullmatch(r'[+-](?:[0-9]+)(?:\.[0-9]+)?', value[key])):
            raise ValueError('invalid quantity bound')
    return {key: value.get(key) for key in ('amount', 'unit', 'lowerBound', 'upperBound')}


def verify_native_entity_snapshot(*, path: Path, expected_sha256: str, qid: str,
                                  statement_guid: str, property_id: str,
                                  entity_revision: int, max_bytes: int = _MAX_BYTES) -> dict[str, Any]:
    if not _SHA256.fullmatch(expected_sha256):
        raise ValueError('independently pinned raw entity SHA256 is required')
    if not _QID.fullmatch(qid) or not _PID.fullmatch(property_id):
        raise ValueError('canonical QID and property ID required')
    if (not isinstance(statement_guid, str) or not statement_guid.startswith(qid + '$')
            or not statement_guid[len(qid)+1:] or any(ch.isspace() for ch in statement_guid)):
        raise ValueError('statement GUID must carry exactly the requested QID prefix')
    if type(entity_revision) is not int or entity_revision <= 0:
        raise ValueError('positive integer native entity revision required')
    if type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError('strict positive raw entity byte budget required')
    if not path.is_file() or not 0 < path.stat().st_size <= max_bytes:
        raise ValueError('raw native entity file missing or over size budget')
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError('original native entity raw SHA256 differs from independently pinned bytes')
    parsed = _decode_json(raw)
    entities = parsed.get('entities')
    if type(entities) is not dict or set(entities) != {qid}:
        raise ValueError('full Wikibase JSON must contain exactly the declared entity')
    entity = entities[qid]
    if (type(entity) is not dict or entity.get('id') != qid
            or type(entity.get('lastrevid')) is not int or entity['lastrevid'] != entity_revision):
        raise ValueError('native original entity ID or lastrevid mismatches pinned revision')
    claims = entity.get('claims')
    if type(claims) is not dict:
        raise ValueError('full native Wikibase JSON claims required (not REST statement shape)')
    statements = claims.get(property_id)
    if type(statements) is not list or not statements:
        raise ValueError('native property has no statements in pinned entity revision')
    found = [claim for claim in statements if type(claim) is dict and claim.get('id') == statement_guid]
    if len(found) != 1:
        raise ValueError('native statement GUID missing or ambiguous')
    claim = found[0]
    if claim.get('type') != 'statement':
        raise ValueError('Wikibase native claim is not a statement')
    rank = claim.get('rank')
    if rank not in ('preferred', 'normal', 'deprecated'):
        raise ValueError('native statement rank not supported')
    mainsnak = _snak(claim.get('mainsnak'), property_id)
    if property_id == 'P14143' and _quantity(mainsnak) is None:
        raise ValueError('P14143 quantitative observation requires actual numeric quantity snak')
    qualifiers = _snak_lists(claim.get('qualifiers', {}))
    references_raw = claim.get('references', [])
    if type(references_raw) is not list:
        raise ValueError('native references must be an ordered list')
    references = []
    urls = []
    for ix, ref in enumerate(references_raw):
        if type(ref) is not dict:
            raise ValueError('native reference record is not an object')
        snaks = _snak_lists(ref.get('snaks', {}), reference=True)
        p854 = [s for s in snaks if s['property'] == 'P854']
        for snak in p854:
            if (snak['snaktype'] != 'value' or snak['datatype'] != 'url'
                    or snak['datavalue']['type'] != 'string'
                    or not isinstance(snak['datavalue']['value'], str)
                    or not snak['datavalue']['value'].startswith(('https://', 'http://'))):
                raise ValueError('P854 native source URL must be an actual URL value snak')
            urls.append(snak['datavalue']['value'])
        references.append({'index': ix, 'hash': ref.get('hash') if isinstance(ref.get('hash'), str) else None,
                           'snaks': snaks})
    return {
        'version': 'itir.wikidata.raw_native_entity_statement.v1',
        'subject_qid': qid,
        'statement_guid': statement_guid,
        'property_id': property_id,
        'native_entity_revision_id': entity_revision,
        'source_kind': 'full-wikibase-json-entity',
        'raw_entity_sha256_checked': digest,
        'raw_entity_bytes_checked': len(raw),
        'native_statement_rank': rank,
        'native_mainsnak': mainsnak,
        'native_quantity': _quantity(mainsnak),
        'qualifiers': qualifiers,
        'references': references,
        'p854_url_candidates': urls,
        'same_source_native_statement_found': True,
        'snapshot_bytes_match_pinned_digest': True,
        'upstream_http_provenance_independently_verified': False,
        'p854_documents_independently_verified': False,
        'statement_semantics_independently_verified': False,
        'reviewed_source_support_paid': False,
        'persisted_s29_review_verified': False,
        'creates_world_truth': False,
        'edit_authority': False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-entity', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--qid', required=True)
    parser.add_argument('--statement-guid', required=True)
    parser.add_argument('--property', dest='property_id', required=True)
    parser.add_argument('--entity-revision', required=True, type=int)
    parser.add_argument('--max-bytes', default=_MAX_BYTES, type=int)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = verify_native_entity_snapshot(
            path=args.raw_entity, expected_sha256=args.expected_sha256,
            qid=args.qid, statement_guid=args.statement_guid,
            property_id=args.property_id, entity_revision=args.entity_revision,
            max_bytes=args.max_bytes,
        )
        body = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + '\n'
        if args.output:
            args.output.write_text(body, encoding='utf-8')
        else:
            print(body, end='')
        return 0
    except (ValueError, TypeError, UnicodeDecodeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc), 'edit_authority': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
