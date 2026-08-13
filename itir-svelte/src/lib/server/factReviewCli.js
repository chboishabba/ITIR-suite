export function parseFactReviewCliPayload(raw, field) {
  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (e) {
    throw new Error(`Failed to parse SensibLaw CLI output as JSON: ${e}\nRaw output: ${raw.slice(0, 500)}`);
  }

  if (!payload?.ok) {
    throw new Error(`SensibLaw CLI reported failure: ${payload?.error || 'Unknown error'}`);
  }

  if (!(field in payload)) {
    throw new Error(`SensibLaw CLI response missing expected field: ${field}`);
  }

  return payload[field];
}

export function classifyFactReviewErrorMessage(message) {
  const detail = `${message ?? ''}`.trim();
  if (
    detail.includes('No fact workflow link found') ||
    detail.includes('No fact-intake run found') ||
    detail.includes('No fact review run found') ||
    detail.includes('No fact-review run found')
  ) {
    return {
      kind: 'missing_run',
      title: 'No persisted fact-review run matched this selector.',
      detail,
    };
  }
  if (detail.includes('Failed to parse SensibLaw CLI output as JSON')) {
    return {
      kind: 'parse_error',
      title: 'The fact-review backend returned malformed data.',
      detail,
    };
  }
  if (detail.includes('SensibLaw CLI reported failure')) {
    return {
      kind: 'backend_error',
      title: 'The fact-review backend reported a query failure.',
      detail,
    };
  }
  return {
    kind: 'unknown_error',
    title: 'The fact-review route could not load this persisted run.',
    detail,
  };
}
