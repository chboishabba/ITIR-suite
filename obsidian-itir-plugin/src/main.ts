import {
  App,
  ItemView,
  Notice,
  Plugin,
  PluginSettingTab,
  requestUrl,
  Setting,
  TFile,
  WorkspaceLeaf,
  normalizePath,
} from "obsidian";

const VIEW_TYPE_ITIR_STATUS = "itir-observer-status";

type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
type JsonObject = { [key: string]: JsonValue };

interface ItirSettings {
  generatedFolder: string;
  observerBundlePath: string;
  mcpBundlePathOverride: string;
  mcpCallEndpoint: string;
  questionLimit: number;
  maxNotes: number;
  includeDisplayFields: boolean;
}

interface ItirRunState {
  lastExportedAt?: string;
  lastBundlePath?: string;
  lastMcpBundlePath?: string;
  status?: JsonObject;
  openQuestions?: JsonObject;
  obsidianScan?: JsonObject;
  lastError?: string;
}

interface ObserverRecord {
  schema_version: "obsidian.note_observer_bundle.v1";
  event: "note_observed";
  note_id_hash: string;
  vault_id_hash: string;
  authority_class: "observer";
  markdown: string;
  excerpt_line_count: number;
  plugin_local: {
    source: "obsidian-itir-plugin";
    path_hash: string;
  };
}

const DEFAULT_SETTINGS: ItirSettings = {
  generatedFolder: "ITIR Projections",
  observerBundlePath: "ITIR Projections/_bundles/obsidian-observer-bundle.json",
  mcpBundlePathOverride: "",
  mcpCallEndpoint: "",
  questionLimit: 100,
  maxNotes: 200,
  includeDisplayFields: false,
};

export default class ItirObserverPlugin extends Plugin {
  settings: ItirSettings = { ...DEFAULT_SETTINGS };
  runState: ItirRunState = {};

  async onload(): Promise<void> {
    await this.loadSettings();

    this.registerView(VIEW_TYPE_ITIR_STATUS, (leaf) => new ItirStatusView(leaf, this));

    this.addRibbonIcon("network", "Open ITIR status", () => {
      void this.activateStatusView();
    });

    this.addCommand({
      id: "open-itir-status-pane",
      name: "Open ITIR status pane",
      callback: () => {
        void this.activateStatusView();
      },
    });

    this.addCommand({
      id: "export-observer-bundle",
      name: "Export observer bundle",
      callback: () => {
        void this.exportObserverBundleWithNotice();
      },
    });

    this.addCommand({
      id: "refresh-docstore-status",
      name: "Refresh ITIR docstore status",
      callback: () => {
        void this.refreshStatusProjection();
      },
    });

    this.addCommand({
      id: "refresh-open-questions",
      name: "Refresh ITIR open questions",
      callback: () => {
        void this.refreshOpenQuestionsProjection();
      },
    });

    this.addCommand({
      id: "scan-exported-observer-bundle",
      name: "Scan exported observer bundle",
      callback: () => {
        void this.refreshObsidianScanProjection();
      },
    });

    this.addCommand({
      id: "refresh-all-itir-projections",
      name: "Refresh all ITIR projections",
      callback: () => {
        void this.refreshAllProjections();
      },
    });

    this.addSettingTab(new ItirSettingTab(this.app, this));
  }

