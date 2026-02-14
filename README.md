# Stobo CLI

AI-powered SEO/AEO audit tool for the terminal. Audit websites, extract brand voice, generate llms.txt files, and optimize content — all from the command line.

## Install

```bash
pip install stobo
```

## Quick Start

```bash
# Run a full site audit (free — no key needed)
stobo audit site https://example.com

# Run an article-level audit (free)
stobo audit run https://example.com/blog/my-post

# Authenticate for paid features
stobo auth login sk_your_api_key

# Extract brand voice (500 credits)
stobo tone extract https://blog.example.com

# Generate llms.txt (500 credits)
stobo llms generate https://example.com

# Full optimization pipeline (1,000 credits)
stobo optimize run https://example.com/blog/my-post

# Check credit balance
stobo credits

# JSON output (any command)
stobo --json audit site https://example.com
```

## Commands

### Free (no API key required)

| Command | Description |
|---------|-------------|
| `stobo audit site <url>` | Full site audit: 30 SEO + 7 AEO checks + blog detection + sitemap discovery |
| `stobo audit run <url>` | Article-level SEO + AEO audit |
| `stobo audit run <url> --seo-only` | SEO-only audit |
| `stobo audit run <url> --aeo-only` | AEO-only audit |
| `stobo freshness run <sitemap>` | Sitemap schema freshness audit |

### Paid (API key + credits)

| Command | Credits | Description |
|---------|---------|-------------|
| `stobo tone extract <blog>` | 500 | Extract brand voice profile from blog |
| `stobo llms generate <url>` | 500 | Generate llms.txt for AI discoverability |
| `stobo optimize run <url>` | 1,000 | Full audit + tone + rewrite pipeline |
| `stobo export run <cid> <type>` | 200 | Generate markdown report |

### Management

| Command | Description |
|---------|-------------|
| `stobo auth login <key>` | Save and validate API key |
| `stobo auth status` | Show current auth status |
| `stobo auth logout` | Clear stored API key |
| `stobo credits` | Check credit usage and balance |
| `stobo audit list` | List recent audits |
| `stobo tone list` | List brand voice profiles |
| `stobo tone get <cid>` | Get a specific profile |
| `stobo tone delete <cid>` | Delete a profile |
| `stobo optimize status <id>` | Check optimization job status |
| `stobo optimize preview <id>` | Show before/after preview |
| `stobo optimize jobs` | List optimization jobs |
| `stobo export get <cid> <type>` | Get cached export |

## Global Options

- `--api-key` — Override stored API key
- `--base-url` — Override API base URL
- `--json` — Raw JSON output
- `--version` — Show version

## What's New in 0.2.0

- `stobo audit site` — full website audit with rich output (SEO categories, AEO checklist, blog detection, sitemap discovery, recommendations)
- `stobo llms generate` — generate llms.txt files for AI discoverability
- `stobo credits` — view credit usage with breakdown table
- Credit display after paid operations
- Security: config file permissions hardened to 600

## Get an API Key

1. Sign up at [trystobo.com](https://trystobo.com)
2. Go to Settings > API Keys
3. Create a new key: `stobo auth login sk_your_key`

## License

MIT
