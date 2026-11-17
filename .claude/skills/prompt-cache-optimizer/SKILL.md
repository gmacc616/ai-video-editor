---
name: prompt-cache-optimizer
description: Restructure prompts and system content so Anthropic prompt caching actually hits, cutting cost and latency on repeated calls. Use when the user asks to "enable prompt caching", "improve cache hit rate", "why isn't my cache hitting", "use cache_control", "reduce API cost with caching", "my prompts are slow/expensive", "optimize the system prompt for caching", or is building anything with the Anthropic SDK / Claude API that re-sends large stable context (tools, system prompt, docs, RAG chunks) across calls. Gives stable-prefix ordering, correct cache_control placement, and a verification checklist.
---

# prompt-cache-optimizer

Make Anthropic [prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) earn its keep. A cache hit can cut the cost of cached input tokens by ~90% and meaningfully drop latency — but only if the prompt is structured so the cached prefix is reused **byte-for-byte** across calls. Most "caching isn't working" cases are a structural mistake, not a config one.

## The mental model (get this right and everything follows)

Prompt caching is **prefix caching**. The cache key is the exact sequence of tokens from the start of the request up to a `cache_control` breakpoint. On the next call, Claude reuses the cache only for the longest prefix that is *identical* to a cached one. Consequences:

1. **Order matters more than anything.** Stable content must come *first*; volatile content must come *last*. One changed byte early in the prompt invalidates the cache for everything after it.
2. **The breakpoint marks the end of the reusable region.** You place `cache_control: {type: "ephemeral"}` on the *last* stable block; everything before it (including content with no breakpoint of its own) becomes cacheable as the prefix.
3. **Minimum cacheable length applies.** A prefix must clear a model-specific token minimum (commonly ~1024 tokens; smaller for some models) or it won't cache at all. Don't try to cache a tiny system string.
4. **Caches are short-lived.** Default TTL is ~5 minutes, refreshed on each hit; a longer (~1 hour) TTL is available via the extended option. Caching helps workloads that re-hit within the window — chat sessions, agent loops, batch jobs over a shared preamble.

## When this runs

The user is sending repeated Claude API requests that share large stable context (a long system prompt, tool definitions, a document, RAG context, few-shot examples) and wants to stop paying full price for it every call — or caching is configured but not hitting.

## Procedure

### 1. Map the prompt into stable vs volatile
Classify every part of the request by how often it changes across calls:

| Layer | Typical volatility | Cache it? |
|---|---|---|
| `tools` array | stable across a session | ✅ yes — and it's *first* in cache order |
| `system` prompt / instructions | stable | ✅ yes |
| Large docs / context / few-shot examples | stable per task | ✅ yes |
| RAG chunks | stable if retrieved once, volatile if per-turn | depends — see below |
| Conversation history (older turns) | append-only (grows, prefix stable) | ✅ yes, with a breakpoint near the end |
| Latest user message | changes every call | ❌ no — keep it after the breakpoint |

### 2. Order for a stable prefix
Anthropic caches in this canonical order — **tools → system → messages**. Arrange your content to match, stable-first within each:
- Put `tools` first and keep their definitions and order **fixed** (reordering tools busts the cache).
- Put the **invariant** part of the system prompt before any part that varies.
- Put long stable documents / few-shot blocks high, before anything per-request.
- Keep the volatile tail — the new user turn, per-call variables, timestamps — **last**, after the final breakpoint.

### 3. Place `cache_control` breakpoints
- Put a breakpoint on the **last block of the longest stable prefix** you want cached. Everything before it caches as the prefix.
- You may use multiple breakpoints (the API supports up to 4) to cache nested layers that change at different rates — e.g. one after `tools`, one after the system prompt, one after the growing conversation prefix. This lets a partial change invalidate only the tail, not everything.
- For a growing conversation, move/repeat the breakpoint to the end of the latest *stable* turn each call so the prior history keeps hitting.

The exact SDK syntax (Python, TypeScript, raw HTTP) and a worked multi-breakpoint example live in **[references/cache-control.md](references/cache-control.md)** — load it when writing code.

### 4. Eliminate cache-busters
A single early change throws away the whole prefix. Hunt these down:
- **Timestamps / dates / request IDs / random values injected into the system prompt or tools.** Move them into the volatile tail, or drop them from the prefix entirely.
- **Reordered tools or JSON keys** between calls (non-deterministic serialization). Fix the order.
- **Per-user data spliced into the middle** of an otherwise shared preamble. Hoist the shared part above it.
- **Whitespace / formatting drift** from regenerating the prompt string differently each time. Build the stable prefix once, reuse the exact bytes.
- **Switching models / settings that change tokenization** of the prefix.

### 5. Verify it actually hits
Don't assume — check the usage fields the API returns:
- `cache_creation_input_tokens` — tokens written to cache (you pay a small premium on the *first* call to populate it).
- `cache_read_input_tokens` — tokens served from cache (the ~90%-cheaper hit you want to see climbing on subsequent calls).
- `input_tokens` — the uncached remainder.
A healthy pattern: call 1 shows high `cache_creation`, calls 2..N show high `cache_read` and low `input_tokens`. If `cache_read` stays 0, the prefix isn't stable — go back to step 4.

## Checklist (run before declaring caching "done")

- [ ] Stable content (tools, system, docs) is ordered **first**; volatile content is **last**.
- [ ] `tools` definitions and order are byte-stable across calls.
- [ ] No timestamps / IDs / random values live inside the cached prefix.
- [ ] The cached prefix clears the model's minimum token length (~1024).
- [ ] `cache_control` sits on the **last block of the stable prefix** (plus extra breakpoints for layers that change at different rates).
- [ ] For growing chats, the breakpoint advances to the end of the latest stable turn.
- [ ] `cache_read_input_tokens` is non-zero and rising on repeat calls (verified, not assumed).
- [ ] The workload re-hits within the cache TTL (~5 min, or ~1 hr extended); if not, caching won't help and that's expected.

## Rules

- **Caching is a structuring problem, not a flag.** Adding `cache_control` to a prompt whose prefix changes every call does nothing. Fix the order and the busters first.
- **First call costs slightly more** (cache write premium); the payoff is on the repeats. If a prompt is sent only once, caching is net-negative — don't add it.
- **Never reorder content purely for caching if it changes the model's behavior or correctness.** A cheaper prompt that answers worse is a loss. Structure for cache hits *within* what produces the right output.
- **Verify with the usage fields.** "I added cache_control" is not evidence; a rising `cache_read_input_tokens` is.
- Don't cache tiny prefixes (below the minimum) — it can't cache and you've added complexity for nothing.
