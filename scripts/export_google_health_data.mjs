#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const DEFAULT_PACKAGE_DIST =
  "/home/c/.npm/_npx/bb4af3b48c50ef84/node_modules/google-health-mcp-unofficial/dist";

const DAILY_DEFAULT_TYPES = [
  "steps",
  "distance",
  "total-calories",
  "active-minutes",
  "active-zone-minutes",
];

const POINTS_DEFAULT_TYPES = [
  "steps",
  "distance",
  "heart-rate",
  "activity-level",
  "exercise",
];

const DATA_TYPE_SET_ALIASES = new Set(["all", "all-daily", "all-points"]);

function parseArgs(argv) {
  const args = {
    mode: "daily",
    startDate: offsetDate(-30),
    endDate: offsetDate(0),
    startTime: undefined,
    endTime: undefined,
    dataTypes: undefined,
    outDir: "exports/google_health",
    pageSize: 100,
    maxPages: 100,
    dataSourceFamily: "users/me/dataSourceFamilies/all-sources",
    packageDist: process.env.GOOGLE_HEALTH_MCP_DIST || DEFAULT_PACKAGE_DIST,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = argv[i + 1];
    if (arg === "--mode") {
      args.mode = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--start-date") {
      args.startDate = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--end-date") {
      args.endDate = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--start-time") {
      args.startTime = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--end-time") {
      args.endTime = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--data-types") {
      const rawDataTypes = requiredValue(arg, next)
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      args.dataTypes = rawDataTypes.length === 1 && DATA_TYPE_SET_ALIASES.has(rawDataTypes[0])
        ? rawDataTypes[0]
        : rawDataTypes;
      i += 1;
    } else if (arg === "--out-dir") {
      args.outDir = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--page-size") {
      args.pageSize = Number(requiredValue(arg, next));
      i += 1;
    } else if (arg === "--max-pages") {
      args.maxPages = Number(requiredValue(arg, next));
      i += 1;
    } else if (arg === "--data-source-family") {
      args.dataSourceFamily = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--package-dist") {
      args.packageDist = requiredValue(arg, next);
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!["daily", "points"].includes(args.mode)) {
    throw new Error("--mode must be daily or points");
  }
  if (!Number.isInteger(args.pageSize) || args.pageSize < 1) {
    throw new Error("--page-size must be a positive integer");
  }
  if (!Number.isInteger(args.maxPages) || args.maxPages < 1) {
    throw new Error("--max-pages must be a positive integer");
  }
  return args;
}

function requiredValue(flag, value) {
  if (!value || value.startsWith("--")) {
    throw new Error(`Missing value for ${flag}`);
  }
  return value;
}

function offsetDate(offsetDays) {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

function defaultStartTime(startDate) {
  return `${startDate}T00:00:00Z`;
}

function defaultEndTime(endDate) {
  return `${endDate}T00:00:00Z`;
}

async function importFromDist(dist, relativePath) {
  const url = pathToFileURL(resolve(dist, relativePath)).href;
  return import(url);
}

function dateFromCivil(point) {
  const date = point?.civilStartTime?.date;
  if (!date) return "";
  return [
    String(date.year).padStart(4, "0"),
    String(date.month).padStart(2, "0"),
    String(date.day).padStart(2, "0"),
  ].join("-");
}

function flattenObject(value, prefix = "", out = {}) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      flattenObject(item, `${prefix}${prefix ? "." : ""}${index}`, out);
    });
    return out;
  }
  if (value && typeof value === "object") {
    for (const [key, child] of Object.entries(value)) {
      flattenObject(child, `${prefix}${prefix ? "." : ""}${key}`, out);
    }
    return out;
  }
  out[prefix] = value;
  return out;
}

function sanitizeCell(value) {
  if (value === undefined || value === null) return "";
  return String(value).replace(/\t/g, " ").replace(/\r?\n/g, " ");
}

