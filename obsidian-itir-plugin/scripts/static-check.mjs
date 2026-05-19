import { readFileSync } from "node:fs";

const jsonFiles = ["manifest.json", "package.json", "tsconfig.json"];

for (const file of jsonFiles) {
  JSON.parse(readFileSync(file, "utf8"));
}

const main = readFileSync("src/main.ts", "utf8");
for (const forbidden of ["git reset", "canonical identity from note titles", "canonical identity from tags"]) {
  if (main.includes(forbidden)) {
    throw new Error(`Forbidden text found in src/main.ts: ${forbidden}`);
  }
}

console.log("static checks passed");
