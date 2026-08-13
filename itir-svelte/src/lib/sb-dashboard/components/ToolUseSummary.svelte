<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let toolUse: Record<string, unknown> | undefined;

  type VariantLeaf = {
    key: string;
    label: string;
    count: number;
    example?: string; // one representative raw command (tooltip)
  };

  type TrunkGroup = {
    trunk: string; // e.g. "'PY'"
    count: number;
    leaves: VariantLeaf[];
  };

  type FindSig = {
    key: string;
    label: string;
    count: number;
    example?: string;
  };

  type FindRootGroup = {
    root: string;
    count: number;
    sigs: FindSig[];
    hiddenSigCount: number;
  };

  type DirGroup = {
    key: string; // full dir path (stable key)
    label: string; // possibly prefix-trimmed display
    count: number;
    leaves: VariantLeaf[];
    hiddenLeafCount: number;
  };

  type VariantRaw = {
    command: string;
    count: number;
    dirs_hint?: string[];
  };

  type Family = {
    family: string;
    count: number;
    unique_variants?: number;
    trunks?: TrunkGroup[];
    plain?: VariantLeaf[];
    findRoots?: FindRootGroup[];
    dirGroups?: DirGroup[];
  };

  function heredocDelimiter(cmd: string): string | null {
    const m = cmd.match(/<<\s*(['"]?)([A-Za-z0-9_]+)\1/);
    return m?.[2] ? String(m[2]) : null;
  }

  function fnv1a(text: string): string {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    // short, stable id for grouping identical scripts
    return (h >>> 0).toString(16).padStart(8, '0');
  }

  type ShellSplit = { segments: string[]; ops: string[] };

  function splitShellTopLevel(line: string): ShellSplit {
    // Conservative shell splitter for "pretty grouping" only.
    // Splits on &&, ||, ;, | when not inside single/double quotes.
    const segments: string[] = [];
    const ops: string[] = [];
    let cur = '';
    let inS = false;
    let inD = false;
    let esc = false;

    const flush = () => {
      const t = cur.trim();
      if (t) segments.push(t);
      cur = '';
    };

    for (let i = 0; i < line.length; i++) {
      const ch = line[i]!;
      if (esc) {
        cur += ch;
        esc = false;
        continue;
      }
      if (ch === '\\') {
        cur += ch;
        esc = true;
        continue;
      }
      if (!inD && ch === "'") {
        inS = !inS;
        cur += ch;
        continue;
      }
      if (!inS && ch === '"') {
        inD = !inD;
        cur += ch;
        continue;
      }

      if (!inS && !inD) {
        const two = line.slice(i, i + 2);
        if (two === '&&' || two === '||') {
          flush();
          ops.push(two);
          i++;
          continue;
        }
        if (ch === ';' || ch === '|') {
          flush();
          ops.push(ch);
          continue;
        }
      }

      cur += ch;
    }
    flush();
    return { segments, ops };
  }

  function stripEnvPrefix(seg: string): string {
    // Drop leading VAR=... assignments for operator detection/labels.
    let s = seg.trim();
    for (let i = 0; i < 6; i++) {
      const m = s.match(/^([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)\s+(.*)$/);
      if (!m) break;
      s = (m[3] ?? '').trim();
    }
    return s;
  }

  function firstToken(seg: string): string {
    const s = stripEnvPrefix(seg);
    const tok = s.split(/\s+/, 1)[0] ?? '';
    return tok.trim();
  }

  function opWordForFamily(family: string, word: string): boolean {
    const w = word.trim();
    if (!w) return false;
    const base = w.includes('/') ? w.slice(w.lastIndexOf('/') + 1) : w;
    if (family === 'python') return base === 'python' || base === 'python3' || base === 'python2';
    if (family === 'bash') return base === 'bash' || base === 'sh' || base === 'zsh';
    return base === family;
  }

  function basenameToken(tok: string): string {
    const t = tok.trim();
    if (!t) return '';
    const base = t.includes('/') ? t.slice(t.lastIndexOf('/') + 1) : t;
    return base.trim();
  }

  function focusSegmentIndex(family: string, segments: string[]): number {
    for (let i = 0; i < segments.length; i++) {
      const seg = stripEnvPrefix(segments[i] ?? '');
      const tok = seg.split(/\s+/, 1)[0] ?? '';
      if (opWordForFamily(family, tok)) return i;
    }
    return Math.max(0, segments.length - 1);
  }

  function suffixKeyAndLabel(segments: string[], ops: string[], focus: number): { key: string; label: string } {
    if (focus >= segments.length - 1) return { key: '', label: '' };
    const partsKey: string[] = [];
    const partsLabel: string[] = [];
    const maxParts = 2;
    for (let j = focus; j < Math.min(segments.length - 1, focus + maxParts); j++) {
      const op = ops[j] ?? '';
      const next = segments[j + 1] ?? '';
      const tok = firstToken(next);
      if (!op || !tok) continue;
      partsKey.push(`${op}${tok}`);
      partsLabel.push(`${op} ${truncate(next, 32)}`);
    }
    const key = partsKey.join(' ');
    const label = partsLabel.length ? ` ${partsLabel.join(' ')}` : '';
    return { key, label };
  }

  function splitLines(cmd: string): string[] {
    return cmd.replaceAll('\r\n', '\n').replaceAll('\r', '\n').split('\n');
  }

  function commonPrefix(xs: string[]): string {
    if (!xs.length) return '';
    let pref = xs[0] ?? '';
    for (let i = 1; i < xs.length; i++) {
      const t = xs[i] ?? '';
      let j = 0;
      const max = Math.min(pref.length, t.length);
      while (j < max && pref[j] === t[j]) j++;
      pref = pref.slice(0, j);
      if (!pref) break;
    }
    const cut = pref.lastIndexOf('/');
    return cut >= 0 ? pref.slice(0, cut + 1) : '';
  }

  function tokenizeShell(s: string): string[] {
    // Minimal shell-ish tokenizer: preserves quoted spans; good enough for grouping labels.
    const out: string[] = [];
    let cur = '';
    let inS = false;
    let inD = false;
    let esc = false;

    const flush = () => {
      const t = cur.trim();
      if (t) out.push(t);
      cur = '';
    };

    for (let i = 0; i < s.length; i++) {
      const ch = s[i]!;
      if (esc) {
        cur += ch;
        esc = false;
        continue;
      }
      if (ch === '\\') {
        esc = true;
        continue;
      }
      if (!inD && ch === "'") {
        inS = !inS;
        continue;
      }
      if (!inS && ch === '"') {
        inD = !inD;
        continue;
      }
      if (!inS && !inD && /\s/.test(ch)) {
        flush();
        continue;
      }
      cur += ch;
    }
    flush();
    return out;
  }

  function isPatchBlock(cmd: string): boolean {
    const s = cmd.trimStart();
    if (s.startsWith('*** Begin Patch')) return true;
    // Sometimes the patch is nested in a larger string; still treat as patch-like.
    return cmd.includes('\n*** Begin Patch') || cmd.includes('*** Begin Patch\n');
  }

  function parsePatchSummary(cmd: string): { label: string; key: string } {
    const lines = splitLines(cmd);
    const hits: Array<{ op: string; path: string }> = [];

    for (const ln of lines) {
      const s = ln.trim();
      if (s.startsWith('*** Update File: ')) hits.push({ op: 'Update', path: s.slice('*** Update File: '.length).trim() });
      else if (s.startsWith('*** Add File: ')) hits.push({ op: 'Add', path: s.slice('*** Add File: '.length).trim() });
      else if (s.startsWith('*** Delete File: ')) hits.push({ op: 'Delete', path: s.slice('*** Delete File: '.length).trim() });
      else if (s.startsWith('*** Move to: ')) hits.push({ op: 'Move', path: s.slice('*** Move to: '.length).trim() });
      if (hits.length >= 8) break;
    }

    if (!hits.length) {
      const key = `patch:${fnv1a(cmd)}`;
      return { label: 'Patch (unparsed)', key };
    }

    const uniq = new Map<string, { op: string; path: string }>();
    for (const h of hits) {
      const k = `${h.op}:${h.path}`;
      if (!uniq.has(k)) uniq.set(k, h);
    }
    const items = [...uniq.values()];

    const opCounts = new Map<string, number>();
    for (const h of items) opCounts.set(h.op, (opCounts.get(h.op) ?? 0) + 1);
    const opSummary = [...opCounts.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([op, n]) => `${op}${n > 1 ? `×${n}` : ''}`)
      .join(', ');

    const first = items[0]!;
    const extra = items.length > 1 ? ` (+${items.length - 1})` : '';
    const label = `${opSummary}: ${truncate(first.path, 56)}${extra}`;
    const key = `patch:${fnv1a(items.map((h) => `${h.op}:${h.path}`).join('|'))}`;
    return { label, key };
  }

  function extractHeredocBody(cmd: string, delim: string): string {
    const lines = splitLines(cmd);
    // Identify the line that starts the heredoc and the delimiter terminator line.
    const start = lines.findIndex((ln) => ln.includes('<<') && ln.includes(delim));
    let end = -1;
    for (let i = lines.length - 1; i >= 0; i--) {
      if (lines[i]?.trim() === delim) {
        end = i;
        break;
      }
    }
    if (start >= 0 && end > start) return lines.slice(start + 1, end).join('\n');
    // Fallback: best-effort, still groupable by hash.
    return cmd;
  }

  function firstMeaningfulLine(body: string): string {
    for (const ln of splitLines(body)) {
      const s = ln.trim();
      if (!s) continue;
      if (s.startsWith('#')) continue;
      return s;
    }
    return '';
  }

  function firstNonImportLine(body: string): string {
    for (const ln of splitLines(body)) {
      const s = ln.trim();
      if (!s) continue;
      if (s.startsWith('#')) continue;
      if (s.startsWith('import ') || s.startsWith('from ')) continue;
      return s;
    }
    return '';
  }

  function truncate(s: string, n: number): string {
    const t = s.replace(/\s+/g, ' ').trim();
    if (t.length <= n) return t;
    return t.slice(0, Math.max(0, n - 1)) + '…';
  }

  function heredocSubLabel(family: string, cmd: string, delim: string): { label: string; key: string } {
    const firstLine = splitLines(cmd)[0] ?? '';
    const split = splitShellTopLevel(firstLine);
    const focus = focusSegmentIndex(family, split.segments);
    const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);

    const body = extractHeredocBody(cmd, delim);
    const a = firstMeaningfulLine(body);
    const b = firstNonImportLine(body);
    const head = a && b && b !== a && (a.startsWith('import ') || a.startsWith('from ')) ? `${a} | ${b}` : a || b || '(empty)';
    const key = `heredoc:${delim}:${fnv1a(body)}:${suffix.key}`;
    return { label: truncate(head, 64) + suffix.label, key };
  }

  function aggregateVariants(
    family: string,
    raw: unknown
  ): { trunks: TrunkGroup[]; plain: VariantLeaf[] } | null {
    if (!Array.isArray(raw)) return null;

    const plain = new Map<string, VariantLeaf>();
    const trunks = new Map<string, Map<string, VariantLeaf>>();
    const trunkCounts = new Map<string, number>();

    for (const v of raw) {
      const cmd = String((v as any)?.command ?? '');
      const count = Number((v as any)?.count ?? 0) || 0;
      if (!cmd.trim() || count <= 0) continue;

      if (isPatchBlock(cmd)) {
        const trunk = "'PATCH'";
        const sub = parsePatchSummary(cmd);
        const leafMap = trunks.get(trunk) ?? new Map<string, VariantLeaf>();
        const cur = leafMap.get(sub.key) ?? { key: sub.key, label: sub.label, count: 0, example: cmd };
        cur.count += count;
        leafMap.set(sub.key, cur);
        trunks.set(trunk, leafMap);
        trunkCounts.set(trunk, (trunkCounts.get(trunk) ?? 0) + count);
        continue;
      }

      const firstLine = splitLines(cmd)[0] ?? cmd;
      const split = splitShellTopLevel(firstLine);
      const focus = focusSegmentIndex(family, split.segments);
      const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);

      const delim = heredocDelimiter(cmd);
      if (delim) {
        const trunk = `'${delim}'`;
        const sub = heredocSubLabel(family, cmd, delim);
        const leafMap = trunks.get(trunk) ?? new Map<string, VariantLeaf>();
        const cur = leafMap.get(sub.key) ?? { key: sub.key, label: sub.label, count: 0, example: cmd };
        cur.count += count;
        leafMap.set(sub.key, cur);
        trunks.set(trunk, leafMap);
        trunkCounts.set(trunk, (trunkCounts.get(trunk) ?? 0) + count);
        continue;
      }

      // Prefer displaying/grouping by the family-relevant segment (plus a compact suffix showing pipes/&&).
      const focusSeg = split.segments[focus] ?? firstLine;
      const norm = stripEnvPrefix(focusSeg);
      const k = `${norm}::${suffix.key}`.trim();
      const label = truncate(norm, 84) + suffix.label;
      const cur = plain.get(k) ?? { key: k, label, count: 0, example: cmd };
      cur.count += count;
      plain.set(k, cur);
    }

    const trunkGroups: TrunkGroup[] = [...trunks.entries()]
      .map(([trunk, leafMap]) => ({
        trunk,
        count: trunkCounts.get(trunk) ?? 0,
        leaves: [...leafMap.values()].sort((a, b) => b.count - a.count)
      }))
      .sort((a, b) => b.count - a.count);

    const plainLeaves = [...plain.values()].sort((a, b) => b.count - a.count);
    return { trunks: trunkGroups, plain: plainLeaves };
  }

  function cdContextBeforeFocus(segments: string[], focus: number): string | null {
    let cwd: string | null = null;
    for (let i = 0; i <= Math.min(focus, segments.length - 1); i++) {
      const seg = stripEnvPrefix(segments[i] ?? '').trim();
      if (!seg) continue;
      const toks = tokenizeShell(seg);
      if (!toks.length) continue;
      const op = basenameToken(toks[0] ?? '');
      if (op === 'cd' || op === 'pushd') {
        const dir = (toks[1] ?? '').trim();
        if (dir && dir !== '-') cwd = dir;
      } else if (op === 'popd') {
        // Best-effort: popd is stack-based, but for grouping we can simply clear context.
        cwd = null;
      }
    }
    return cwd;
  }

  function asVariantArray(raw: unknown): VariantRaw[] {
    if (!Array.isArray(raw)) return [];
    const out: VariantRaw[] = [];
    for (const v of raw) {
      const cmd = String((v as any)?.command ?? '');
      const count = Number((v as any)?.count ?? 0) || 0;
      const dirsHint = (v as any)?.dirs_hint;
      const dirs = Array.isArray(dirsHint) ? dirsHint.map((x: any) => String(x ?? '')).filter(Boolean) : undefined;
      if (!cmd.trim() || count <= 0) continue;
      out.push({ command: cmd, count, dirs_hint: dirs });
    }
    return out;
  }

  function bestDirHint(v: VariantRaw): string | null {
    const hs = v.dirs_hint ?? [];
    if (!hs.length) return null;
    // Prefer the most specific hint (often the absolute path).
    return hs.slice().sort((a, b) => b.length - a.length)[0] ?? null;
  }

  function compactDirLabel(full: string, pref: string): string {
    const trimmed = pref && full.startsWith(pref) ? full.slice(pref.length) : full;
    const parts = trimmed.split('/').filter(Boolean);
    return parts.length >= 2 ? parts.slice(-2).join('/') : trimmed || full;
  }

  function aggregateCdDirGroups(raw: unknown): DirGroup[] {
    const variants = asVariantArray(raw);
    const byDir = new Map<string, Map<string, VariantLeaf>>();
    const dirCounts = new Map<string, number>();

    for (const v of variants) {
      const cmd = v.command;
      const count = v.count;
      const firstLine = splitLines(cmd)[0] ?? cmd;
      const split = splitShellTopLevel(firstLine);
      if (!split.segments.length) continue;

      // Determine directory: prefer SB's dirs_hint, fallback to parsing the `cd` segment.
      let dir = bestDirHint(v);
      if (!dir) {
        const seg0 = stripEnvPrefix(split.segments[0] ?? '').trim();
        const toks0 = tokenizeShell(seg0);
        if (basenameToken(toks0[0] ?? '') === 'cd' || basenameToken(toks0[0] ?? '') === 'pushd') {
          const d = String(toks0[1] ?? '').trim();
          if (d && d !== '-') dir = d;
        }
      }
      if (!dir) dir = '(no dir)';

      // Display: show the first non-cd segment (the "real command"), plus a short suffix.
      let focus = 0;
      for (let i = 0; i < split.segments.length; i++) {
        const seg = stripEnvPrefix(split.segments[i] ?? '').trim();
        if (!seg) continue;
        const tok0 = basenameToken(tokenizeShell(seg)[0] ?? '');
        if (!tok0) continue;
        if (tok0 === 'cd' || tok0 === 'pushd' || tok0 === 'popd') continue;
        focus = i;
        break;
      }

      const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);
      const focusSeg = split.segments[focus] ?? firstLine;
      const norm = stripEnvPrefix(focusSeg);
      const leafKey = `cd:${dir}::${norm}::${suffix.key}`.trim();
      const leafLabel = truncate(norm, 84) + suffix.label;

      const leafMap = byDir.get(dir) ?? new Map<string, VariantLeaf>();
      const cur = leafMap.get(leafKey) ?? { key: leafKey, label: leafLabel, count: 0, example: cmd };
      cur.count += count;
      leafMap.set(leafKey, cur);
      byDir.set(dir, leafMap);
      dirCounts.set(dir, (dirCounts.get(dir) ?? 0) + count);
    }

    const dirsFull = [...byDir.keys()];
    const pref = commonPrefix(dirsFull);
    const groupsAll: DirGroup[] = [...byDir.entries()].map(([dirFull, leafMap]) => {
      const leavesAll = [...leafMap.values()].sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
      const MAX_LEAVES = 8;
      const leaves = leavesAll.slice(0, MAX_LEAVES);
      return {
        key: dirFull,
        label: compactDirLabel(dirFull, pref),
        count: dirCounts.get(dirFull) ?? 0,
        leaves,
        hiddenLeafCount: Math.max(0, leavesAll.length - leaves.length)
      };
    });

    const MAX_DIRS = 8;
    return groupsAll
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
      .slice(0, MAX_DIRS)
      .sort((a, b) => a.label.localeCompare(b.label));
  }

  function parseFindVariant(family: string, cmd: string): { root: string; sigKey: string; label: string; key: string } | null {
    const firstLine = splitLines(cmd)[0] ?? cmd;
    const split = splitShellTopLevel(firstLine);
    const focus = focusSegmentIndex(family, split.segments);
    const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);
    const seg = stripEnvPrefix(split.segments[focus] ?? firstLine);
    const toks = tokenizeShell(seg);
    if (!toks.length) return null;

    const op = toks[0] ?? '';
    if (!(op === 'find' || op.endsWith('/find'))) return null;

    const rest = toks.slice(1);
    const roots: string[] = [];
    let idx = 0;
    const isPredStart = (t: string) => t.startsWith('-') || t === '(' || t === ')' || t === '\\(' || t === '\\)' || t === '!' || t === '\\!';
    while (idx < rest.length && !isPredStart(rest[idx] ?? '')) {
      roots.push(rest[idx]!);
      idx++;
    }
    const root = roots.length ? roots.join(' ') : '.';
    const expr = rest.slice(idx);

    let maxdepth: string | null = null;
    let mindepth: string | null = null;
    let typeFlag: string | null = null;
    let sizeFlag: string | null = null;
    let printfFlag: string | null = null;
    let printFlag = false;
    let print0Flag = false;
    let deleteFlag = false;
    let hasOr = false;
    const names: string[] = [];
    const inames: string[] = [];
    const paths: string[] = [];
    const ipaths: string[] = [];
    let execTool: string | null = null;

    for (let i = 0; i < expr.length; i++) {
      const t = expr[i] ?? '';
      const n = expr[i + 1] ?? '';
      if (t === '-maxdepth' && n) {
        maxdepth = n;
        i++;
        continue;
      }
      if (t === '-mindepth' && n) {
        mindepth = n;
        i++;
        continue;
      }
      if (t === '-type' && n) {
        typeFlag = n;
        i++;
        continue;
      }
      if (t === '-size' && n) {
        sizeFlag = n;
        i++;
        continue;
      }
      if (t === '-printf' && n) {
        printfFlag = n;
        i++;
        continue;
      }
      if (t === '-print') {
        printFlag = true;
        continue;
      }
      if (t === '-print0') {
        print0Flag = true;
        continue;
      }
      if (t === '-delete') {
        deleteFlag = true;
        continue;
      }
      if (t === '-o') {
        hasOr = true;
        continue;
      }
      if (t === '-name' && n) {
        names.push(n);
        i++;
        continue;
      }
      if (t === '-iname' && n) {
        inames.push(n);
        i++;
        continue;
      }
      if (t === '-path' && n) {
        paths.push(n);
        i++;
        continue;
      }
      if (t === '-ipath' && n) {
        ipaths.push(n);
        i++;
        continue;
      }
      if (t === '-exec' && n) {
        execTool = firstToken(n);
        continue;
      }
    }

    const parts: string[] = [];
    if (maxdepth) parts.push(`-maxdepth ${maxdepth}`);
    if (mindepth) parts.push(`-mindepth ${mindepth}`);
    if (typeFlag) parts.push(`-type ${typeFlag}`);

    const joiner = hasOr ? ' OR ' : ', ';
    if (names.length) parts.push(`-name ${names.join(joiner)}`);
    if (inames.length) parts.push(`-iname ${inames.join(joiner)}`);
    if (paths.length) parts.push(`-path ${paths.join(joiner)}`);
    if (ipaths.length) parts.push(`-ipath ${ipaths.join(joiner)}`);

    if (sizeFlag) parts.push(`-size ${sizeFlag}`);
    if (printfFlag) parts.push(`-printf ${truncate(printfFlag, 22)}`);
    if (execTool) parts.push(`-exec ${execTool} …`);
    if (deleteFlag) parts.push('-delete');
    if (print0Flag) parts.push('-print0');
    else if (printFlag) parts.push('-print');

    const sig = parts.length ? parts.join(' ') : truncate(expr.join(' '), 84) || '(default)';
    const label = truncate(sig, 96) + suffix.label;
    const sigKey = `${sig}::${suffix.key}`;
    const key = `${root}::${sigKey}`;
    return { root, sigKey, label, key };
  }

  function aggregateFindVariants(raw: unknown): FindRootGroup[] | null {
    if (!Array.isArray(raw)) return null;
    const byRoot = new Map<string, Map<string, FindSig>>();
    const rootCounts = new Map<string, number>();

    for (const v of raw) {
      const cmd = String((v as any)?.command ?? '');
      const count = Number((v as any)?.count ?? 0) || 0;
      if (!cmd.trim() || count <= 0) continue;
      const parsed = parseFindVariant('find', cmd);
      if (!parsed) continue;
      const sigMap = byRoot.get(parsed.root) ?? new Map<string, FindSig>();
      const cur = sigMap.get(parsed.key) ?? { key: parsed.key, label: parsed.label, count: 0, example: cmd };
      cur.count += count;
      sigMap.set(parsed.key, cur);
      byRoot.set(parsed.root, sigMap);
      rootCounts.set(parsed.root, (rootCounts.get(parsed.root) ?? 0) + count);
    }

    const roots = [...byRoot.keys()];
    const pref = commonPrefix(roots);

    const rootGroups: FindRootGroup[] = [...byRoot.entries()]
      .map(([root, sigMap]) => {
        const sigsAll = [...sigMap.values()].sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));
        const MAX_SIGS = 8;
        const sigs = sigsAll.slice(0, MAX_SIGS);
        return {
          root: pref && root.startsWith(pref) ? root.slice(pref.length) : root,
          count: rootCounts.get(root) ?? 0,
          sigs,
          hiddenSigCount: Math.max(0, sigsAll.length - sigs.length)
        };
      })
      .sort((a, b) => b.count - a.count || a.root.localeCompare(b.root));

    const MAX_ROOTS = 6;
    const trimmed = rootGroups.slice(0, MAX_ROOTS);
    // If trimmed, keep the lexical order among the trimmed set to feel like Artifacts grouping.
    trimmed.sort((a, b) => a.root.localeCompare(b.root));
    return trimmed;
  }

  function families(): Family[] {
    const raw = toolUse?.['families'];
    if (!Array.isArray(raw)) return [];
    return raw
      .map((f) => {
        const family = String(f?.family ?? '');
        const count = Number(f?.count ?? 0);
        const unique_variants = typeof f?.unique_variants === 'number' ? f.unique_variants : undefined;

        if (family === 'find') {
          const roots = aggregateFindVariants(asVariantArray(f?.variants));
          return { family, count, unique_variants, findRoots: roots ?? [] } satisfies Family;
        }

        if (family === 'cd') {
          const groups = aggregateCdDirGroups(f?.variants);
          return { family, count, unique_variants, dirGroups: groups, plain: [], trunks: [] } satisfies Family;
        }

        const agg = aggregateVariants(family, asVariantArray(f?.variants));
        return {
          family,
          count,
          unique_variants,
          trunks: agg ? agg.trunks.slice(0, 2).map((t) => ({ ...t, leaves: t.leaves.slice(0, 4) })) : [],
          plain: agg ? agg.plain.slice(0, 6) : []
        } satisfies Family;
      })
      .filter((f) => f.family)
      .sort((a, b) => b.count - a.count || a.family.localeCompare(b.family));
  }
