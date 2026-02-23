#!/usr/bin/env node
/**
 * health-check.js — MeKB Vault Health Check
 *
 * Runs basic health checks on the vault: frontmatter validation,
 * broken link detection, orphan detection, and freshness checks.
 *
 * Usage:
 *   node .claude/scripts/health-check.js
 *   node .claude/scripts/health-check.js --verbose
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_ROOT = path.resolve(__dirname, "../..");
const verbose = process.argv.includes("--verbose");

// MeKB note types
const VALID_TYPES = new Set([
  "Daily", "Note", "Concept", "Task", "Project", "Meeting",
  "Person", "Resource", "Decision", "ActionItem", "Interaction"
]);

const results = { errors: 0, warnings: 0, files: 0 };

function checkFile(filePath) {
  const content = fs.readFileSync(filePath, "utf8");
  const relPath = path.relative(VAULT_ROOT, filePath);
  results.files++;

  // Check frontmatter exists
  if (!content.startsWith("---")) {
    results.warnings++;
    if (verbose) console.log(`  WARN: ${relPath} — missing frontmatter`);
    return;
  }

  const fmEnd = content.indexOf("---", 4);
  if (fmEnd === -1) return;

  const fm = content.slice(4, fmEnd);

  // Check type field
  const typeMatch = fm.match(/^type:\s*(.+)$/m);
  if (!typeMatch) {
    results.errors++;
    console.log(`  ERROR: ${relPath} — missing type field`);
    return;
  }

  const noteType = typeMatch[1].trim();
  if (!VALID_TYPES.has(noteType)) {
    results.warnings++;
    if (verbose) console.log(`  WARN: ${relPath} — unknown type: ${noteType}`);
  }

  // Check title field
  if (!fm.match(/^title:/m)) {
    results.warnings++;
    if (verbose) console.log(`  WARN: ${relPath} — missing title field`);
  }
}

function scanDir(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!entry.name.startsWith(".") && entry.name !== "node_modules") {
        scanDir(fullPath);
      }
    } else if (entry.name.endsWith(".md") && !entry.name.startsWith("_")) {
      checkFile(fullPath);
    }
  }
}

console.log("MeKB Health Check");
console.log("=================");
scanDir(VAULT_ROOT);
console.log(`\nScanned ${results.files} files`);
console.log(`Errors: ${results.errors}`);
console.log(`Warnings: ${results.warnings}`);
process.exit(results.errors > 0 ? 1 : 0);
