# OSS Roadmap

## Current snapshot

- curated MCP surface is defined and wired in code
- local runtime currently exposes 35 implemented tools
- strategy layer currently ships 3 reusable skills
- targeted MCP server / registry tests are green

## Phase 1 — completed foundation

- establish clean repo shape
- define stable curated tool surface
- move strategy docs into reusable skills
- add naming / style rules and formatter configuration
- remove debug/legacy sprawl from the public core

## Phase 2 — mostly completed runtime port

Completed:
- port Douyin stable flows into typed adapters
- port XHS stable flows into typed adapters
- add search, note-detail, private-message reply, comment-reply, and post-stats flows
- add transport-ready MCP server runtime and manifest layer
- add adapter / registry / server-layer tests for the curated surface

Still open in this phase:
- real platform end-to-end verification for the `external_dependent` publish flows
- doc cleanup so README / roadmap / inventory stay aligned with registry truth
- broader fixture coverage for higher-risk browser-state edges

## Phase 3 — next expansion

- optional experimental modules for music, growth experiments, or research flows
- richer storage layer
- account/job abstractions
- CI + packaging
- publish-ready examples and operator docs for external users