  onunload(): void {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_ITIR_STATUS);
  }

  async loadSettings(): Promise<void> {
    const loaded = (await this.loadData()) as Partial<ItirSettings> | null;
    this.settings = { ...DEFAULT_SETTINGS, ...loaded };
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }

  async activateStatusView(): Promise<void> {
    const leaves = this.app.workspace.getLeavesOfType(VIEW_TYPE_ITIR_STATUS);
    if (leaves.length > 0) {
      this.app.workspace.revealLeaf(leaves[0]);
      return;
    }

    const leaf = this.app.workspace.getRightLeaf(false);
    if (!leaf) {
      new Notice("Unable to open ITIR status pane.");
      return;
    }
    await leaf.setViewState({ type: VIEW_TYPE_ITIR_STATUS, active: true });
    this.app.workspace.revealLeaf(leaf);
  }

  async exportObserverBundleWithNotice(): Promise<void> {
    try {
      const result = await this.exportObserverBundle();
      new Notice(`Exported ${result.records.length} observer records.`);
      this.refreshStatusViews();
    } catch (error) {
      this.recordError(error);
    }
  }

  async refreshAllProjections(): Promise<void> {
    await this.refreshStatusProjection();
    await this.refreshOpenQuestionsProjection();
    await this.refreshObsidianScanProjection();
  }

  async refreshStatusProjection(): Promise<void> {
    try {
      const payload = await this.payloadWithFreshBundle();
      const result = await this.callMcpTool("itir.docstore.status", payload);
      this.runState.status = result;
      await this.writeProjection("docstore-status.md", renderStatusProjection(result, this.runState));
      new Notice("ITIR docstore status refreshed.");
      this.refreshStatusViews();
    } catch (error) {
      this.recordError(error);
    }
  }

  async refreshOpenQuestionsProjection(): Promise<void> {
    try {
      const payload = await this.payloadWithFreshBundle();
      const result = await this.callMcpTool("itir.docstore.open_questions", payload);
      this.runState.openQuestions = result;
      await this.writeProjection("open-questions.md", renderQuestionsProjection(result, this.runState));
      new Notice("ITIR open questions refreshed.");
      this.refreshStatusViews();
    } catch (error) {
      this.recordError(error);
    }
  }

  async refreshObsidianScanProjection(): Promise<void> {
    try {
      const payload = await this.payloadWithFreshBundle();
      const result = await this.callMcpTool("itir.obsidian.vault_scan", payload);
      this.runState.obsidianScan = result;
      await this.writeProjection("obsidian-scan.md", renderScanProjection(result, this.runState));
      new Notice("Obsidian observer scan refreshed.");
      this.refreshStatusViews();
    } catch (error) {
      this.recordError(error);
    }
  }

  async payloadWithFreshBundle(): Promise<JsonObject> {
    const exported = await this.exportObserverBundle();
    const bundlePath = exported.mcpBundlePath;
    const payload: JsonObject = {
      bundle_path: bundlePath,
      bundle_paths: [bundlePath],
      limit: this.settings.questionLimit,
      question_limit: this.settings.questionLimit,
      max_notes: this.settings.maxNotes,
      include_display_fields: this.settings.includeDisplayFields,
    };
    return payload;
  }

  async callMcpTool(toolName: string, payload: JsonObject): Promise<JsonObject> {
    const endpoint = this.settings.mcpCallEndpoint.trim();
    if (!endpoint) {
      throw new Error("Configure an ITIR MCP call endpoint before refreshing MCP-backed projections.");
    }

    const url = endpoint.includes("{tool}") ? endpoint.replace("{tool}", encodeURIComponent(toolName)) : endpoint;
    const response = await requestUrl({
      url,
      method: "POST",
      contentType: "application/json",
      body: JSON.stringify({
        tool: toolName,
        name: toolName,
        arguments: payload,
        payload,
      }),
    });

    const body = parseJsonObject(response.text);
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`MCP endpoint returned HTTP ${response.status}: ${response.text.slice(0, 300)}`);
    }

    if (body.ok === false) {
      const message = typeof body.error === "object" && body.error && "message" in body.error
        ? String((body.error as { message?: JsonValue }).message)
        : "MCP call failed";
      throw new Error(message);
    }

    if (body.ok === true && isJsonObject(body.result)) {
      return body.result;
    }
    return body;
  }

  async exportObserverBundle(): Promise<{ records: ObserverRecord[]; vaultPath: string; mcpBundlePath: string }> {
    const vaultIdHash = await this.vaultIdHash();
    const generatedFolder = normalizePath(this.settings.generatedFolder);
    const files = this.app.vault
      .getMarkdownFiles()
      .filter((file) => !isGeneratedPath(file.path, generatedFolder))
      .slice(0, this.settings.maxNotes);

    const records: ObserverRecord[] = [];
    for (const file of files) {
      const markdown = await this.app.vault.cachedRead(file);
      const excerpt = extractPressureExcerpt(markdown);
      if (!excerpt.trim()) {
        continue;
      }
      const noteIdHash = await hashText(`obsidian-note:${vaultIdHash}:${file.path}`);
      const pathHash = await hashText(`obsidian-path:${file.path}`);
      records.push({
        schema_version: "obsidian.note_observer_bundle.v1",
        event: "note_observed",
        note_id_hash: noteIdHash,
        vault_id_hash: vaultIdHash,
        authority_class: "observer",
        markdown: excerpt,
        excerpt_line_count: excerpt.split("\n").filter((line) => line.trim()).length,
        plugin_local: {
          source: "obsidian-itir-plugin",
          path_hash: pathHash,
        },
      });
    }

    const vaultPath = normalizePath(this.settings.observerBundlePath);
    await this.writeVaultFile(vaultPath, `${JSON.stringify({ schema_version: "obsidian.itir_observer_bundle.v1", records }, null, 2)}\n`);

    const mcpBundlePath = this.resolveMcpBundlePath(vaultPath);
    this.runState.lastExportedAt = new Date().toISOString();
    this.runState.lastBundlePath = vaultPath;
    this.runState.lastMcpBundlePath = mcpBundlePath;
    return { records, vaultPath, mcpBundlePath };
  }

  async writeProjection(name: string, content: string): Promise<void> {
    const folder = normalizePath(this.settings.generatedFolder);
    await this.ensureFolder(folder);
    await this.writeVaultFile(normalizePath(`${folder}/${name}`), content);
  }

  async writeVaultFile(path: string, content: string): Promise<void> {
    const normalized = normalizePath(path);
    const parent = normalized.split("/").slice(0, -1).join("/");
    if (parent) {
      await this.ensureFolder(parent);
    }

    const existing = this.app.vault.getAbstractFileByPath(normalized);
    if (existing instanceof TFile) {
      await this.app.vault.modify(existing, content);
      return;
    }
    await this.app.vault.create(normalized, content);
  }

  async ensureFolder(path: string): Promise<void> {
    const normalized = normalizePath(path);
    if (!normalized || this.app.vault.getAbstractFileByPath(normalized)) {
      return;
    }

    const parts = normalized.split("/");
    let active = "";
    for (const part of parts) {
      active = active ? `${active}/${part}` : part;
      if (!this.app.vault.getAbstractFileByPath(active)) {
        await this.app.vault.createFolder(active);
      }
    }
  }

  resolveMcpBundlePath(vaultPath: string): string {
    const override = this.settings.mcpBundlePathOverride.trim();
    if (override) {
      return override;
    }
    const basePath = getVaultBasePath(this.app);
    return basePath ? normalizeSystemPath(`${basePath}/${vaultPath}`) : vaultPath;
  }

  async vaultIdHash(): Promise<string> {
    const basePath = getVaultBasePath(this.app);
    const raw = basePath ? `obsidian-vault:${basePath}` : `obsidian-vault:${this.app.vault.getName()}`;
    return hashText(raw);
  }

  recordError(error: unknown): void {
    const message = error instanceof Error ? error.message : String(error);
    this.runState.lastError = message;
    new Notice(`ITIR: ${message}`);
    this.refreshStatusViews();
  }

  refreshStatusViews(): void {
    for (const leaf of this.app.workspace.getLeavesOfType(VIEW_TYPE_ITIR_STATUS)) {
      const view = leaf.view;
      if (view instanceof ItirStatusView) {
        view.render();
      }
    }
  }
}

