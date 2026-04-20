---
name: yakit-hotpatch-skill
description: Use when creating, fixing, or reviewing Yakit MITM hotpatch scripts in Yaklang, especially for encrypted mini-program traffic, bizContent-style request/response wrapping, old-style request re-signing, or compile/debug issues where JavaScript was pasted into Yakit by mistake.
---

# Yakit Hotpatch Skill

## Overview

This skill is for building reliable Yakit MITM hotpatch scripts in **Yaklang**.

Use it for two common patterns:

1. **Interactive decrypt-edit-reencrypt**
   Request or response enters the MITM editor as plaintext, and is packed back before release.
2. **Old-style request re-signing**
   Keep the body human-readable or form-encoded, and only recompute fields like `sign` in `beforeRequest`.

## When to Use

Use this skill when you need to:

- fix Yakit hotload compile errors caused by pasting JavaScript or Node code into MITM hotpatch
- reverse encrypted mini-program traffic and expose plaintext in the editor
- rebuild wrapped request bodies such as `{"bizContent":"..."}` before upstream
- rebuild wrapped response bodies before returning them to the client
- auto-recalculate request signatures for form requests such as `sign`, `token`, or checksum fields
- debug why hijacked traffic still appears encrypted or why release-time re-pack fails

Do not use this skill for Burp extensions, Frida hooks, or non-Yakit proxy tooling.

## Core Rules

### 1. Yakit MITM hotpatch uses Yaklang, not JavaScript

If logs show tokens like:

- `const`
- `function tryParseJSON`
- `require("crypto")`

the script never loaded. Fix the language first.

### 2. Choose the correct hotpatch shape

#### A. Interactive decrypt-edit-reencrypt

Use this for encrypted JSON wrappers.

Typical hook layout:

- `hijackHTTPRequest` and `hijackRequest`
  - decrypt request for editor view
- `beforeRequest`
  - re-encrypt modified request before upstream
- `hijackHTTPResponseEx` and `hijackResponseEx`
  - decrypt response for editor view
- `afterRequest`
  - re-encrypt modified response before client

Use marker headers such as:

- `X-Yak-...-Plain`
- `X-Yak-...-Flow`

These make request and response re-pack deterministic.

#### B. Old-style request re-signing

Use this when traffic is already readable and only `sign` must be recalculated.

Typical hook layout:

- `hijackHTTPRequest`
  - pass through
- `beforeRequest`
  - parse body, recompute fields, fix packet
- response hooks
  - usually pass through

## Workflow

### Step 1. Confirm body type and wrapper

Identify all of the following:

- content type
  - JSON
  - form-urlencoded
  - multipart
- encrypted field name
  - `bizContent`
  - `signContent`
  - custom field
- ciphertext encoding
  - Base64
  - hex
  - raw bytes
- whether both request and response use the same wrapper

Never assume hex. Verify with a known sample.

### Step 2. Confirm algorithm details

Recover the exact tuple:

- algorithm
- mode
- padding
- key
- IV if any
- output encoding

Examples:

- `AES-128-ECB + PKCS7 + Base64`
- `DES-ECB + PKCS7 + Base64`
- `MD5(...).upper()` for request signatures

### Step 3. Build helper functions first

Keep helpers small and deterministic:

- JSON parse helper
- compact JSON helper
- encrypt helper
- decrypt helper
- request fix helper
- response fix helper

### Step 4. Rebuild the wrapper, not just the plaintext

For encrypted JSON traffic, preserve the server-side body shape.

Example:

```json
{"bizContent":"..."}
```

If responses contain extra fields besides ciphertext, cache the original response template and only replace the encrypted field during re-pack.

### Step 5. Recalculate packet metadata

After changing the body, always fix the packet:

- `poc.FixHTTPRequest(...)`
- `poc.FixHTTPResponse(...)`

For form bodies, use post-param helpers instead of manual string concatenation when available.

## Yaklang Patterns

### JSON wrapper decrypt for editor

```yak
obj, ok = tryParseJson(body)
if !ok || !("bizContent" in obj) {
    return packet, false
}

plain = decryptBizContent(obj["bizContent"])
packet = poc.ReplaceHTTPPacketBody(packet, plain)
packet = poc.ReplaceHTTPPacketHeader(packet, reqMarkerHeader, "1")
packet = poc.FixHTTPRequest(packet)
return packet, true
```

### JSON wrapper re-pack before upstream

```yak
plain = string(poc.GetHTTPPacketBody(packet))
newBody = json.dumps({
    "bizContent": encryptBizContent(plain),
})
packet = poc.ReplaceHTTPPacketBody(packet, newBody)
packet = poc.DeleteHTTPPacketHeader(packet, reqMarkerHeader)
packet = poc.FixHTTPRequest(packet)
return packet, true
```

### Form request re-sign

```yak
params = poc.GetAllHTTPPacketPostParams(packet)
params["sign"] = newSign
packet = poc.ReplaceAllHTTPPacketPostParamsWithoutEscape(packet, params)
packet = poc.FixHTTPRequest(packet)
return packet, true
```

## Common Failure Modes

### Hotload says compile error

Root cause:

- JavaScript or unsupported syntax was pasted into Yaklang

Action:

- rewrite in Yaklang
- re-check helper function names

### Traffic enters editor still encrypted

Root cause candidates:

- hooks never loaded
- wrong wrapper field
- wrong encoding assumption
- path filter did not match

Check:

- whether hotload log shows your custom startup log
- whether `hijackHTTPRequest` or `hijackHTTPResponseEx` actually ran

### Release-time request is broken

Root cause candidates:

- forgot to remove marker headers
- forgot to restore wrapped JSON body
- forgot `poc.FixHTTPRequest`

### Response cannot be re-packed

Root cause candidates:

- you replaced the whole response body but did not preserve the original wrapper
- no flow ID or template cache was kept

## Reverse Checklist

- verify whether ciphertext is Base64 or hex from a real sample
- verify the hook style before coding
- preserve request and response wrappers
- keep request and response marker headers minimal
- fix packet after every body rewrite
- add debug logs during iteration
- remove assumptions about timestamp fields until code proves them

## Reference Files

- `references/patterns.md`
  - reusable patterns for MITM hook layout, response template caching, and old-style request re-signing
- `references/troubleshooting.md`
  - compile, hook, encoding, and path-match troubleshooting notes
