# Ideas Vault Format

## Entry Format (append under `## Queue`)

    - **[YYYY-MM-DD]** [type] Short description
      - Raw: (original input verbatim)
      - Angle: (suggested angle, or "none yet")
      - Source: (URL if applicable)
      - Platform: x | threads | both
      - Status: raw | concept | drafted | posted

## Types
- `thought` — half-formed idea, observation, shower thought
- `link` — URL to article, post, video worth commenting on
- `demo` — something Mike built that's worth showing
- `reference` — useful resource to cite or build content around
- `hot-take` — strong opinion, contrarian view, reaction

## Moving to Used (when posted)

Move the entry from `## Queue` to `## Used` and add:

    - **[YYYY-MM-DD]** [type] Short description
      - Posted: YYYY-MM-DD
      - Platform: [x | threads | both]
      - Link: (post URL)

## Backward Compatibility

Existing entries without a `Platform:` field default to `threads`.
