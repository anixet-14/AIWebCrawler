# Architecture

`URL -> remote-URL validation -> Cloudflare Browser Run -> generic evidence -> Gemini structured output or metadata-only fallback -> Pydantic normalization -> evidence report -> API/UI`.

Cloudflare performs the page retrieval remotely; the direct local fetcher remains an explicit fallback. Evidence extraction uses only JSON-LD, standards metadata, headings, text, and image URLs; it never interprets HTML classes/IDs or uses retailer configurations. Gemini receives bounded evidence and a JSON schema without browsing tools. Product output is strict; evidence remains outside the public ten-field object.
