#!/usr/bin/env node
/**
 * graph-query.js — MeKB Graph Search
 *
 * Simple BM25-style search over vault notes with type and tag filtering.
 *
 * Usage:
 *   node .claude/scripts/graph-query.js <query>
 *   node .claude/scripts/graph-query.js <query> --type Concept
 *   node .claude/scripts/graph-query.js <query> --tag domain/security
 *   node .claude/scripts/graph-query.js --orphans
 *   node .claude/scripts/graph-query.js --since 2026-02-01
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VAULT_ROOT = path.resolve(__dirname, "../..");

const args = process.argv.slice(2);
const query = args.find(a => !a.startsWith("--"));
const filterType = args.find(a => a.startsWith("--type="))?.split("=")[1]
  || (args.indexOf("--type") !== -1 ? args[args.indexOf("--type") + 1] : null);
const filterTag = args.find(a => a.startsWith("--tag="))?.split("=")[1]
  || (args.indexOf("--tag") !== -1 ? args[args.indexOf("--tag") + 1] : null);
const showOrphans = args.includes("--orphans");
const sinceDate = args.find(a => a.startsWith("--since="))?.split("=")[1]
  || (args.indexOf("--since") !== -1 ? args[args.indexOf("--since") + 1] : null);

const notes = [];
const linkTargets = new Set();

function parseFrontmatter(content) {
  if (!content.startsWith("---")) return null;
  const end = content.indexOf("---", 4);
  if (end === -1) return null;
  const fm = content.slice(4, end);
  const result = {};
  for (const line of fm.split("\n")) {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (match) result[match[1]] = match[2].trim().replace(/^["']|["']$/g, "");
  }
  // Parse tags array
  const tagMatch = fm.match(/tags:\s*\[([^\]]+)\]/);
  if (tagMatch) result.tags = tagMatch[1].split(",").map(t => t.trim().replace(/^["']|["']$/g, ""));
  return result;
}

function extractLinks(content) {
  const links = [];
  const re = /\[\[([^\]|]+)/g;
  let m;
  while ((m = re.exec(content))) links.push(m[1]);
  return links;
}

function scanDir(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith(".") && entry.name !== "node_modules") {
      scanDir(fullPath);
    } else if (entry.name.endsWith(".md")) {
      const content = fs.readFileSync(fullPath, "utf8");
      const fm = parseFrontmatter(content);
      const links = extractLinks(content);
      links.forEach(l => linkTargets.add(l));
      const title = fm?.title || entry.name.replace(".md", "");
      notes.push({
        path: path.relative(VAULT_ROOT, fullPath),
        title,
        type: fm?.type,
        tags: fm?.tags || [],
        created: fm?.created,
        content: content.toLowerCase(),
        links,
      });
    }
  }
}

scanDir(VAULT_ROOT);

let results = notes;

// Filter by type
if (filterType) results = results.filter(n => n.type === filterType);

// Filter by tag
if (filterTag) results = results.filter(n => n.tags.some(t => t.includes(filterTag)));

// Filter by date
if (sinceDate) results = results.filter(n => n.created && n.created >= sinceDate);

// Orphan detection
if (showOrphans) {
  const allTitles = new Set(notes.map(n => n.title));
  results = results.filter(n => {
    const name = n.path.replace(/\.md$/, "").split("/").pop();
    return !linkTargets.has(name) && !linkTargets.has(n.title);
  });
  console.log(`Found ${results.length} orphaned notes:`);
  results.slice(0, 30).forEach(n => console.log(`  ${n.path} (${n.type || "unknown"})`));
  process.exit(0);
}

// BM25-style search
if (query) {
  const terms = query.toLowerCase().split(/\s+/);
  results = results.map(n => {
    let score = 0;
    for (const term of terms) {
      const count = (n.content.match(new RegExp(term, "gi")) || []).length;
      if (count > 0) score += Math.log(1 + count);
      if (n.title.toLowerCase().includes(term)) score += 3;
    }
    return { ...n, score };
  }).filter(n => n.score > 0).sort((a, b) => b.score - a.score);
}

// Output
const limit = 20;
console.log(`Found ${results.length} results${query ? ` for "${query}"` : ""}:`);
results.slice(0, limit).forEach(n => {
  const type = n.type ? `[${n.type}]` : "";
  const score = n.score ? ` (${n.score.toFixed(1)})` : "";
  console.log(`  ${type} ${n.path}${score}`);
});
if (results.length > limit) console.log(`  ... and ${results.length - limit} more`);