class ItirStatusView extends ItemView {
  constructor(leaf: WorkspaceLeaf, private readonly plugin: ItirObserverPlugin) {
    super(leaf);
  }

  getViewType(): string {
    return VIEW_TYPE_ITIR_STATUS;
  }

  getDisplayText(): string {
    return "ITIR";
  }

  getIcon(): string {
    return "network";
  }

  async onOpen(): Promise<void> {
    this.render();
  }

  render(): void {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.addClass("itir-status-view");

    contentEl.createEl("h2", { text: "ITIR" });

    const actions = contentEl.createDiv({ cls: "itir-actions" });
    this.addButton(actions, "Export", () => this.plugin.exportObserverBundleWithNotice());
    this.addButton(actions, "Status", () => this.plugin.refreshStatusProjection());
    this.addButton(actions, "Questions", () => this.plugin.refreshOpenQuestionsProjection());
    this.addButton(actions, "Scan", () => this.plugin.refreshObsidianScanProjection());
    this.addButton(actions, "All", () => this.plugin.refreshAllProjections());

    const state = this.plugin.runState;
    this.renderMeta(contentEl, state);
    this.renderCounts(contentEl, "Docstore Status", state.status);
    this.renderCounts(contentEl, "Open Questions", state.openQuestions);
    this.renderCounts(contentEl, "Obsidian Scan", state.obsidianScan);

    if (state.lastError) {
      contentEl.createEl("h3", { text: "Last Error" });
      contentEl.createEl("pre", { text: state.lastError });
    }
  }

