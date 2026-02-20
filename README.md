# life365-search

FastAPI service for searching Life365 products.

## Search entry points samples

Base URL: `http://localhost:8000`

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
