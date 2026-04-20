# yakit-hotpatch-skill

> Reusable Yakit MITM hotpatch skill for Yaklang, focused on wrapped JSON decrypt-repack and old-style request re-sign templates.

## Overview

`yakit-hotpatch-skill` is a reusable skill pack for building and debugging **Yakit MITM hotpatch scripts in Yaklang**.

It is designed for two common traffic-handling workflows:

- **Wrapped JSON decrypt-repack**
  Show encrypted request or response data as plaintext in the MITM editor, then pack it back before release.
- **Old-style request re-sign**
  Keep request bodies readable and only rebuild fields such as `sign`, `token`, or checksums in `beforeRequest`.

This repository is meant to save time when you need a reliable starting point instead of rebuilding hotpatch structure from scratch every time.

## Best For

Use this repository when you need to:

- fix Yakit hotload compile errors caused by JavaScript being pasted into Yaklang
- expose encrypted mini-program traffic as plaintext in the editor
- rebuild wrapped fields such as `bizContent`, `signContent`, or similar ciphertext containers
- preserve response wrapper formats while editing only the inner plaintext
- recalculate request signatures for form bodies such as `sign`, `token`, and other digest fields

## Included Templates

### 1. Generic wrapped JSON MITM template

**File**

`references/examples/generic-wrapped-json-mitm-hotpatch.yak`

**Use it when**

- ciphertext is stored inside a JSON field
- requests and responses should be shown as plaintext in the editor
- release-time traffic must be rebuilt into the original wrapper

**What you need to replace**

- encrypted field name
- `decryptPayload(...)`
- `encryptPayload(...)`
- optional marker headers

---

### 2. Generic request re-sign template

**File**

`references/examples/generic-request-resign-hotpatch.yak`

**Use it when**

- traffic is already plaintext
- request body is usually `application/x-www-form-urlencoded`
- only fields such as `sign` need recalculation before upstream

**What you need to replace**

- `targetPath`
- `calcSign(params)`
- optional default field handling

---

### 3. Concrete wrapped JSON example

**File**

`references/examples/bizcontent-mitm-hotpatch.yak`

This is a concrete AES-ECB plus Base64 example for a wrapped `bizContent` workflow.

## Quick Start

### Option A: Wrapped JSON decrypt-repack

1. Copy `generic-wrapped-json-mitm-hotpatch.yak`
2. Replace the encrypted field name
3. Implement `decryptPayload(...)`
4. Implement `encryptPayload(...)`
5. Load the script into Yakit MITM hotpatch
6. Confirm the request enters the editor as plaintext
7. Confirm the released traffic is packed back correctly

### Option B: Request re-sign

1. Copy `generic-request-resign-hotpatch.yak`
2. Set `targetPath`
3. Implement `calcSign(params)`
4. Load the script into Yakit MITM hotpatch
5. Modify the request as needed
6. Release and verify that `sign` was rebuilt

## Repository Structure

```text
yakit-hotpatch-skill/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── patterns.md
    ├── troubleshooting.md
    └── examples/
        ├── generic-wrapped-json-mitm-hotpatch.yak
        ├── generic-request-resign-hotpatch.yak
        └── bizcontent-mitm-hotpatch.yak
```

## Common Problems

### Hotpatch compile error

If logs mention tokens such as:

- `const`
- `require("crypto")`
- `function tryParseJSON`

then the script was written in JavaScript and Yakit never loaded it.

### Request is still encrypted in the editor

Check these in order:

1. whether the hotpatch actually loaded
2. whether the path filter matched
3. whether the wrapper field name is correct
4. whether ciphertext is Base64 or hex

### Request breaks after release

Check:

1. whether `beforeRequest` rebuilt the wrapper
2. whether marker headers were removed
3. whether `poc.FixHTTPRequest(...)` was called

### Response cannot be returned to the client

Check:

1. whether the original response wrapper was cached
2. whether flow IDs are stable
3. whether only the encrypted field was replaced during re-pack

## Reference Notes

For more detail, read:

- `references/patterns.md`
- `references/troubleshooting.md`

## Notes

- This repository focuses on Yakit MITM hotpatch usage in **Yaklang**
- The templates are intended to be copied and adapted
- Always verify encoding and signing assumptions with a real sample before debugging hook behavior