</script>

<Section title="Tool Use" subtitle="Top command families (first pass).">
  {@const fs = families()}
  {#if fs.length}
    <div class="grid gap-3 md:grid-cols-2">
      {#each fs.slice(0, 8) as f (f.family)}
        <div class="rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
          <div class="flex items-baseline justify-between gap-4">
            <div class="font-mono text-sm text-ink-950">{f.family}</div>
            <div class="font-mono text-xs text-ink-800/70">{f.count.toLocaleString()} calls</div>
          </div>

          {#if f.findRoots && f.findRoots.length}
            <div class="mt-3 space-y-3">
              {#each f.findRoots as g (g.root)}
                <div class="rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
                  <div class="flex items-baseline justify-between gap-4">
                    <div class="font-mono text-xs text-ink-900/80 break-all">{g.root}</div>
                    <div class="font-mono text-[11px] text-ink-800/70">{g.count}</div>
                  </div>
                  <ul class="mt-2 space-y-1">
                    {#each g.sigs as s (s.key)}
                      <li class="flex items-start justify-between gap-4">
                        <div class="font-mono text-[11px] text-ink-800/70 break-words" title={s.example ?? s.label}>{s.label}</div>
                        <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{s.count}</div>
                      </li>
                    {/each}
                    {#if g.hiddenSigCount}
                      <li class="text-[11px] text-ink-800/50">… +{g.hiddenSigCount} more</li>
                    {/if}
                  </ul>
                </div>
              {/each}
            </div>
          {:else}
            {#if f.dirGroups && f.dirGroups.length}
              <div class="mt-3 space-y-3">
                {#each f.dirGroups as g (g.key)}
                  <div class="rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
                    <div class="flex items-baseline justify-between gap-4">
                      <div class="font-mono text-xs text-ink-900/80 break-all" title={g.key}>in {g.label}</div>
                      <div class="font-mono text-[11px] text-ink-800/70">{g.count}</div>
                    </div>
                    <ul class="mt-2 space-y-1">
                      {#each g.leaves as v (v.key)}
                        <li class="flex items-start justify-between gap-4">
                          <div class="font-mono text-[11px] text-ink-800/70 break-words" title={v.example ?? v.label}>{v.label}</div>
                          <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{v.count}</div>
                        </li>
                      {/each}
                      {#if g.hiddenLeafCount}
                        <li class="text-[11px] text-ink-800/50">… +{g.hiddenLeafCount} more</li>
                      {/if}
                    </ul>
                  </div>
                {/each}
              </div>
            {/if}

            {#if f.plain && f.plain.length}
              <ul class="mt-3 space-y-1">
                {#each f.plain as v (v.key)}
                  <li class="flex items-start justify-between gap-4">
                    <div class="font-mono text-[11px] text-ink-800/70 break-words" title={v.example ?? v.label}>{v.label}</div>
                    <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{v.count}</div>
                  </li>
                {/each}
              </ul>
            {/if}
          {/if}
          {#if f.trunks && f.trunks.length}
            <div class="mt-3 space-y-2">
              {#each f.trunks as t (t.trunk)}
                <div class="rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
                  <div class="flex items-baseline justify-between gap-4">
                    <div class="font-mono text-xs text-ink-900/80">{t.trunk}</div>
                    <div class="font-mono text-[11px] text-ink-800/70">{t.count}</div>
                  </div>
                  <ul class="mt-2 space-y-1">
                    {#each t.leaves as v (v.key)}
                      <li class="flex items-start justify-between gap-4">
                        <div class="font-mono text-[11px] text-ink-800/70 break-words" title={v.example ?? v.label}>{v.label}</div>
                        <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{v.count}</div>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-sm text-ink-800/70">No tool use summary.</div>
  {/if}
</Section>
