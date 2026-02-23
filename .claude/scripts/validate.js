#!/usr/bin/env node
/**
 * validate.js — MeKB Frontmatter Validator
 *
 * Validates frontmatter schemas against MeKB's type system.
 *
 * Usage:
 *   node .claude/scripts/validate.js [path]
 *   node .claude/scripts/validate.js --type Concept
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_ROOT = path.resolve(__dirname, "../..");

// MeKB required fields by type
const SCHEMAS = {
  Daily:       ["type", "title", "created"],
  Note:        ["type", "title", "created", "tags"],
  Concept:     ["type", "title", "created", "tags"],
  Task:        ["type", "title", "created", "status"],
  Project:     ["type", "title", "created", "status"],
  Meeting:     ["type", "title", "created"],
  Person:      ["type", "title"],
  Resource:    ["type", "title", "created", "tags"],
  Decision:    ["type", "title", "created"],
  ActionItem:  ["type", "title", "created", "status"],
  Interaction: ["type", "title", "created"],
};

const filterType = process.argv.find(a => a.startsWith("--type="))?.split("=")[1]
  || (process.argv.indexOf("--type") !== -1 ? process.argv[process.argv.indexOf("--type") + 1] : null);

let errors = 0;
let checked = 0;

function validate(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  if (!content.startsWith("---")) return;

  const fmEnd = content.indexOf("---", 4);
  if (fmEnd === -1) return;

  const fm = content.slice(4, fmEnd);
  const typeMatch = fm.match(/^type:\s*(.+)$/m);
  if (!typeMatch) return;

  const noteType = typeMatch[1].trim();
  if (filterType && noteType !== filterType) return;

  const schema = SCHEMAS[noteType];
  if (!schema) return;

  checked++;
  const relPath = path.relative(VAULT_ROOT, filePath);

  for (const field of schema) {
    const re = new RegExp(`^${field}:`, "m");
    if (!re.test(fm)) {
      errors++;
      console.log(`${relPath}: missing required field '${field}' for type ${noteType}`);
    }
  }
}

function scanDir(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith(".") && entry.name !== "node_modules") {
      scanDir(fullPath);
    } else if (entry.name.endsWith(".md")) {
      validate(fullPath);
    }
  }
}

const target = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : VAULT_ROOT;
if (fs.statSync(target).isDirectory()) {
  scanDir(target);
} else {
  validate(target);
}

console.log(`Validated ${checked} notes, ${errors} error(s)`);
process.exit(errors > 0 ? 1 : 0);
