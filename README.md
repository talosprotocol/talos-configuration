# Talos Configuration Service

Backend-for-Frontend (BFF) service for the Talos Configuration Control Plane.

## Features
-   **Validation**: Validates configuration against strict JSON Schema.
-   **Normalization**: Canonicalizes configuration using JCS (RFC 8785).
-   **management**: Handles drafts, history, and publishing.

## API
The API is defined in `contracts/openapi/configuration/v1/openapi.yaml`.

## Development
Run locally:
```bash
uvicorn main:app --reload
```

## License

Talos Configuration Service is distributed under the Apache License 2.0. See
`LICENSE` and `NOTICE` in this repository for attribution details.
