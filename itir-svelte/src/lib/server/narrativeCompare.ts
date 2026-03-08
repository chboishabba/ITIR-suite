import path from 'node:path';
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';

export type NarrativeValidationReport = {
  source: {
    source_id: string;
    title: string;
    origin_url?: string | null;
    source_type: string;
  };
  summary: {
    unit_count: number;
    fact_count: number;
    proposition_count: number;
    proposition_link_count: number;
    abstention_count: number;
    corroboration_ref_count: number;
  };
  facts: Array<{
    fact_id: string;
    event_id: string;
    source_id: string;
    subjects: string[];
    action: string;
    objects: string[];
    text: string;
    receipts?: Array<{ kind: string; value: string }>;
  }>;
  propositions: Array<{
    proposition_id: string;
    event_id: string;
    source_id: string;
    proposition_kind: string;
    predicate_key: string;
    anchor_text?: string;
    arguments: Array<{ role: string; value: string }>;
    receipts?: Array<{ kind: string; value: string }>;
  }>;
  proposition_links: Array<{
    link_id: string;
    event_id: string;
    source_id: string;
    source_proposition_id: string;
    target_proposition_id: string;
    link_kind: string;
    receipts?: Array<{ kind: string; value: string }>;
  }>;
  abstentions: Array<{ event_id: string; reason: string; text: string }>;
  corroboration_refs: Array<{ event_id: string; ref_kind: string; label: string; claim_text: string }>;
};

export type NarrativeComparisonReport = {
  fixture_id: string;
  sources: Array<{
    source_id: string;
    title: string;
    origin_url?: string | null;
    source_type: string;
  }>;
  reports: Record<string, NarrativeValidationReport>;
  summary: {
    shared_proposition_count: number;
    disputed_proposition_count: number;
    source_only_proposition_count: number;
    shared_fact_count: number;
    disputed_fact_count: number;
    link_difference_count: number;
  };
  shared_propositions: Array<{
    signature: string;
    left: any[];
    right: any[];
    left_attributions: string[];
    right_attributions: string[];
  }>;
  disputed_propositions: Array<{
    subject_object_key: string;
    left: any;
    right: any;
  }>;
  source_only_propositions: Record<string, any[]>;
  shared_facts: Array<{ signature: string; left: any; right: any }>;
  disputed_facts: Array<{ left: any; right: any }>;
  link_differences: Array<{ signature: string; left_attributions: string[]; right_attributions: string[] }>;
  comparison_receipts: Array<{ kind: string; value: string }>;
  abstentions: Record<string, any[]>;
  corroboration_refs: Record<string, any[]>;
};

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const candidate of candidates) {
    if (existsSync(path.join(candidate, 'SensibLaw'))) return candidate;
  }
  return path.resolve('..');
}

async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`${cmd} ${args.join(' ')} failed with ${code}\n${stderr || stdout}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

export async function loadNarrativeComparison(fixture = 'friendlyjordies_demo'): Promise<{
  fixture: { fixture_id?: string; label?: string };
  comparison: NarrativeComparisonReport;
  availableFixtures: Array<{ key: string; label: string }>;
}> {
  const repoRoot = resolveRepoRoot();
  const raw = await readStdout(
    'python3',
    [path.join('SensibLaw', 'scripts', 'narrative_compare.py'), '--fixture', fixture, 'compare'],
    repoRoot
  );
  const parsed = JSON.parse(raw);
  return {
    fixture: parsed.fixture ?? {},
    comparison: parsed.comparison as NarrativeComparisonReport,
    availableFixtures: [{ key: 'friendlyjordies_demo', label: 'FriendlyJordies public-media demo' }]
  };
}
