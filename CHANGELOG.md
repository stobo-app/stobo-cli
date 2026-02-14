# Changelog

## 0.3.5

- Smarter error messages: auth failures now point users to https://trystobo.com
- Distinct messages for missing API key, invalid/expired key, insufficient credits, and rate limits
- Bump user-agent to stobo-cli/0.3.5

## 0.3.4

- Add `generate_robots_txt`, `generate_sitemap`, `generate_freshness_code` commands
- Add `rewrite_article` (synchronous optimization)
- Site audit with combined SEO + AEO scoring

## 0.2.0

- `audit site` — combined SEO + AEO site audit
- `llms generate` — llms.txt generator
- `tone extract` — brand voice extraction
- Rich terminal output with progress bars and tables