  private addButton(parent: HTMLElement, text: string, action: () => Promise<void>): void {
    const button = parent.createEl("button", { text });
    button.addEventListener("click", () => {
      void action();
    });
  }

  private renderMeta(parent: HTMLElement, state: ItirRunState): void {
    const table = parent.createEl("table", { cls: "itir-meta" });
    renderRow(table, "Generated folder", this.plugin.settings.generatedFolder);
    renderRow(table, "Vault bundle", state.lastBundlePath ?? this.plugin.settings.observerBundlePath);
    renderRow(table, "MCP bundle", state.lastMcpBundlePath ?? this.plugin.resolveMcpBundlePath(this.plugin.settings.observerBundlePath));
    renderRow(table, "Last export", state.lastExportedAt ?? "never");
  }

  private renderCounts(parent: HTMLElement, title: string, payload: JsonObject | undefined): void {
    parent.createEl("h3", { text: title });
    if (!payload) {
      parent.createEl("p", { text: "No result in this session." });
      return;
    }
    const table = parent.createEl("table", { cls: "itir-meta" });
    const counts = isJsonObject(payload.counts) ? payload.counts : undefined;
    renderRow(table, "Version", stringValue(payload.version));
    renderRow(table, "Authority", stringValue(payload.authority_class));
    renderRow(table, "Items", String(arrayValue(payload.candidates).length || arrayValue(payload.questions).length || arrayValue(payload.latest_artifacts).length));
    if (counts) {
      renderRow(table, "Counts", JSON.stringify(counts));
    }
  }
}

