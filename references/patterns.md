# Patterns

## Pattern 1. Interactive encrypted JSON traffic

Use when request and response both wrap ciphertext in JSON.

### Structure

1. detect wrapper field in request body
2. decrypt body for editor
3. mark request as plaintext
4. re-encrypt in `beforeRequest`
5. decrypt response for editor
6. cache original response wrapper
7. re-encrypt only the ciphertext field in `afterRequest`

### Recommended hooks

- `hijackHTTPRequest`
- `hijackRequest`
- `beforeRequest`
- `hijackHTTPResponseEx`
- `hijackResponseEx`
- `afterRequest`

### Recommended state

- request marker header
- response marker header or shared marker
- flow ID header
- response template cache

## Pattern 2. Request-only form re-sign

Use when:

- traffic is already plaintext
- body is form-urlencoded
- only fields like `sign`, `token`, or checksum must be updated

### Structure

1. match target path
2. parse post params
3. recover or inject defaults for required fields
4. recompute `sign`
5. replace post params
6. fix request

Response path can stay pass-through.

### Recommended reusable template

- `references/examples/generic-request-resign-hotpatch.yak`

## Pattern 3. Base64 vs hex verification

Never guess.

### Quick checks

- ends with `=` often indicates Base64
- only `[0-9a-fA-F]` with even length often indicates hex
- verify by local decrypt script before writing hotpatch

## Pattern 4. Signature formulas

Treat signatures separately from ciphertext handling.

Common flow:

1. identify exact field order
2. identify constant salt
3. identify whether date granularity is day-only or includes time
4. verify with one known request

If a formula uses only day, month, year, changing minute values will not help.

## Pattern 5. Template selection

Use:

- `generic-wrapped-json-mitm-hotpatch.yak`
  - when ciphertext is wrapped inside JSON and editor should show plaintext
- `generic-request-resign-hotpatch.yak`
  - when traffic is already readable and only fields such as `sign` need rebuilding