function writeTsv(path, rows) {
  if (!rows.length) {
    writeFileSync(path, "", "utf8");
    return;
  }
  const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  const lines = [
    columns.join("\t"),
    ...rows.map((row) => columns.map((column) => sanitizeCell(row[column])).join("\t")),
  ];
  writeFileSync(path, `${lines.join("\n")}\n`, "utf8");
}

function dailyRow(date, byType) {
  const row = { date };
  const steps = byType.steps?.steps?.countSum;
  const distanceMm = byType.distance?.distance?.millimetersSum;
  const calories = byType["total-calories"]?.totalCalories?.kcalSum;
  const active = byType["active-minutes"]?.activeMinutes?.activeMinutesRollupByActivityLevel || [];
  const zones = byType["active-zone-minutes"]?.activeZoneMinutes;

  if (steps !== undefined) row.steps = Number(steps);
  if (distanceMm !== undefined) row.distance_km = Number((Number(distanceMm) / 1_000_000).toFixed(3));
  if (calories !== undefined) row.total_calories_kcal = Number(Number(calories).toFixed(1));
  for (const item of active) {
    const key = `${String(item.activityLevel || "unknown").toLowerCase()}_minutes`;
    row[key] = Number(item.activeMinutesSum || 0);
  }
  if (zones?.sumInFatBurnHeartZone !== undefined) {
    row.fat_burn_zone_minutes = Number(zones.sumInFatBurnHeartZone);
  }
  if (zones?.sumInCardioHeartZone !== undefined) {
    row.cardio_zone_minutes = Number(zones.sumInCardioHeartZone);
  }
  if (zones?.sumInPeakHeartZone !== undefined) {
    row.peak_zone_minutes = Number(zones.sumInPeakHeartZone);
  }
  for (const [dataType, point] of Object.entries(byType)) {
    const flattened = flattenObject(point);
    for (const [key, value] of Object.entries(flattened)) {
      if (!key) continue;
      const column = `${dataType}.${key}`;
      if (row[column] === undefined) row[column] = value;
    }
  }
  return row;
}

function filterFor(catalogEntry, startTime, endTime) {
  const slug = catalogEntry.slug;
  const filterName = slug.replaceAll("-", "_");
  if (catalogEntry.kind === "Daily") {
    return `${filterName}.date >= "${startTime.slice(0, 10)}" AND ${filterName}.date < "${endTime.slice(0, 10)}"`;
  }
  if (catalogEntry.kind === "Sample") {
    return `${filterName}.sample_time.physical_time >= "${startTime}" AND ${filterName}.sample_time.physical_time < "${endTime}"`;
  }
  if (slug === "sleep") {
    return `${filterName}.interval.civil_end_time >= "${startTime}" AND ${filterName}.interval.civil_end_time < "${endTime}"`;
  }
  if (slug === "electrocardiogram") {
    return `${filterName}.interval.start_time >= "${startTime}" AND ${filterName}.interval.start_time < "${endTime}"`;
  }
  if (slug === "exercise") {
    return undefined;
  }
  return `${filterName}.interval.start_time >= "${startTime}" AND ${filterName}.interval.start_time < "${endTime}"`;
}

async function exportDaily(client, dataTypes, args) {
  const raw = {};
  const byDate = new Map();
  for (const dataType of dataTypes) {
    try {
      const responses = [];
      for (const [chunkStart, chunkEnd] of dailyChunks(args.startDate, args.endDate)) {
        let pageToken;
        for (let page = 0; page < args.maxPages; page += 1) {
          const response = await client.dailyRollup({
            dataType,
            startDate: chunkStart,
            endDate: chunkEnd,
            windowSizeDays: 1,
            pageSize: Math.max(1, daysBetween(chunkStart, chunkEnd)),
            pageToken,
            dataSourceFamily: args.dataSourceFamily,
          });
          responses.push(response);
          for (const point of response.rollupDataPoints || []) {
            const date = dateFromCivil(point);
            if (!date) continue;
            const existing = byDate.get(date) || {};
            existing[dataType] = point;
            byDate.set(date, existing);
          }
          pageToken = response.nextPageToken;
          if (!pageToken) break;
        }
      }
      raw[dataType] = {
        pages: responses.length,
        rollupDataPoints: responses.flatMap((response) => response.rollupDataPoints || []),
        nextPageToken: responses.some((response) => response.nextPageToken),
      };
    } catch (error) {
      raw[dataType] = { error: error.message };
    }
  }
  const rows = [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, values]) => dailyRow(date, values));
  return { rows, raw };
}

