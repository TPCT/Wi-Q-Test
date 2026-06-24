# wi-Q - PHP Backend Developer Test

The purpose of this test is to demonstrate your understanding of REST APIs and how you would orchestrate their consumption within an application. Please create the basics of a library using whichever tools you feel would be the most suitable to get the job done. We would prefer no specific framework, but if you have a good reason to use something, then feel free. We would also encourage the use of other packages that you deem useful.

Your library should provide the functionality to interact with a REST API, allowing you to perform the operations listed below (Scenario 1 & Scenario 2). It is not necessary to create a functioning REST API for this task, we are simply trying to see how you would go about connecting and consuming information from one. It is important that your library would work in a real world scenario, if required.

Please only spend 1 to 2 hours at most. AI development tools are permitted, but please disclose if you have used them. The next interview stage will contain a discussion of your code including how it works and the design decisions you made.

## How to provide your answer

Your repository should contain a library for interacting with a REST API. It is highly desired that you provide tests, to prove that your solution works and is robust. 

Alongside your library, you will need some additional logic to take the API responses and convert them into the outputs specified in the scenarios below.

## Scenario 1

wi-Q is integrating with a fictitious company called 'Great Food Ltd'. 'Great Food Ltd' provide menu and item data from a REST API. Your job is to write some code to consume their API and parse the response into a readable format.

Using the API endpoints described below, write code that would be able to make a request to this API and collect the product data for the menu named `Takeaway`. Once the product data has been obtained, print it out in a list, containing the product id and name.

### Expected (sample) output

| ID | Name    |
| -- | ------- |
| 4  | Burger  |
| 5  | Chips   |
| 99 | Lasagna |

### API Endpoints

The available endpoints for the 'Great Food Ltd' API are as follows:
> ### /auth_token
> #### Arguments
> | Name          | Value              |
> | ------------- | ------------------ |
> | client_secret | 4j3g4gj304gj3      |
> | client_id     | 1337               |
> | grant_type    | client_credentials |
> #### Request Type
> `POST`
> #### Headers
> | Name         | Value                             |
> | -------------| --------------------------------- |
> | Content-Type | application/x-www-form-urlencoded |
> #### Response
> This has been provided in `responses/token.json`

> ### /menus
> #### Request Type
> `GET`
> #### Headers
> Authorization:
> | Name          | Value          |
> | ------------- | -------------- |
> | Authorization | Bearer {token} |
> #### Response
> This has been provided in `responses/menus.json`

> ### /menu/{menu_id}/products
> #### Request Type
> `GET`
> #### Headers
> Authorization:
> | Name          | Value          |
> | ------------- | -------------- |
> | Authorization | Bearer {token} |
> #### Response
> The list of products for the `Takeaway` menu has been provided in `responses/menu-products.json`

## Scenario 2

A customer has been in touch and advised you that product with id 84 in menu 7 has the wrong name. The product is currently named 'Chpis' but it should be named 'Chips'.

Using any of the API endpoints from Scenario 1 and the new method detailed below, write code to demonstrate this item being updated in the 'Great Food Ltd' API.

### Expected output

Proof that the API request has been successful.

> ### /menu/{menu_id}/product/{product_id}
> #### Arguments
> Product model as described in the `GET /menu/{menu_id}/products` response
> #### Request Type
> `PUT`
> #### Headers
> | Name          | Value          |
> | ------------- | -------------- |
> | Authorization | Bearer {token} |

## When you're done

Please zip up your solution and email it to eng-tests@wi-q.com.

---

## Solution Notes

This submission is implemented in Python with FastAPI. I used AI development tooling while building it, and reviewed/verified the generated code with tests and linting.

### What is included

- A FastAPI API that exposes the exact endpoint names from the brief.
- SQLite persistence through SQLAlchemy.
- Startup seeding from the provided response-shaped JSON files.
- A real client-credentials auth flow backed by a seeded `clients` table.
- Client permissions stored as JSON scope arrays.
- One-hour signed JWT bearer tokens containing `client_id`, `scope`, and `grant_type`.
- Modular feature boundaries for auth, menus, and products.
- Tests for routes, services, repositories, database seeding, JWT claims, and product updates.
- A generated OpenAPI spec for manual testing.

### Project structure

```text
app/
  api/                 Root router aggregation and health check
  core/                env config, database setup, SQLAlchemy tables, security
  modules/
    auth/              auth model, repository, service, router
    menus/             menu model, repository, service, router
    products/          product model, repository, service, router
docs/openapi.json      Generated OpenAPI schema
responses/             Great Food response-shaped payloads
seed/                  Internal app seed data, such as API clients
tests/                 Route, service, repository, auth, and seeder tests
```

