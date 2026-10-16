# MacLean v0.9 research checkpoint

**Branch:** `research/decision-engine-regenerability-v0.9` (based on v0.8).  
**Product principle (frozen):** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

User corrected the excessively cautious strategy: ordinary, known regenerable caches should be recommended without a blanket veto based on whether npm, Codex or Cursor is running. Only a validated *operation-specific* safety mechanism should decide actual execution. Do not require elaborate E3 proof for every known package cache or log.

History: v0.1 synthetic evaluator; v0.2 real blind model pilot without Gold; v0.3 uv native isolated E2; v0.4 operation-scope/TOCTOU; v0.5 native browser-list false positives; v0.6/0.7 Playwright client evidence; v0.8 Smart Selection and original executor preview; **v0.9 regenerability first**.

**Measured Mac result:** 32 original 1.4.0 read-only candidates; 7 DEFAULT **3,148.1 MiB**, 15 OPTIONAL **2,824.6 MiB**, 10 BLOCKED **3,184.4 MiB**. 19 recommendation candidates previously suppressed by `RELATED_PROCESS_RUNNING`. npm 12.2.0 real read-only npx enumeration matched 11/11 leaf keys. 29/29 local unit tests passed.

**Hard boundary:** This is the revised recommendation classifier, not a new production executor. Every newly recommended item has `execution_ready=false`; native adapters have not yet been safety-tested or added to v1.4.0. No actual cache deletion, `npm cache verify`, `npm cache clean`, `npm cache npx rm` or `uv cache prune` on user data. The existing 70.3 MiB unapproved preview remains unchanged. Gross allocated candidate size is not APFS net reclaim.

**Next:** implement and isolate-test exact npm/npx/uv native adapters, map native npx keys, investigate concurrency and runtime binaries separately, then revise executor under full original privacy/path/user-confirmation rules. Keep Profile, offline data and newest runtime version protections. Maintain one understandable default/optional selection batch.

Source files: `research/decision-engine-v0.9/regenerability_policy.py`, `render_stdin.py`, `test_regenerability_v09.py`, `RESULTS-v0.9.md`.

### Latest addition

`native_method_proposal.py` plus `test_native_method_v09.py` build non-executable typed proposals; **29/29** local tests. CI now checks both test modules. The proposal is not an executor integration; first implement and verify native isolated adapters before actual cleanup readiness.
