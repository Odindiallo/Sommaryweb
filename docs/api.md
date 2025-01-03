# API Documentation

The Documentation Management System provides a RESTful API for managing documents, categories, and attachments.

## Authentication

All API endpoints require authentication. Use session-based authentication or token authentication.

### Session Authentication

Log in through the web interface at `/users/login/`.

### Basic Authentication

Send username and password with each request:
```
Authorization: Basic <base64-encoded-credentials>
```

## API Endpoints

### Documents

#### List Documents
```http
GET /api/documents/
```
Query Parameters:
- `search`: Search in title and content
- `category`: Filter by category slug
- `tags`: Filter by tag names (comma-separated)
- `ordering`: Order by field (prefix with - for descending)

#### Create Document
```http
POST /api/documents/
```
Request Body:
```json
{
    "title": "Document Title",
    "content": "Document Content",
    "category": {
        "name": "Category Name",
        "description": "Category Description"
    },
    "is_public": true,
    "tags": ["tag1", "tag2"]
}
```

#### Get Document
```http
GET /api/documents/{slug}/
```

#### Update Document
```http
PUT /api/documents/{slug}/
```

#### Delete Document
```http
DELETE /api/documents/{slug}/
```

### Categories

#### List Categories
```http
GET /api/categories/
```

#### Create Category
```http
POST /api/categories/
```
Request Body:
```json
{
    "name": "Category Name",
    "description": "Category Description"
}
```

### Attachments

#### List Attachments
```http
GET /api/attachments/
```
Query Parameters:
- `document`: Filter by document ID

#### Create Attachment
```http
POST /api/attachments/
```
Form Data:
- `document`: Document ID
- `file`: File to upload
- `name`: Optional file name

## Response Format

Successful responses follow this format:
```json
{
    "count": 123,
    "next": "http://api.example.org/accounts/?page=4",
    "previous": "http://api.example.org/accounts/?page=2",
    "results": [
        {
            "id": 1,
            "title": "Document Title",
            ...
        }
    ]
}
```

## Error Handling

Errors follow this format:
```json
{
    "detail": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 20 requests per minute for anonymous users
