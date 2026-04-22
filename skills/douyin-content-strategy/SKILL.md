---
name: douyin-content-strategy
description: Strategy-layer skill for Douyin publishing, hooks, comment handling, and post-review without embedding platform execution code.
---

# Douyin Content Strategy

Use this skill when:
- preparing a new Douyin image-note or short-form publish brief
- reviewing why a post did not move
- deciding how to reply to comments without losing tone consistency

## Layer split

- MCP / platform adapter handles:
  - auth
  - upload
  - publish
  - recent-post inspection
  - visible-comment reply actions
- This skill handles:
  - hook quality
  - tone consistency
  - interaction prompts
  - review loop after publish

## Publishing checklist

1. First line must create tension in under one breath.
2. Do not stack multiple emotional claims in one sentence.
3. Keep the first card visually obvious on mobile.
4. Add one light interaction prompt, not a hard CTA.
5. Avoid repetitive self-descriptions across consecutive posts.

## Review loop

If traffic is weak, check in this order:
1. hook clarity
2. first-screen stop power
3. comment signal
4. post density overlap with recent posts
5. whether the publish timing was crowded by same-day posts
