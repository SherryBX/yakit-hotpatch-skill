# Troubleshooting

## Compile errors mentioning `const`, `require`, or JavaScript functions

Meaning:

- hotpatch is still JavaScript
- Yakit MITM never loaded the plugin

Fix:

- rewrite the script in Yaklang

## Request still encrypted in editor

Check in this order:

1. hotpatch actually loaded
2. path filter matched
3. body parser succeeded
4. wrapper field name is correct
5. ciphertext encoding assumption is correct

## Request leaves editor as plaintext and server rejects it

Check:

1. `beforeRequest` exists
2. marker header is present before release
3. encryption helper returns the expected encoding
4. body is wrapped back to the original JSON shape
5. `poc.FixHTTPRequest` was called

## Response cannot be edited safely

If the client expects an outer JSON wrapper, do not replace the whole response with plaintext permanently.

Use:

- a flow ID derived from the original request
- cached response template
- replace only the encrypted field during `afterRequest`

## Form request re-sign does nothing

Check:

1. request path match
2. content type really is form-urlencoded
3. expected params are present
4. packet post-param helpers are available in this Yakit build
5. request was fixed after rewriting

## Signature mismatch despite recalculation

Check:

1. field order in the raw signing string
2. uppercase vs lowercase MD5 output
3. whether user ID defaults to `0`
4. whether the formula uses `openid`, login `code`, or another identifier
5. whether date granularity is day-only
