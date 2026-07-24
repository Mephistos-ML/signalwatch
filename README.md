# SignalWatch

SignalWatch is a configurable product monitoring bot. It fetches product listings
from external sources, normalises them into domain objects, stores seen items in
SQLite, detects newly observed items, applies matching rules, and sends
notifications.

The first production source is TK Maxx Gold Label.

## Features

- Fetches TK Maxx Gold Label product listings with Playwright-rendered HTML.
- Normalises source-specific product cards into a shared `WatchItem` domain model.
- Persists seen items in SQLite with `first_seen_at` and `last_seen_at` timestamps.
- Detects new items across runs.
- Filters notifications by brand with case-insensitive matching.
- Supports log and Telegram notification adapters.
- Provides one-shot checks and long-running watch mode.
- Adds random polling jitter to avoid fixed, machine-like request intervals.

## Architecture

SignalWatch keeps the monitoring pipeline layered:

```text
CLI -> app workflow -> source -> WatchItem -> storage/dedup -> matching -> notification
```

Key modules:

- `signalwatch.cli`: command-line entry point.
- `signalwatch.app.run_bot`: one monitoring cycle.
- `signalwatch.app.watch`: repeated monitoring loop with polling jitter.
- `signalwatch.sources`: external source adapters.
- `signalwatch.storage`: persistence adapters.
- `signalwatch.matching`: relevance filters such as brand matching.
- `signalwatch.notify`: notification interfaces and adapters.
- `signalwatch.models`: domain models shared across the pipeline.

The source layer only fetches and normalises products. Storage, deduplication,
matching, scheduling, and notifications are kept outside source adapters.

## Installation

SignalWatch requires Python 3.12 or newer.

Install the package from PyPI:

```bash
pip install signalwatch
playwright install webkit
```

The first command installs the `signalwatch` CLI. The second installs the
Playwright browser runtime required by the TK Maxx source adapter.

For local development:

```bash
python3 -m pip install -e ".[dev]"
python3 -m playwright install webkit
```

## Configuration

Example Telegram configuration:

```yaml
source:
  type: tkmaxx
  url: "https://www.tkmaxx.com/uk/en/mens-gold-label/c/02090000?sort=published_date+desc"

storage:
  sqlite_path: "../data/tkmaxx.sqlite3"

notification:
  type: telegram
  bot_token_env: "SIGNALWATCH_TELEGRAM_BOT_TOKEN"
  chat_id_env: "SIGNALWATCH_TELEGRAM_CHAT_ID"

matching:
  brands:
    - Balenciaga
    - Rick Owens
    - Palm Angels
    - Off-White
    - Saint Laurent
    - Stone Island
    - Givenchy

polling:
  interval_seconds: 3600
  jitter_seconds: 600
```

Relative paths such as `storage.sqlite_path` are resolved relative to the YAML
file location.

## Usage

Run one monitoring cycle:

```bash
signalwatch check examples/tkmaxx-telegram.yml
```

Run continuously:

```bash
signalwatch watch examples/tkmaxx-telegram.yml
```

Stop watch mode with `Ctrl+C`.

## Telegram Setup

1. Create a bot with `@BotFather`.
2. Send `/start` to the bot.
3. Fetch updates to find your chat ID:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

4. Export the required environment variables:

```bash
export SIGNALWATCH_TELEGRAM_BOT_TOKEN="<TOKEN>"
export SIGNALWATCH_TELEGRAM_CHAT_ID="<CHAT_ID>"
```

5. Run:

```bash
signalwatch check examples/tkmaxx-telegram.yml
```

Telegram messages use a compact HTML-formatted layout:

```text
❗ NEW ITEM

Gucci & Co - Leather belt
💷 £199.99 | RRP £410.00 | Save £210.01 (51%)
⚠️ ONLY 1 LEFT

https://example.com/products/1
```

## Matching

Brand matching is case-insensitive:

```yaml
matching:
  brands:
    - Balenciaga
    - Rick Owens
```

The following source values all match `Balenciaga`:

```text
Balenciaga
BALENCIAGA
balenciaga
```

If `matching` is omitted or `matching.brands` is empty, all newly seen items are
eligible for notification.

Storage still records every fetched item, not only matched items. Matching only
controls which new items are reported.

## Storage

SQLite is used as durable local state. The `seen_items` table stores:

- `source`
- `item_id`
- `title`
- `url`
- `first_seen_at`
- `last_seen_at`
- `metadata_json`

The primary key is `(source, item_id)`, which allows one database to store items
from multiple sources without collisions.

On a fresh database, all currently visible matching items are considered new.
After that, only previously unseen matching items trigger notifications.

## Polling Jitter

Watch mode uses:

```yaml
polling:
  interval_seconds: 3600
  jitter_seconds: 600
```

With this configuration, checks happen every 3000 to 4200 seconds. This avoids
requesting the source at exactly the same time every hour.

## Development

Run tests:

```bash
pytest
```

Run a syntax check:

```bash
python3 -m compileall src tests
```

## Current Limitations

- TK Maxx is the only implemented production source.
- Telegram notifications are text-only; product images are parsed but not sent.
- Watch mode runs as a foreground process, not as an installed service.
- Notification batching and retry policies are intentionally minimal.

## License

MIT License. See [LICENSE](LICENSE).
