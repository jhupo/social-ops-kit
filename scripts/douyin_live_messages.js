#!/usr/bin/env node
const { chromium } = require('playwright');

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

function cleanLines(text) {
  return String(text || '')
    .split('\n')
    .map((x) => x.replace(/\u00a0/g, ' ').trim())
    .filter(Boolean);
}

async function ensureImOpen(page) {
  if (await page.locator('[data-e2e="im-dialog"] [data-e2e="im-entry"]').count()) return;

  await page.mouse.click(1318, 20);
  await page.waitForTimeout(3000);

  if (await page.locator('[data-e2e="im-dialog"] [data-e2e="im-entry"]').count()) return;

  await page.evaluate(() => {
    const candidates = [...document.querySelectorAll('*')].filter((el) => (el.innerText || '').trim() === '私信');
    const headerHit = candidates.find((el) => {
      const rect = el.getBoundingClientRect();
      return rect.top >= 0 && rect.top < 220 && rect.width < 180 && rect.height < 140;
    });
    if (headerHit) {
      headerHit.click();
      return true;
    }
    return false;
  });

  await page.waitForSelector('[data-e2e="im-dialog"]', { timeout: 15000 }).catch(() => null);
  await page.waitForFunction(
    () => document.querySelectorAll('[data-e2e="im-dialog"] [data-e2e="im-entry"]').length > 0,
    { timeout: 20000 }
  ).catch(() => null);
}

async function openThread(page, index, threadId, targetName) {
  if (targetName) {
    const clickedByName = await page.evaluate((name) => {
      const candidates = [...document.querySelectorAll('*')].filter((el) => (el.innerText || '').trim() === name);
      const hit = candidates.find((el) => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
      if (!hit) return false;
      hit.click();
      return true;
    }, String(targetName));
    if (clickedByName) {
      await page.waitForTimeout(4000);
      return;
    }
  }

  if (threadId) {
    const opened = await page.evaluate((id) => {
      if (typeof window.openImConversation === 'function') {
        try {
          window.openImConversation(String(id));
          return true;
        } catch (error) {
          return false;
        }
      }
      return false;
    }, String(threadId));
    if (opened) {
      await page.waitForTimeout(4000);
      return;
    }
  }

  const items = page.locator('[data-e2e="im-dialog"] [data-e2e="im-entry"]');
  const count = await items.count();
  if (!(index >= 0 && index < count)) {
    throw new Error(`thread_index_out_of_range:${index}/${count}`);
  }
  await items.nth(index).click();
  await page.waitForTimeout(1500);
}

async function listThreads(page, limit) {
  return page.evaluate((rawLimit) => {
    const parsedLimit = rawLimit == null ? null : Number(rawLimit);
    const entries = [...document.querySelectorAll('[data-e2e="im-dialog"] [data-e2e="im-entry"]')].map((el, index) => {
      const lines = (el.innerText || '')
        .split('\n')
        .map((x) => x.replace(/\u00a0/g, ' ').trim())
        .filter(Boolean);
      let unreadCount = 0;
      for (const line of lines) {
        if (/^\d+$/.test(line) && Number(line) < 1000) {
          unreadCount = Math.max(unreadCount, Number(line));
        }
      }
      return {
        index,
        user_name: lines[0] || '',
        last_message: lines[1] || '',
        unread_count: unreadCount,
        raw_lines: lines,
      };
    });
    return parsedLimit == null ? entries : entries.slice(0, parsedLimit);
  }, limit ?? null);
}

async function replyMessage(page, content) {
  const editor = page.locator('div.public-DraftEditor-content[contenteditable="true"]').last();
  await editor.waitFor({ timeout: 15000 });
  await editor.click();
  await page.keyboard.press(process.platform === 'darwin' ? 'Meta+A' : 'Control+A');
  await page.keyboard.press('Backspace');
  await page.keyboard.type(content);
  await page.waitForTimeout(600);

  const sendButton = page.locator('.e2e-send-msg-btn').last();
  await sendButton.waitFor({ timeout: 10000 });
  await sendButton.click();
  await page.waitForTimeout(2500);

  const state = await page.evaluate((expected) => {
    const editorNode = document.querySelector('div.public-DraftEditor-content[contenteditable="true"]');
    const editorText = (editorNode && editorNode.innerText) || '';
    const detail = document.querySelector('[data-mask="conversaton-detail-content"]');
    const detailText = (detail && detail.innerText) || document.body.innerText || '';
    return {
      editorText,
      editorCleared: !String(editorText || '').trim(),
      appearedInDom: String(detailText).includes(expected),
    };
  }, content);

  return {
    success: Boolean(state.editorCleared || state.appearedInDom),
    ...state,
  };
}

(async () => {
  const args = parseArgs(process.argv.slice(2));
  const action = String(args.action || 'list_threads');
  const profileDir = String(args.profileDir || '');
  const url = String(args.url || 'https://www.douyin.com/user/self');
  const proxy = args.proxy ? { server: String(args.proxy) } : undefined;

  const context = await chromium.launchPersistentContext(profileDir, {
    headless: true,
    proxy,
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled'],
  });
  const hits = [];

  try {
    const page = context.pages()[0] || await context.newPage();
    page.on('response', async (resp) => {
      const url = resp.url();
      if (!/imapi\.douyin\.com\/(v1|v2)\/(conversation\/list|conversation\/get_info_list|message\/get_by_conversation|stranger\/get_conversation_list)/.test(url)) {
        return;
      }
      try {
        const body = await resp.body();
        hits.push({
          url,
          status: resp.status(),
          method: resp.request().method(),
          bodyBase64: body.toString('base64'),
        });
      } catch (error) {
        hits.push({ url, status: resp.status(), method: resp.request().method(), bodyBase64: '' });
      }
    });
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
      window.chrome = window.chrome || { runtime: {} };
    });
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(12000);
    await ensureImOpen(page);
    await page.waitForTimeout(3000);

    if (action === 'list_threads') {
      const items = await listThreads(page, args.limit ? Number(args.limit) : null);
      console.log(JSON.stringify({ success: true, items, hits }, null, 2));
      return;
    }

    if (action === 'reply_message') {
      const content = String(args.content || '');
      const threadId = String(args.threadId || '');
      const threadIndex = Number(args.threadIndex || 0);
      let active = null;
      const targetName = String(args.targetName || '');
      if (threadId) {
        await openThread(page, threadIndex, threadId, targetName);
      } else {
        const threads = await listThreads(page, null);
        active = threads[threadIndex] || null;
        await openThread(page, threadIndex, active?.thread_id || '', active?.user_name || targetName);
      }
      const result = await replyMessage(page, content);
      console.log(JSON.stringify({ success: result.success, action, active, threadId, ...result }, null, 2));
      return;
    }

    console.log(JSON.stringify({ success: false, error: 'unknown_action', action }, null, 2));
  } catch (error) {
    console.log(JSON.stringify({ success: false, error: String(error && error.message ? error.message : error) }, null, 2));
    process.exitCode = 1;
  } finally {
    await context.close();
  }
})();
