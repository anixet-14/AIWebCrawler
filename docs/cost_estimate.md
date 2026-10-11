# Cost estimate

The demo uses Cloudflare Browser Run and Gemini API free tiers, but both are quota-limited and subject to their providers' current terms. This does **not** mean production crawling costs zero. Gemini free-tier page evidence is transmitted to Google and may be handled under its free-tier data terms.

There is no local model storage, RAM, or CPU inference requirement in this configuration. At volume, estimate `pages × (remote browser duration + hosted-model input/output tokens)` plus hosting, bandwidth, observability, and compliance review—measure these on representative permitted pages rather than inventing a price per 1,000 pages.
