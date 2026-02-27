# life365-search

FastAPI service for searching Life365 products.

## Search entry points samples

Base URL: `http://localhost:8000`

### `/search` supported query parameters

| Param | Type | Default | Constraints |
|---|---|---|---|
| `q` | `string \| null` | `null` | Full-text query |
| `category_level_1` | `int \| null` | `null` |  |
| `category_level_2` | `int \| null` | `null` |  |
| `category_level_3` | `int \| null` | `null` |  |
| `brand` | `string \| null` | `null` |  |
| `available` | `bool` | `true` |  |
| `visible` | `bool` | `true` |  |
| `outlet` | `bool` | `false` |  |
| `page` | `int` | `1` | `>= 1` |
| `page_size` | `int` | `20` | `>= 1`, `<= 100` |
| `lang` | `enum` | `it` | `it`, `en`, `cn` |
| `sort` | `enum` | `relevance` | `relevance`, `newest`, `brand` |

### `sort` values behavior

- `relevance`: sorts by OpenSearch `_score` (best text match first). Scoring uses `title` (higher boost), `keywords`, `description`, and category title in the selected language.
- `newest`: sorts by `created_at` descending (most recent first).
- `brand`: sorts by `brand` ascending (A to Z) using exact keyword values.

Notes:

- Filters (`category_level_*`, `brand`, `available`, `visible`, `outlet`) limit which products are returned, but do not change text relevance scoring.
- If `q` is omitted, the query is `match_all`; with `sort=relevance`, ordering is not meaningful by relevance.

### Health check

```bash
curl -s http://localhost:8000/health
```

### Basic full-text search

```bash
curl -sG http://localhost:8000/search \
  --data-urlencode "q=pellicola"
```

### Search with category and brand filters

```bash
curl -sG http://localhost:8000/search \
  --data-urlencode "q=iphone" \
  --data-urlencode "category_level_1=1" \
  --data-urlencode "category_level_2=2" \
  --data-urlencode "brand=Devia"
```

### Search with language, paging, and sort

```bash
curl -sG http://localhost:8000/search \
  --data-urlencode "q=cover" \
  --data-urlencode "lang=en" \
  --data-urlencode "page=2" \
  --data-urlencode "page_size=10" \
  --data-urlencode "sort=newest"
```

### Search outlet products only

```bash
curl -sG http://localhost:8000/search \
  --data-urlencode "outlet=true" \
  --data-urlencode "available=true" \
  --data-urlencode "visible=true"
```

### Trigger full reindex

```bash
curl -sX POST http://localhost:8000/admin/reindex
```

When running with `docker-compose`, the `scheduler` service also triggers
`app.infrastructure.celery.tasks.reindex_all_task` automatically every 6 hours
using the schedule defined in `worker/reindex.cron`.