async function exportPoints(client, catalog, dataTypes, args) {
  const rows = [];
  const raw = {};
  const startTime = args.startTime || defaultStartTime(args.startDate);
  const endTime = args.endTime || defaultEndTime(args.endDate);

  for (const dataType of dataTypes) {
    const entry = catalog.get(dataType);
    if (!entry) {
      raw[dataType] = { error: `Unknown data type: ${dataType}` };
      continue;
    }
    if (!entry.supports.includes("list") && !entry.supports.includes("reconcile")) {
      raw[dataType] = { error: `${dataType} does not support list or reconcile` };
      continue;
    }
    const baseQuery = {
      dataType,
      pageSize: args.pageSize,
      dataSourceFamily: args.dataSourceFamily,
    };
    const filter = filterFor(entry, startTime, endTime);
    if (filter) baseQuery.filter = filter;
    try {
      const responses = [];
      let pageToken;
      let index = 0;
      for (let page = 0; page < args.maxPages; page += 1) {
        const query = { ...baseQuery, pageToken };
        const response = entry.supports.includes("reconcile")
          ? await client.reconcileDataPoints(query)
          : await client.listDataPoints(query);
        responses.push(response);
        const points = extractPoints(response, dataType)
          .filter((point) => pointWithinRange(point, startTime, endTime));
        for (const point of points) {
          rows.push({
            data_type: dataType,
            index,
            ...flattenObject(point),
          });
          index += 1;
        }
        pageToken = response.nextPageToken;
        if (!pageToken) break;
      }
      raw[dataType] = {
        pages: responses.length,
        dataPoints: responses
          .flatMap((response) => extractPoints(response, dataType))
          .filter((point) => pointWithinRange(point, startTime, endTime)),
        nextPageToken: pageToken,
      };
    } catch (error) {
      raw[dataType] = { error: error.message, filter: baseQuery.filter };
    }
  }
  return { rows, raw };
}

function pointWithinRange(point, startTime, endTime) {
  const timestamp = pointTimestamp(point);
  if (!timestamp) return true;
  return timestamp >= startTime && timestamp < endTime;
}

function pointTimestamp(point) {
  const stack = [point];
  while (stack.length) {
    const current = stack.pop();
    if (!current || typeof current !== "object") continue;
    if (typeof current.physicalTime === "string") return current.physicalTime;
    if (typeof current.startTime === "string") return current.startTime;
    for (const value of Object.values(current)) {
      if (value && typeof value === "object") stack.push(value);
    }
  }
  return undefined;
}

function extractPoints(response, dataType) {
  return response.dataPoints
    || response.reconciledDataPoints
    || response[`${camel(dataType)}DataPoints`]
    || [];
}

function camel(slug) {
  return slug.replace(/-([a-z])/g, (_match, letter) => letter.toUpperCase());
}

function daysBetween(startDate, endDate) {
  const start = Date.parse(`${startDate}T00:00:00Z`);
  const end = Date.parse(`${endDate}T00:00:00Z`);
  return Math.max(1, Math.ceil((end - start) / 86_400_000));
}

