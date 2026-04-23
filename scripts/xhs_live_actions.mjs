#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const cur = argv[i];
    if (!cur.startsWith('--')) continue;
    const key = cur.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      out[key] = true;
      continue;
    }
    out[key] = next;
    i += 1;
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
const action = String(args.action || '');
const packagePath = String(args.packagePath || '');
const statePath = String(args.statePath || '');

async function main() {
  if (!packagePath) throw new Error('package_path is required');
  if (!statePath) throw new Error('state_path is required');
  const pkgEntry = path.join(packagePath, 'dist', 'xhs', 'index.js');
  const mod = await import(pathToFileURL(pkgEntry).href);
  const { XhsClient } = mod;
  const state = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
  const client = new XhsClient({
    accountId: args.accountId,
    accountName: args.accountName,
    state,
    proxy: args.proxy,
  });
  try {
    let result;
    if (action === 'post_comment') {
      result = await client.postComment(String(args.noteId || ''), String(args.xsecToken || ''), String(args.content || ''));
    } else if (action === 'reply_comment') {
      result = await client.replyComment(String(args.noteId || ''), String(args.xsecToken || ''), String(args.commentId || ''), String(args.content || ''));
    } else if (action === 'get_notifications') {
      result = await client.getNotifications(String(args.type || 'all'), Number(args.limit || 20));
    } else {
      throw new Error(`unknown_action:${action}`);
    }
    console.log(JSON.stringify({ success: Boolean(result?.success ?? true), action, result }, null, 2));
  } finally {
    await client.close().catch(() => null);
  }
}

main().catch((error) => {
  console.log(JSON.stringify({ success: false, error: String(error?.message || error) }, null, 2));
  process.exitCode = 1;
});
