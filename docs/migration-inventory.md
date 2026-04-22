# Migration Inventory

This document records what should move forward and what should stay behind.

## Douyin: keep / redesign

Keep as conceptual inputs:
- persistent QR login worker
- generic image-note publish flow
- recent-post inspection
- comment collection + reply state
- request-driven asset generation

Do not carry over as stable core:
- debug probes
- theme-specific publish scripts
- hardcoded proxy/profile/output paths
- React-internal music injection as a default stable API
- destructive cleanup scripts without stable identifiers

## XHS: keep / redesign

Keep as conceptual inputs:
- browser service split by capability
- draft / publish lifecycle
- creator note fetch
- notification / comment reply path
- deterministic note-image renderer
- multi-account execution model

Do not carry over as stable core:
- runtime env sprawl
- brittle QR image upload hacks
- Bun-specific HTTP path in the main OSS core
- explore / engagement automation as part of the stable release
- compiled-vendor package shape as the project source of truth

## New stable OSS surface

Douyin tools:
- douyin_check_auth
- douyin_start_login
- douyin_get_login_state
- douyin_stop_login
- douyin_search_content
- douyin_publish_image_post
- douyin_publish_image_post_with_music
- douyin_inspect_recent_posts
- douyin_get_post_stats
- douyin_get_note_detail
- douyin_list_messages
- douyin_reply_message
- douyin_reply_visible_comments

XHS tools:
- xhs_check_auth
- xhs_search_content
- xhs_create_draft
- xhs_get_draft
- xhs_list_drafts
- xhs_delete_draft
- xhs_delete_note
- xhs_update_draft
- xhs_publish_draft
- xhs_like_feed
- xhs_favorite_feed
- xhs_like_comment
- xhs_favorite_comment
- xhs_post_comment
- xhs_create_and_publish_draft
- xhs_get_my_notes
- xhs_get_note_detail
- xhs_get_post_stats
- xhs_get_notifications
- xhs_list_messages
- xhs_reply_message
- xhs_reply_comment
