# OpenAPI structural validation schema

`openapi-3.1.schema.json` is the unmodified official OpenAPI Initiative schema:

- Source and schema ID: https://spec.openapis.org/oas/3.1/schema/2025-02-13
- SHA-256: `66f9c674bff99e11d584e7c0162ac159218b9595f418fea9e443b2d78174d44c`
- Retrieved for F02-CONTRACT on 2026-11-04.

This is validation data, not an executable download. Tests run offline and pin
the original bytes. The official schema validates OpenAPI document structure;
separate Draft 2020-12 validation checks the component schemas/examples, and
`validate_bundle` checks cross-record semantics. The upstream document contains
its `$comment` and identifier. Upstream licensing is Apache-2.0 under the
[OpenAPI specification repository](https://github.com/OAI/OpenAPI-Specification/blob/main/LICENSE).
An unmodified copy is included as [LICENSE.openapi](LICENSE.openapi).
