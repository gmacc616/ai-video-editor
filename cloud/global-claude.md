# Default working guidelines (every session, every project)

Adapted from https://github.com/multica-ai/andrej-karpathy-skills (MIT), based on Andrej Karpathy's observations on LLM coding pitfalls.
They lean toward caution over speed; for trivial tasks, use judgment. Project CLAUDE.md files and explicit user instructions take precedence.

## 1. Think before coding
Don't assume, don't hide confusion, surface tradeoffs.
- State your assumptions explicitly. If uncertain, ask.
- If several interpretations exist, present them; don't pick one silently.
- If a simpler approach exists, say so, and push back when warranted.
- If something is unclear, stop, name what's confusing and ask.

## 2. Simplicity first
Write the minimum code that solves the problem, nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If 200 lines could be 50, rewrite it. Would a senior engineer call it overcomplicated? Then simplify.

## 3. Surgical changes
Touch only what you must; clean up only your own mess.
- Don't "improve" adjacent code, comments or formatting.
- Don't refactor things that aren't broken.
- Match the existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it; don't delete it.
- Remove imports, variables and functions that your own change made unused; leave pre-existing dead code unless asked.
- Every changed line should trace directly to the request.

## 4. Goal-driven execution
Define success criteria, then loop until they're verified.
- "Add validation" → write tests for invalid inputs, then make them pass.
- "Fix the bug" → write a test that reproduces it, then make it pass.
- "Refactor X" → make sure tests pass before and after.
- For multi-step tasks, state a brief plan: each step paired with how it will be verified.

These guidelines are working if diffs have fewer unnecessary changes, there are fewer rewrites from overcomplication, and clarifying questions come before implementation rather than after mistakes.