function addDays(dateString, days) {
  const date = new Date(`${dateString}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function dailyChunks(startDate, endDate, maxDays = 14) {
  const chunks = [];
  let chunkStart = startDate;
  while (chunkStart < endDate) {
    const chunkEnd = minDate(addDays(chunkStart, maxDays), endDate);
    chunks.push([chunkStart, chunkEnd]);
    chunkStart = chunkEnd;
  }
  return chunks;
}

function minDate(a, b) {
  return a < b ? a : b;
}

function printHelp() {
  console.log(`Usage:
  node scripts/export_google_health_data.mjs [options]

Modes:
  --mode daily   Export daily rollups, best for Google Sheets summaries.
  --mode points  Export finer-grained interval/sample/session records.

Options:
  --start-date YYYY-MM-DD
  --end-date YYYY-MM-DD              Exclusive end date. Defaults to today.
  --start-time ISO_TIMESTAMP         Points mode only; defaults from start date.
  --end-time ISO_TIMESTAMP           Points mode only; defaults from end date.
  --data-types a,b,c                 Defaults depend on mode. Use all, all-daily, or all-points.
  --out-dir PATH                     Default: exports/google_health
  --page-size N                      Points mode page size. Default: 100.
  --max-pages N                      Max pages per data type. Default: 100.
  --data-source-family FAMILY        Default: users/me/dataSourceFamilies/all-sources
  --package-dist PATH                Override installed MCP dist path.

Examples:
  node scripts/export_google_health_data.mjs --mode daily --start-date 2026-08-10 --end-date 2026-09-09
  node scripts/export_google_health_data.mjs --mode points --data-types steps,distance,heart-rate --start-date 2026-09-01 --end-date 2026-09-09
  node scripts/export_google_health_data.mjs --mode daily --data-types all --start-date 2026-08-10 --end-date 2026-09-09
  node scripts/export_google_health_data.mjs --mode points --data-types all --start-date 2026-09-07 --end-date 2026-09-09
`);
}

function resolveDataTypes(selection, mode, catalogEntries) {
  if (selection === "all" || selection === "all-daily") {
    if (mode === "daily") {
      return catalogEntries
        .filter((entry) => entry.official_operations?.includes("dailyRollup"))
        .map((entry) => entry.slug);
    }
    if (selection === "all-daily") {
      throw new Error("--data-types all-daily can only be used with --mode daily");
    }
  }
  if (selection === "all" || selection === "all-points") {
    if (mode === "points") {
      return catalogEntries
        .filter((entry) => entry.supports.includes("list") || entry.supports.includes("reconcile"))
        .map((entry) => entry.slug);
    }
    if (selection === "all-points") {
      throw new Error("--data-types all-points can only be used with --mode points");
    }
  }
  if (Array.isArray(selection)) return selection;
  return mode === "daily" ? DAILY_DEFAULT_TYPES : POINTS_DEFAULT_TYPES;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [{ getConfig }, { GoogleHealthClient }, { buildDataTypeCatalog }] = await Promise.all([
    importFromDist(args.packageDist, "services/config.js"),
    importFromDist(args.packageDist, "services/google-health-client.js"),
    importFromDist(args.packageDist, "services/inventory.js"),
  ]);

  const config = getConfig();
  const client = new GoogleHealthClient(config);
  const catalogEntries = buildDataTypeCatalog().data_types;
  const catalog = new Map(catalogEntries.map((entry) => [entry.slug, entry]));
  const dataTypes = resolveDataTypes(args.dataTypes, args.mode, catalogEntries);

  const result = args.mode === "daily"
    ? await exportDaily(client, dataTypes, args)
    : await exportPoints(client, catalog, dataTypes, args);

  const outDir = resolve(args.outDir);
  mkdirSync(outDir, { recursive: true });
  const stem = `google_health_${args.mode}_${args.startDate}_to_${args.endDate}`;
  const jsonPath = resolve(outDir, `${stem}.json`);
  const tsvPath = resolve(outDir, `${stem}.tsv`);
  const payload = {
    source: "google-health-mcp-unofficial",
    privacy_note: "Uses authenticated local Google Health config/tokens; output excludes OAuth secrets.",
    mode: args.mode,
    data_types: dataTypes,
    start_date: args.startDate,
    end_date_exclusive: args.endDate,
    rows: result.rows,
    raw_by_data_type: result.raw,
  };
  writeFileSync(jsonPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  writeTsv(tsvPath, result.rows);
  console.log(JSON.stringify({ ok: true, rows: result.rows.length, json: jsonPath, tsv: tsvPath }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