class ItirSettingTab extends PluginSettingTab {
  constructor(app: App, private readonly plugin: ItirObserverPlugin) {
    super(app, plugin);
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "ITIR Observer" });

    new Setting(containerEl)
      .setName("Generated folder")
      .setDesc("Replaceable Markdown projections are written here.")
      .addText((text) =>
        text
          .setPlaceholder(DEFAULT_SETTINGS.generatedFolder)
          .setValue(this.plugin.settings.generatedFolder)
          .onChange(async (value) => {
            this.plugin.settings.generatedFolder = normalizePath(value.trim() || DEFAULT_SETTINGS.generatedFolder);
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Observer bundle path")
      .setDesc("Vault-relative JSON bundle path exported for ITIR MCP.")
      .addText((text) =>
        text
          .setPlaceholder(DEFAULT_SETTINGS.observerBundlePath)
          .setValue(this.plugin.settings.observerBundlePath)
          .onChange(async (value) => {
            this.plugin.settings.observerBundlePath = normalizePath(value.trim() || DEFAULT_SETTINGS.observerBundlePath);
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("MCP bundle path override")
      .setDesc("Optional absolute path as seen by the ITIR MCP process.")
      .addText((text) =>
        text
          .setPlaceholder("/absolute/path/to/obsidian-observer-bundle.json")
          .setValue(this.plugin.settings.mcpBundlePathOverride)
          .onChange(async (value) => {
            this.plugin.settings.mcpBundlePathOverride = value.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("MCP call endpoint")
      .setDesc("Optional HTTP adapter endpoint. Use {tool} in the URL if the adapter routes by tool name.")
      .addText((text) =>
        text
          .setPlaceholder("http://127.0.0.1:8787/call")
          .setValue(this.plugin.settings.mcpCallEndpoint)
          .onChange(async (value) => {
            this.plugin.settings.mcpCallEndpoint = value.trim();
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Question limit")
      .addSlider((slider) =>
        slider
          .setLimits(10, 500, 10)
          .setValue(this.plugin.settings.questionLimit)
          .setDynamicTooltip()
          .onChange(async (value) => {
            this.plugin.settings.questionLimit = value;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Max notes")
      .addSlider((slider) =>
        slider
          .setLimits(25, 1000, 25)
          .setValue(this.plugin.settings.maxNotes)
          .setDynamicTooltip()
          .onChange(async (value) => {
            this.plugin.settings.maxNotes = value;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Include display fields")
      .setDesc("Passes include_display_fields to ITIR MCP scan calls.")
      .addToggle((toggle) =>
        toggle
          .setValue(this.plugin.settings.includeDisplayFields)
          .onChange(async (value) => {
            this.plugin.settings.includeDisplayFields = value;
            await this.plugin.saveSettings();
          }),
      );
  }
}

function extractPressureExcerpt(markdown: string): string {
  const out: string[] = [];
  let activeHeading = "";
  let activeKind = "";

  for (const rawLine of markdownLines(markdown)) {
    const heading = parseHeading(rawLine);
    if (heading) {
      activeHeading = heading.text;
      activeKind = pressureKindForHeading(heading.text);
      if (activeKind && out[out.length - 1] !== `## ${heading.text}`) {
        out.push(`## ${heading.text}`);
      }
      continue;
    }

    const stripped = rawLine.trim();
    if (!stripped) {
      continue;
    }

    const queryKind = pressureKindForQueryLine(stripped);
    const shouldCapture = Boolean(queryKind) || Boolean(activeKind && isBoundedHintLine(stripped));
    if (!shouldCapture) {
      continue;
    }

    if (queryKind && !activeKind && activeHeading !== "Candidate hints") {
      activeHeading = "Candidate hints";
      out.push("## Candidate hints");
    }
    out.push(stripMarkdownMarker(stripped));
    if (out.length >= 50) {
      break;
    }
  }

  return out.join("\n").trim();
}

function parseHeading(line: string): { level: number; text: string } | null {
  const stripped = line.trim();
  let level = 0;
  while (level < stripped.length && stripped[level] === "#") {
    level += 1;
  }
  if (level < 1 || level > 6 || stripped[level] !== " ") {
    return null;
  }
  const text = stripped.slice(level + 1).trim();
  return text ? { level, text } : null;
}

function pressureKindForHeading(heading: string): string {
  const normalized = normalizeWords(heading);
  const tokens = ["open question", "open questions", "question", "questions", "blocker", "blockers", "gap", "gaps", "assumption", "assumptions"];
  return tokens.some((token) => normalized.includes(token)) ? normalized : "";
}

function pressureKindForQueryLine(line: string): string {
  const lowered = line.toLowerCase();
  if (lowered.includes(":itir-query:") || lowered.includes(":sl-query:")) {
    return "query_intent";
  }
  if (lowered.endsWith("?") && (lowered.includes("todo") || lowered.includes("question"))) {
    return "open_question";
  }
  return "";
}

function isBoundedHintLine(line: string): boolean {
  return startsWithListMarker(line) || line.endsWith("?") || line.includes(":itir-query:") || line.includes(":sl-query:");
}

function stripMarkdownMarker(line: string): string {
  const stripped = line.trim();
  if (!startsWithListMarker(stripped)) {
    return stripped;
  }
  let rest = stripped.slice(2).trim();
  if (rest.length >= 4 && rest[0] === "[" && rest[2] === "]" && rest[3] === " ") {
    const marker = rest[1];
    if (marker === " " || marker === "x" || marker === "X") {
      rest = rest.slice(4).trim();
    }
  }
  return rest;
}

function renderStatusProjection(payload: JsonObject, state: ItirRunState): string {
  return renderProjectionHeader("ITIR Docstore Status", state) + fencedJson(payload);
}

function renderQuestionsProjection(payload: JsonObject, state: ItirRunState): string {
  const questions = arrayValue(payload.questions).length ? arrayValue(payload.questions) : arrayValue(payload.candidates);
  const rows = questions.map((item) => {
    if (!isJsonObject(item)) {
      return "";
    }
    return `| ${escapeTable(stringValue(item.pressure_kind))} | ${escapeTable(stringValue(item.authority_class))} | ${escapeTable(stringValue(item.promotion_level))} | ${escapeTable(questionText(item))} |`;
  }).filter(Boolean);

  return [
    renderProjectionHeader("ITIR Open Questions", state),
    "| Kind | Authority | Promotion | Text |",
    "| --- | --- | --- | --- |",
    ...rows,
    "",
    fencedJson(payload),
  ].join("\n");
}

function renderScanProjection(payload: JsonObject, state: ItirRunState): string {
  const candidates = arrayValue(payload.candidates);
  const rows = candidates.map((item) => {
    if (!isJsonObject(item)) {
      return "";
    }
    return `| ${escapeTable(stringValue(item.pressure_kind))} | ${escapeTable(stringValue(item.promotion_level))} | ${escapeTable(questionText(item))} |`;
  }).filter(Boolean);

  return [
    renderProjectionHeader("ITIR Obsidian Scan", state),
    "| Kind | Promotion | Text |",
    "| --- | --- | --- |",
    ...rows,
    "",
    fencedJson(payload),
  ].join("\n");
}

function renderProjectionHeader(title: string, state: ItirRunState): string {
  return [
    "---",
    "itir_projection: replaceable",
    "authority_class: observer",
    `generated_at: ${new Date().toISOString()}`,
    "---",
    "",
    `# ${title}`,
    "",
    `Bundle: ${state.lastMcpBundlePath ?? state.lastBundlePath ?? "not exported"}`,
    "",
  ].join("\n");
}

function fencedJson(payload: JsonObject): string {
  return `\n\`\`\`json\n${JSON.stringify(payload, null, 2)}\n\`\`\`\n`;
}

function renderRow(table: HTMLTableElement, label: string, value: string): void {
  const row = table.createEl("tr");
  row.createEl("th", { text: label });
  row.createEl("td", { text: value });
}

function isGeneratedPath(path: string, generatedFolder: string): boolean {
  const normalizedPath = normalizePath(path);
  const normalizedFolder = normalizePath(generatedFolder);
  return normalizedPath === normalizedFolder || normalizedPath.startsWith(`${normalizedFolder}/`);
}

function getVaultBasePath(app: App): string | null {
  const adapter = app.vault.adapter as unknown as { getBasePath?: () => string };
  return typeof adapter.getBasePath === "function" ? adapter.getBasePath() : null;
}

function normalizeSystemPath(path: string): string {
  return path.split("\\").join("/");
}

async function hashText(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return `sha256:${Array.from(new Uint8Array(digest)).map((byte) => byte.toString(16).padStart(2, "0")).join("")}`;
}

function parseJsonObject(text: string): JsonObject {
  const value = JSON.parse(text) as JsonValue;
  if (!isJsonObject(value)) {
    throw new Error("MCP endpoint did not return a JSON object.");
  }
  return value;
}

function isJsonObject(value: JsonValue | undefined): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function arrayValue(value: JsonValue | undefined): JsonValue[] {
  return Array.isArray(value) ? value : [];
}

function stringValue(value: JsonValue | undefined): string {
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return "";
}

function escapeTable(value: string): string {
  return markdownLines(value.split("|").join("\\|")).join("<br>");
}

function markdownLines(text: string): string[] {
  return text.split("\r\n").join("\n").split("\r").join("\n").split("\n");
}

function normalizeWords(value: string): string {
  const words: string[] = [];
  let active = "";
  for (const char of value.toLowerCase()) {
    if ((char >= "a" && char <= "z") || (char >= "0" && char <= "9")) {
      active += char;
      continue;
    }
    if (active) {
      words.push(active);
      active = "";
    }
  }
  if (active) {
    words.push(active);
  }
  return words.join(" ");
}

function startsWithListMarker(line: string): boolean {
  const stripped = line.trim();
  return stripped.length >= 3 && (stripped[0] === "-" || stripped[0] === "*" || stripped[0] === "+") && stripped[1] === " ";
}

function questionText(item: JsonObject): string {
  return stringValue(item.question_text_or_reason) || stringValue(item.text);
}
