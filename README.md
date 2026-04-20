# yakit-hotpatch-skill

Reusable Yakit MITM hotpatch skill for Yaklang, focused on wrapped JSON decrypt-repack and old-style request re-sign templates.

## What this repository is for

This skill helps you build and debug Yakit MITM hotpatch scripts in **Yaklang**.

It targets two high-frequency workflows:

1. **Wrapped JSON decrypt-repack**
   Request or response enters the MITM editor as plaintext, then gets packed back before release.
2. **Old-style request re-sign**
   Request body stays readable, and fields such as `sign` are rebuilt in `beforeRequest`.

## Best fit scenarios

Use this skill when you need to:

- fix Yakit MITM hotload compile errors caused by JavaScript being pasted into Yaklang
- expose encrypted mini-program traffic as plaintext in the editor
- rebuild wrapped fields such as `bizContent`, `signContent`, or similar ciphertext containers
- preserve response wrapper formats while editing inner plaintext
- recalculate form request signatures like `sign`, `token`, checksum fields, or day-based digests

## Repository layout

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
        ├── bizcontent-mitm-hotpatch.yak
        └── bizcontent_codec.py
```

## Included templates

### 1. Generic wrapped JSON MITM template

File:

- `references/examples/generic-wrapped-json-mitm-hotpatch.yak`

Use it when:

- ciphertext is stored inside a JSON field
- request and response should be shown as plaintext in the editor
- release-time traffic must be packed back into the original wrapper

You only need to replace:

- encrypted field name
- encrypt and decrypt helpers
- optional marker header names

### 2. Generic request re-sign template

File:

- `references/examples/generic-request-resign-hotpatch.yak`

Use it when:

- traffic is already plaintext
- request body is usually form-urlencoded
- only fields like `sign` need to be recalculated before upstream

You only need to replace:

- target path
- `calcSign(params)` logic
- optional default field handling

### 3. Concrete example

File:

- `references/examples/bizcontent-mitm-hotpatch.yak`

This is a concrete AES-ECB plus Base64 example for a wrapped `bizContent` workflow.

### 4. Local verification helper

File:

- `references/examples/bizcontent_codec.py`

Use it to verify ciphertext encoding and algorithm assumptions outside Yakit before writing the final hotpatch.

## Quick start

### Wrapped JSON flow

1. Copy `generic-wrapped-json-mitm-hotpatch.yak`
2. Replace the encrypted field name
3. Implement `decryptPayload(...)`
4. Implement `encryptPayload(...)`
5. Load into Yakit MITM hotpatch
6. Verify request enters editor as plaintext
7. Verify release-time traffic is packed back correctly

### Request re-sign flow

1. Copy `generic-request-resign-hotpatch.yak`
2. Set `targetPath`
3. Implement `calcSign(params)`
4. Load into Yakit MITM hotpatch
5. Modify the request as needed
6. Release and confirm `sign` was rebuilt

## Common troubleshooting

### Hotpatch compile error

If the log mentions tokens such as:

- `const`
- `require("crypto")`
- `function tryParseJSON`

the script was written in JavaScript and Yakit never loaded it.

### Request still looks encrypted in the editor

Check:

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

1. whether you cached the original response wrapper
2. whether flow IDs are stable
3. whether only the encrypted field was replaced during re-pack

For more detail, read:

- `references/patterns.md`
- `references/troubleshooting.md`

## Notes

- This repository focuses on Yakit MITM hotpatch usage in **Yaklang**
- The templates are meant to be copied and adapted, not used unchanged
- Always verify encoding and signing assumptions with a real sample before debugging hook behavior