Each feature module owns its own models, repository, service, dependencies, and router. Services depend on exactly one repository, and repositories are scoped to exactly one model type.

The `responses/` files are kept in the same response shape as the task brief:

- `responses/token.json`
- `responses/menus.json`
- `responses/menu-products.json`

`seed/clients.json` is separate because it is application auth seed data, not a Great Food response file from the brief. It stores client identity, secret, and scope permissions only; `grant_type` comes from the token request and is copied into the JWT claim after validation. `seed/menu-product-sources.json` links response files to their parent menu, so products are seeded under a real menu relationship rather than assigned to a menu in code.

### Design notes

- `POST /auth_token` validates `client_id` and `client_secret` against the `clients` table, then validates the submitted `grant_type` as the supported client-credentials flow.
- Valid `client_credentials` requests receive a signed JWT that expires in 3600 seconds.
- Protected endpoints decode and validate the JWT, including the `grant_type=client_credentials` claim.
- JWT claims include scope as an array, while the token response keeps the task fixture shape with `scope` as a string.
- Products are related to their parent menu through a SQLAlchemy relationship and a `products.menu_id` foreign key.
- The product seeder reads `seed/menu-product-sources.json` to attach `responses/menu-products.json` to the `Takeaway` menu.
- Product services delegate product mutation to the repository; the repository owns product persistence/model construction.
- `GET /menus` returns the same top-level shape as `responses/menus.json`.
- `GET /menu/{menu_id}/products` returns the same top-level shape as `responses/menu-products.json`.
- `PUT /menu/{menu_id}/product/{product_id}` returns proof of the updated product in a `data` wrapper.

### Run locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

On startup, the application creates a local SQLite database and seeds it from `responses/` and `seed/`.

Configuration is loaded from `.env`. See `.env.example` for the required keys.

```env
DATABASE_PATH=great_food.sqlite3
RESPONSE_FIXTURES_PATH=responses
JWT_SECRET=replace-with-at-least-32-bytes-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_SECONDS=3600
```

### Endpoints

```http
POST /auth_token
Content-Type: application/x-www-form-urlencoded

client_secret=4j3g4gj304gj3&client_id=1337&grant_type=client_credentials
```

Validates the submitted client against the seeded `clients` table and checks that the submitted grant type is `client_credentials`, then returns a signed JWT bearer token that expires in one hour. Client scopes are stored as a JSON array and emitted as an array in JWT claims. The token response follows the field shape of `responses/token.json`, with a generated JWT replacing the sample token value.

```json
{
  "access_token": "jwt",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "catalogue"
}
```

Use it as `Authorization: Bearer {access_token}` for the protected endpoints below.

```http
GET /menus
Authorization: Bearer {access_token}
```

Returns menus using the same top-level shape as `responses/menus.json`.

```json
{
  "data": [
    {
      "id": 3,
      "name": "Takeaway"
    }
  ]
}
```

```http
GET /menu/3/products
Authorization: Bearer {access_token}
```

Returns products for the Takeaway menu using the same top-level shape as `responses/menu-products.json`.

```json
{
  "data": [
    {
      "id": 4,
      "name": "Chips"
    }
  ]
}
```

```http
PUT /menu/7/product/84
Content-Type: application/json
Authorization: Bearer {access_token}

{"name": "Chips"}
```

Renames product `84` in menu `7` from `Chpis` to `Chips`.

```json
{
  "data": {
    "id": 84,
    "name": "Chips"
  }
}
```

### Manual Testing

Use the generated OpenAPI file:

```text
docs/openapi.json
```

Or use the live docs while the app is running:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
```

### Test Coverage

The test suite is intentionally split by layer:

| Test file | Coverage |
| --- | --- |
| `tests/test_api_routes.py` | Route contracts, auth-token form flow, JWT-protected endpoints, response shapes matching `responses/*.json`, and product update error handling. |
| `tests/modules/auth/test_service.py` | Client-credentials validation, unsupported grant rejection, JWT generation, one-hour expiry, and required JWT claims including `grant_type=client_credentials` and array scopes. |
| `tests/modules/menus/test_repository.py` | SQLAlchemy menu repository reads seeded menu data from `responses/menus.json`. |
| `tests/modules/menus/test_service.py` | Menu service lookup behavior and missing-menu errors. |
| `tests/modules/products/test_repository.py` | SQLAlchemy product repository reads seeded products, verifies products are attached to the `Takeaway` menu relationship, and persists update/upsert operations. |
| `tests/modules/products/test_service.py` | Product service listing and rename behavior. |

### Quality checks

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
```

Current verification:

- `16` pytest tests cover auth, route contracts, services, repositories, seeding, relationships, and update behavior.
- Ruff linting passes.
- OpenAPI is regenerated at `docs/openapi.json`.
