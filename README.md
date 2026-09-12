# Game Store Backend API

A RESTful backend for managing digital game products and purchases. The application imports product data from CSV, authenticates users with JSON Web Tokens (JWT), provides paginated product browsing, and creates order receipts.

## Technology Stack

- Python 3.14
- Django 5.2
- Django REST Framework
- PostgreSQL 18
- Simple JWT
- drf-spectacular (OpenAPI and Swagger UI)

## Features

- JWT login and token refresh
- Authentication required for product and order endpoints
- Paginated product listing
- Optional product filtering by location (`JO` or `SA`)
- Product details
- Purchase flow for one product per request
- Receipt retrieval restricted to the user who created the order
- CSV product import with validation and transaction rollback
- PostgreSQL database integration
- Swagger/OpenAPI documentation

## Database Design

### Product

Stores the imported game-item information:

- `id`
- `title`
- `description`
- `price`
- `location` (`JO` or `SA`)
- `created_at`

### Order

Stores each completed purchase:

- `id`
- `receipt_number` (unique UUID)
- `user`
- `product`
- `product_title`
- `product_location`
- `unit_price`
- `purchased_at`

The order stores a snapshot of the product title, location, and price. Therefore, an existing receipt remains historically correct if the product is changed later.

## Why PostgreSQL?

PostgreSQL was selected because it is a reliable open-source relational database with strong transaction support, constraints, indexing, and Django integration. Relational tables and foreign keys are a natural fit for users, products, and orders. Transactions are particularly useful for ensuring an incomplete purchase or invalid CSV import does not leave partial data in the database.

## Design Decisions and Assumptions

- React Context manages authentication state.
- Axios provides a shared API client and adds the JWT access token to requests.
- Session storage keeps authentication active for the current browser tab.
- React Router protects pages and redirects unauthenticated users.
- Parcel is used as the React build tool.
- The frontend assumes the Django API is available at the configured
  API_BASE_URL.

## Authentication

### Login

`POST /api/auth/login/`

Request:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Successful response (`200 OK`):

```json
{
  "refresh": "refresh-token",
  "access": "access-token"
}
```

Send the access token with protected requests:

```http
Authorization: Bearer access-token
```

### Refresh the access token

`POST /api/auth/refresh/`

```json
{
  "refresh": "refresh-token"
}
```

## API Endpoints

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| `POST` | `/api/auth/login/` | No | Validate credentials and return JWTs |
| `POST` | `/api/auth/refresh/` | No | Return a new access token |
| `GET` | `/api/products/` | Yes | Return paginated products |
| `GET` | `/api/products/{id}/` | Yes | Return one product |
| `POST` | `/api/orders/` | Yes | Purchase one product and create an order |
| `GET` | `/api/orders/{receipt_number}/` | Yes | Return the authenticated user's receipt |

## Product Listing

`GET /api/products/`

Supported query parameters:

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `page` | No | `1` | Requested page number |
| `page_size` | No | `10` | Records per page; maximum `100` |
| `location` | No | All | Filter by `JO` or `SA` |

Examples:

```text
GET /api/products/?page=1&page_size=10
GET /api/products/?location=JO
GET /api/products/?location=SA&page=2&page_size=5
```

A successful response uses Django REST Framework's pagination structure:

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": []
}
```

An unsupported location returns `400 Bad Request`.

## Product Details

`GET /api/products/{id}/`

Returns `200 OK` when the product exists and `404 Not Found` otherwise.

## Purchase and Receipt

### Create an order

`POST /api/orders/`

Request:

```json
{
  "product_id": 1
}
```

Successful response (`201 Created`):

```json
{
  "id": 1,
  "receipt_number": "d81140bb-f918-4631-8ac0-6aed50ca264f",
  "username": "your_username",
  "product_id": 1,
  "product_title": "Sword of Valor",
  "product_location": "JO",
  "unit_price": "150.00",
  "purchased_at": "2026-09-11T18:45:00Z"
}
```

An unknown `product_id` returns `400 Bad Request`. Each request accepts one product only.

### Retrieve a receipt

`GET /api/orders/{receipt_number}/`

The query is restricted to orders owned by the authenticated user. A missing receipt, or a receipt belonging to another user, returns `404 Not Found`.

## Error Responses

Common status codes include:

| Status | Meaning |
| --- | --- |
| `200 OK` | Successful read or authentication |
| `201 Created` | Order created successfully |
| `400 Bad Request` | Invalid input, location, or product ID |
| `401 Unauthorized` | Missing, expired, or invalid JWT |
| `404 Not Found` | Product or accessible receipt not found |


## Security Notes

- Database credentials and Django secrets are loaded from `.env`.
- `.env` and `.venv` must never be committed.
- Business endpoints require JWT authentication.
- Receipt queries are restricted to the authenticated user.
- Order creation uses a database transaction.
- The development server and `DEBUG=True` must not be used in production.
- A dedicated PostgreSQL application user should be used in production instead of `postgres`.

## Current Scope

The backend implements the API and database portion of the technical assignment. The React frontend is maintained as a separate project/module and will consume these endpoints.


## Author

Saif Al-Kurdi
