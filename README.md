# Expense Tracker API — Intern Screening

A small Django REST Framework backend for tracking personal spending
(categories, expenses, date filtering, and a per-category summary).

## Your Task (read this first)

You will work with this codebase in four stages:

1. **Fix 5 bugs.** The code contains **5 intentional bugs**. Find and fix them
   all. Every hint you need is in the codebase or in this file.
2. **Add Authentication (required).** Scope expenses and categories to the
   logged-in user and protect the endpoints.
3. **Build 2 integration features (required):**
   [Currency conversion](#feature-1--currency-conversion) and
   [Budget threshold bot alerts](#feature-2--budget-threshold-bot-alerts).
   Both are specified in detail below, with example requests/responses — these
   are the hard part.
4. **Add 2 optional features** of your choice ([list below](#optional-pick-any-2)).

Config placeholders for stage 3 are already in `.env.example` — copy them into
your `.env`.

Full rules, branch naming, and submission details are in
[requirements](#full-requirements) at the bottom. Read that **before** writing
code — workflow is graded.

## What you've been given

| File / Dir                 | What it is                                              |
|----------------------------|---------------------------------------------------------|
| `expenses/`                | The app: `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py` |
| `config/`                  | Django project settings and root URL config             |
| `postman_collection.json`  | **Ready-to-import Postman collection — every endpoint.** Use it to test and hunt bugs. |
| `.env.example`             | Template for your `.env`                                 |
| `pyproject.toml`           | Dependencies (managed by `uv`)                          |
| `manage.py`                | Django entry point                                      |

## Setup (3 commands)

Uses [uv](https://docs.astral.sh/uv/). Prefix every `manage.py` call with `uv run`.

```bash
uv sync                                  # create .venv + install deps
cp .env.example .env                     # then fill in SECRET_KEY
uv run python manage.py migrate          # set up the SQLite DB
uv run python manage.py runserver        # start at http://127.0.0.1:8000/
```

> No `uv`? Use the stdlib instead — same result:
> `python -m venv .venv && .venv\Scripts\activate` (Windows) or
> `source .venv/bin/activate` (macOS/Linux), then
> `pip install -e .`, `python manage.py migrate`, `python manage.py runserver`.

## Test the endpoints

1. Import `postman_collection.json` into Postman.
2. The `base_url` variable is preset to `http://127.0.0.1:8000`.
3. Run each request against your local server. **This is your main bug-hunting
   tool** — compare actual responses against the expected behavior below.

### Endpoints

All `/api/` endpoints except register/login require an auth token
(`Authorization: Token <key>`).

| Method      | Endpoint                         | Description                                                        |
|-------------|----------------------------------|-------------------------------------------------------------------|
| POST        | `/api/auth/register/`            | Create a user, returns an auth token (public)                     |
| POST        | `/api/auth/login/`               | Exchange credentials for an auth token (public)                   |
| GET         | `/api/categories/`               | List the caller's categories                                      |
| POST        | `/api/categories/`               | Create a category (optional `monthly_limit`)                      |
| GET/PUT/PATCH/DELETE | `/api/categories/{id}/` | Retrieve, update, or delete one category                          |
| GET         | `/api/expenses/`                 | List expenses; filter with `?start_date=` & `?end_date=` (inclusive), `?search=`, `?category=`, `?min_amount=`, `?max_amount=` |
| POST        | `/api/expenses/`                 | Create an expense (optional `currency`, ISO code)                 |
| GET         | `/api/expenses/{id}/`            | Retrieve one expense                                              |
| PUT/PATCH   | `/api/expenses/{id}/`            | Update an expense                                                 |
| DELETE      | `/api/expenses/{id}/`            | Delete an expense                                                 |
| GET         | `/api/expenses/summary/`         | Total spent per category, converted to `BASE_CURRENCY`            |
| GET         | `/api/expenses/monthly-summary/` | Total spent per calendar month, converted to `BASE_CURRENCY`      |

## Tech stack

Python 3 · Django 5 · Django REST Framework · SQLite · python-dotenv

---

## Full Requirements

### Git workflow (graded)

- Create a new repo under **your** GitHub account.
- Default branch **must be named `trunk`** (not `main`/`master`).
- One branch + one PR per item:
  - Bug fixes → `fix/<bug-name>`
  - Features → `feature/<feature-name>`
- **Never commit fixes or features directly to `trunk`.** Merge via PR.
- Do **not** squash. Keep a clean, atomic, readable history. Push regularly.
- Each commit message must say **what** changed and **why**. Example:

  ```text
  fix(expenses): prevent negative expense amounts
  fix(api): correct serializer field mapping
  ```

### Required features

**Authentication** — expenses and categories owned by and scoped to the
authenticated user; endpoints protected (token/session auth + login).

Plus the two integration features below.

#### Feature 1 — Currency conversion

Let expenses be recorded in different currencies and reported in one base
currency, using a third-party exchange-rate API.

- Add a `currency` field to expenses (ISO code, e.g. `EUR`); `amount` stays in
  that currency.
- Reporting endpoints (e.g. `summary`) convert each amount to `BASE_CURRENCY`
  (see `.env.example`) using rates from an exchange-rate API.
- Free providers needing no key: `exchangerate.host`, `open.er-api.com`.

Example (illustrative — refine the exact shape as you see fit):

```jsonc
// POST /api/expenses/
{
  "title": "Hotel in Paris",
  "amount": "120.00",
  "currency": "EUR",
  "category": 1,
  "date": "2026-06-09"
}

// 201 Created
{
  "id": 7,
  "title": "Hotel in Paris",
  "amount": "120.00",
  "currency": "EUR",
  "category": 1,
  "date": "2026-06-09"
}
```

```jsonc
// GET /api/expenses/summary/   (BASE_CURRENCY = USD)
{
  "base_currency": "USD",
  "categories": [
    {
      "category": "Travel",
      "total": "129.60",        // 120.00 EUR converted at 1.08
      "rate": "1.08",
      "as_of": "2026-06-10"
    }
  ]
}
```

#### Feature 2 — Budget threshold bot alerts

Send a chat-bot alert when a category's spending crosses a configured limit.

- Add a per-category monthly budget limit.
- When a created/updated expense pushes that category's month-to-date total over
  its limit, send an alert via a bot (Telegram recommended — free token from
  `@BotFather`; Discord/Slack also fine). Credentials come from `.env`
  (`BOT_TOKEN`, `BOT_CHAT_ID`).

Example (illustrative — refine the exact shape as you see fit):

```jsonc
// Set a monthly limit on a category
// POST /api/categories/   (or PATCH an existing one)
{
  "name": "Dining",
  "monthly_limit": "200.00"
}
```

```jsonc
// POST /api/expenses/  — this expense pushes Dining's month total to 215.00,
// over its 200.00 limit, so an alert fires once.
{
  "title": "Dinner out",
  "amount": "45.00",
  "category": 3,
  "date": "2026-06-09"
}

// 201 Created — API responds normally; the alert is sent off the request path.
{
  "id": 12,
  "title": "Dinner out",
  "amount": "45.00",
  "category": 3,
  "date": "2026-06-09"
}
```

```text
Bot message delivered to BOT_CHAT_ID:

⚠️ Budget alert: "Dining" is over its monthly limit.
Spent 215.00 / 200.00 USD for June 2026.
```

Include **screenshots of the delivered bot alert** (the message in your
Telegram/Discord/Slack chat) in your README as proof it works.

#### Optional (pick any 2)

Recurring expenses · CSV export · Analytics dashboard · Expense
search/filtering · Monthly spending summaries · Favorite categories.

Each feature must be fully functional, follow existing API conventions, and
include validation. You may also improve the Django Admin.

### API documentation

- Update `postman_collection.json` with any new endpoints.
- Responses must carry enough data for a frontend to render views without extra
  follow-up requests.

### README write-up

In your README, add two sections:

- `## My Features` — for each feature (auth, currency conversion, bot alerts,
  and your optional one): overview, design decisions, API changes, example
  request/response, assumptions, known limits. For bot alerts, include
  **screenshots of the delivered alert**.
- `## Bugs Found and Fixed` — for each bug: description, root cause, fix, and
  commit hash.

### Submission

Submit: GitHub repo URL · updated Postman collection · updated README
(including bot-alert screenshots).

### Evaluation criteria

Commit quality · bug-fix correctness (no regressions) · feature design ·
Postman completeness · code readability · REST conventions (status codes,
response shape).

---

## My Features

### Authentication (required)

**Overview.** All category and expense data is owned by, and scoped to, the
authenticated user. Every `/api/` endpoint requires a token except the two
public auth endpoints.

**Design decisions.**
- **DRF `TokenAuthentication` + `SessionAuthentication`.** Token auth for API
  clients (Postman/frontend); session auth keeps the browsable API usable in a
  logged-in browser. Set globally via `DEFAULT_AUTHENTICATION_CLASSES`.
- **`DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`** — secure by default. The
  only opt-outs are `register`/`login`, which set `@permission_classes([AllowAny])`.
- **Ownership at the query layer.** Every queryset is filtered by
  `owner=request.user`, and detail lookups use `get(pk=pk, owner=request.user)`,
  so one user can never read or mutate another's rows — a wrong owner yields a
  clean `404`, not a `403` that would leak existence. The serializer also
  rejects attaching an expense to a category the caller doesn't own.

**API changes.**
- `POST /api/auth/register/` → `{ "username", "password" }` ⇒ `201 { id, username, token }`
- `POST /api/auth/login/` → `{ "username", "password" }` ⇒ `200 { token }` (or `401`)
- All other endpoints require header `Authorization: Token <key>`.

**Example.**
```jsonc
// POST /api/auth/register/   { "username": "demo", "password": "passw0rd123" }
// 201 Created
{ "id": 1, "username": "demo", "token": "6b8b7dd8…" }
```

**Assumptions / known limits.** Username + password only (no email
verification). Tokens are long-lived and non-rotating — fine for this scope;
production would add expiry/refresh.

### Currency conversion (required)

**Overview.** Expenses are stored in their own ISO currency; reporting endpoints
convert every amount to `BASE_CURRENCY` (default `USD`) using live rates.

**Design decisions.**
- **`currency` field on `Expense`** (3-char ISO, default `USD`); `amount` stays
  in that currency, so historical records are never silently rewritten.
- **Provider:** `open.er-api.com` — free, no API key, shape
  `GET <url>/latest/<BASE>` → `{ "rates": {…} }`. URL is configurable via
  `EXCHANGE_RATE_API_URL`, so swapping providers is a `.env` change.
- **In-process rate cache** keyed by base currency, valid for the current day, so
  a summary over many expenses makes at most one HTTP call per base currency.
- **Graceful degradation:** if the rate API is unreachable, `_convert_safe`
  falls back to the raw amount instead of 500-ing the report.
- Conversion is isolated in `expenses/currency.py` (pure functions, easy to
  unit-test and mock).

**API changes.** `POST/PUT /api/expenses/` accept `currency`. `summary` and
`monthly-summary` responses are expressed in `BASE_CURRENCY`.

**Example.**
```jsonc
// POST /api/expenses/  { "title": "Hotel in Paris", "amount": "120.00",
//                        "currency": "EUR", "category": 1, "date": "2026-06-09" }
// GET /api/expenses/summary/   (BASE_CURRENCY = USD)
{
  "base_currency": "USD",
  "categories": [ { "category": "Travel", "total": "138.47" } ]
}
```

**Assumptions / known limits.** Daily rates (not intraday); a stored expense is
converted at *report time*, not locked at entry time. Rate cache is per-process
(resets on restart) — a shared cache (Redis) would suit multi-worker deploys.

### Budget threshold bot alerts (required — Discord)

**Overview.** Each category may carry a `monthly_limit` (in `BASE_CURRENCY`).
When a created/updated expense pushes that category's month-to-date total over
the limit, a Discord alert is delivered.

**Design decisions.**
- **Discord webhook** (`DISCORD_WEBHOOK_URL` in `.env`) — no bot token/gateway
  needed, just an HTTP `POST` of `{ "content": "…" }`.
- **Off the request path:** the alert is sent from a daemon `threading.Thread`,
  so a slow or failing webhook never blocks (or fails) the API response — the
  spec's "API responds normally; the alert is sent off the request path."
- **Fires once, on the crossing edge:** the alert sends only when the total was
  at/under the limit *before* this expense and over it *after*
  (`total_before <= limit < total_after`), so re-saving an already-over category
  doesn't spam the channel.
- **Month-to-date is computed in `BASE_CURRENCY`,** converting each contributing
  expense, so mixed-currency spending is compared against the limit correctly.
- Delivery isolated in `expenses/alerts.py`; failures are logged, never raised.

**API changes.** `monthly_limit` added to the category serializer (set via
`POST`/`PATCH /api/categories/`). No new endpoints — alerts are a side effect of
creating/updating expenses.

**Example + proof.**
```text
⚠️ Budget alert: "Dining" is over its monthly limit.
Spent 215.00 / 200.00 USD for June 2026.
```

> **TODO (you):** create a Discord webhook (Server Settings → Integrations →
> Webhooks → New Webhook → Copy URL), put it in `.env` as `DISCORD_WEBHOOK_URL`,
> trigger an over-limit expense, and **paste the screenshot of the delivered
> message here.**
>
> `![Discord budget alert](docs/discord-alert.png)`

**Assumptions / known limits.** Limit is interpreted in `BASE_CURRENCY`. The
"fire once" check is per save event, not persisted state — re-crossing in a new
month alerts again (intended); editing history downward then back up could
re-alert. A production system would record an "alerted" flag per category-month.

### Optional 1 — Expense search & filtering

**Overview.** `GET /api/expenses/` accepts extra query params, composable with
the existing date range.

**API changes / example.**
- `?search=` — case-insensitive title match (`title__icontains`)
- `?category=` — category id
- `?min_amount=` / `?max_amount=` — amount bounds
- `GET /api/expenses/?search=paris&min_amount=50&category=1`

**Design / limits.** All filters are applied in `_filter_expenses`, ORM-side
(no Python filtering), and always after owner scoping. Amount filtering compares
the *stored* amount (in its own currency), not the converted value — documented
so a frontend knows what it's filtering on.

### Optional 2 — Monthly spending summaries

**Overview.** `GET /api/expenses/monthly-summary/` returns total spend per
calendar month, converted to `BASE_CURRENCY`, newest month first.

**Example.**
```jsonc
{ "base_currency": "USD", "months": [ { "month": "2026-06", "total": "138.47" } ] }
```

**Design / limits.** Months are keyed `YYYY-MM`. Conversion reuses the same
cached-rate path as the category summary. Aggregation is done in Python because
each expense may need a per-currency conversion before summing.

---

## Bugs Found and Fixed

> Commit hashes are filled in once each `fix/*` branch is committed (see the
> Git-workflow section). Replace the `<hash>` placeholders before submitting.

| # | Bug | Root cause | Fix | Commit |
|---|-----|------------|-----|--------|
| 1 | Creating an expense returned `500` / `category` never saved | `ExpenseSerializer.Meta.fields` listed `"catgory"` — a typo that doesn't match the model field | Corrected to `"category"` in `expenses/serializers.py` | `<hash>` |
| 2 | `POST /api/expenses/` raised `NameError` after a valid save | `return Response(serialzer.data …)` — `serialzer` is a typo, the variable is `serializer` | Fixed the variable name in `expense_list` (`views.py`) | `<hash>` |
| 3 | `?start_date=` excluded expenses *on* the start date | Filter used `date__gt` (strictly greater) but the docs specify an **inclusive** range | Changed to `date__gte` in `_filter_expenses` (`views.py`) | `<hash>` |
| 4 | `GET /api/expenses/summary/` raised `NameError: Sum` | `Sum` was used in the aggregate but never imported | (Summary was rewritten for currency conversion; the original needed `from django.db.models import Sum`.) The shipped version aggregates per-category in Python after converting each amount | `<hash>` |
| 5 | `GET /api/expenses/summary/` hit the detail view and 404'd / errored | In `urls.py`, `expenses/<pk>/` was declared **before** `expenses/summary/`, so the router matched `"summary"` as a `pk` | Reordered so specific routes (`summary/`, `monthly-summary/`) precede the `<int:pk>` catch-all, and constrained `pk` to `<int:pk>` | `<hash>` |



---

## Git workflow note

Per the brief: create a repo under your GitHub account, default branch **`trunk`**,
one `fix/<bug-name>` or `feature/<feature-name>` branch + PR per item, no
squashing, atomic commits saying *what* and *why*. The code in this snapshot is
complete and verified; commit it across branches in this order (each branched
off `trunk` after the previous PR merges):
`fix/serializer-category-field` · `fix/expense-create-typo` ·
`fix/inclusive-date-filter` · `fix/summary-sum-import` · `fix/url-route-order` ·
`feature/authentication` · `feature/currency-conversion` ·
`feature/budget-alerts` · `feature/expense-search` · `feature/monthly-summary`.
