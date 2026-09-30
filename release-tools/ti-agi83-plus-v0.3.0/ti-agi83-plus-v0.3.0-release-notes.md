<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# TEXTERMENTALITY™ · TI-AGI83+

**A local spreadsheet bot with persistent geometric memory, provable repairs, and an unreasonable amount of confidence.**

Authorship lineage: **Frazer Σ Love ACO-Σ; Sara ΣΩ**. Version **0.3.0**.

The calculator face and trash talk survive. Underneath: a complete local service, SQLite persistence, exact Decimal arithmetic, imported CSV work surfaces, related-error guidance, traceable incidents, forward undo, a visible conductance lattice, and three calculator-era games with local scores.

![TI-AGI83+ running with persistent geometric memory](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/ti-agi83-desktop.png)

## Run it

Download this demo directory or the standalone release package. Python 3.10 or later is required.

```bash
python -m venv .venv
# Linux / WSL / macOS
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
python -m tiagi83 --open
```

Open **http://127.0.0.1:8383**. The default database is `~/.ti-agi83/work.sqlite`. Stop with Ctrl+C; restart with the same command to retain work and memory.

For the accelerated backend:

```bash
python -m pip install '.[accelerated]'
python -m tiagi83 --backend jax --open
```

`--backend auto` uses JAX when installed and NumPy otherwise. `--backend numpy` explicitly selects the reference backend. `--state /path/to/work.sqlite` selects a separate workspace. No API key, model, account, cloud service, or paid compute is required. Initial dependency installation requires package access; ordinary use is local.

## Try the memory, not just the attitude

1. **AUDIT** the invoice sample. Its cable total is wrong.
2. **REPAIR** it. The total becomes **32.00**.
3. Choose **Restore sample as new sheet** and audit the new sheet.
4. Inspect **Related incident**: it retrieves the earlier corrected error. Expand **Why this suggestion?** to compare transport distance under learned and flat geometry.
5. Choose **GRAPH**. The 8×8 lattice and fixed-probe ablation expose a persistent geometric response difference.
6. Choose **TRACE**. The original error remains visible after repair.
7. Close/restart the app. Sheets, incidents and conductance are still present.

The new invoice is calculated from its own inputs. A previous total is never copied into a new task as if memory made it correct.

## What it does

| Workflow | Useful behavior |
|---|---|
| Invoice | Whole nonnegative quantities × cent-denominated prices; exact per-row totals |
| Inventory | Whole stock values; Used ≤ Starting; remaining stock checks |
| Tax receipt | Cent-denominated amount × (1 + decimal tax rate), per-row half-up rounding |
| CSV import | Quoted CSV parsing, exact schema headers, 1–2000 rows, visible editable values |
| Repair | Recompute verified arithmetic fixes; stale sheet/audit rejection; atomic commit |
| Memory | Workflow-scoped conductance deformation, geometry-dependent related-incident retrieval |
| GRAPH / TRACE | Exact current lattice, controlled flat comparison, preserved incident evidence |
| Undo | Restore prior table values as a further event; retain error memory and ancestry |
| Export | CSV with formula-like text escaped; full JSON history with sheets, geometry, audits, game scores and receipts |
| Receipt verification | Local hash-chain consistency and geometric-state integrity checks |

Empty names, duplicate labels, malformed values and invalid ranges require human input. The bot never guesses them. Edits save before an audit, export or sheet switch. Audit is idempotent for one unchanged sheet revision; clicking it twice does not create two scars. A later edited/reverted revision is a new observation.

CSV headers must be exactly one of:

```csv
Item,Qty,Unit price,Line total
Part,Starting,Used,Remaining
Expense,Amount,Tax rate,Total
```

Choose the matching schema before import. Amounts use plain decimals without currency symbols or thousands separators. Rates use fractions (`0.07` = 7%). Inputs are bounded to absolute value ≤1,000,000,000 and at most eight decimal places; applicable money inputs require cent precision. Totals compare exactly, so an extra fractional cent is not silently hidden.

## Games: a proper calculator distraction

Choose **Games**, then **Snake**, **Falling Blocks** or **Pong**. These are original browser implementations, inspired by TI-83+ community games, on a 96×64 monochrome canvas. They do not include TI firmware or copied community game code.

| Game | Controls | Saved record |
|---|---|---|
| Snake | Arrows / WASD, or touch arrows | Food score; avoid walls and your body |
| Falling Blocks | Left/right move, up rotates, down soft-drops, Space hard-drops; touch controls | Drop/line-clear score, increasing levels |
| Pong | Up/down / W/S, or hold touch arrows | Longest rally; match ends at five points |

Start, pause/resume, restart and switch back to Work at any time. **P** pauses/resumes; **Escape** pauses. Switching modes saves your edits and pauses the game. Completed games save scores and play counts to the same local database, with idempotent score retries. An unfinished game is abandoned on restart or reload. Scores are self-reported local records, not competitive verification. Games do not change table incidents or geometric memory.

![Falling Blocks on the local arcade surface](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/ti-agi83-arcade-desktop.png)

## Next: CRM and Office-style tools

The next planned module is a CRM bot for contacts, companies, deals, notes and follow-ups. Document, spreadsheet and presentation workflows follow: DOCX/PDF, XLSX and PPTX output, local history, templates and inspectable evidence. See [OFFICE_EXPANSION.md](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/OFFICE_EXPANSION.md) for the sequence and completion checks. These modules are **planned**, and are not included in this release.

## Where the geometric memory comes from

This is a **bounded standalone descendant** of the BLOOMCORE R20 periodic conductance-memory relations in `bloomcore/fields.py`. It preserves the numerical law:

$$
p_x' = p_x + 0.04\,|u-\operatorname{roll}_x(u)|\,(2-p_x),
\qquad
p_y' = p_y + 0.04\,|u-\operatorname{roll}_y(u)|\,(2-p_y).
$$

The retained conductance grids change the later response to a matched cue through periodic finite-volume transport. The fixed query begins from the same working input under learned geometry and under flat geometry. Geometry is loaded from committed state; it is not reconstructed from chat logs or receipts.

**Declared application extensions:** typed errors are projected onto a signed sparse 8×8 field by kind, column, sign and relative magnitude. Transported query/candidate responses rank related incidents of the same kind. Incident text, timestamps and repair status are separately stored evidence. Row order is deliberately absent from the error projection. Each workflow has its own lattice.

This supplies a real, inspectable geometry-dependent retrieval path. It does **not** demonstrate semantic historical authentication, general memory capacity, native BLOOMCORE admission, or the full R20 torus/Pyra/shell/MIRRORSEED system. It preserves the original memory research's distinction between retained numerical consequences and robust semantic recall. The source mapping, controls, known limits and exact source hashes are in [GEOMETRIC_MEMORY.md](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/GEOMETRIC_MEMORY.md) and [SOURCE_PINS.json](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/SOURCE_PINS.json).

## Evidence

See [BUILD_RECEIPT.json](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/BUILD_RECEIPT.json) for the measured release results and [LINEAGE.md](https://github.com/dkl101001/BLOOMCORE-/blob/ti-agi83-plus-v0.3.0/demos/ti-agi83-plus/docs/LINEAGE.md) for the prototype/source relation. Tests include Decimal rounding, invalid inputs, no invented values, stale-state refusal, all-surface rollback, restart, useful historical guidance, unchanged current arithmetic, geometry ablation, receipt independence, scope isolation, and CPU backend parity. Arcade tests cover movement, collision, line clears, rotation, score persistence, idempotency, transaction rollback and v0.2 database compatibility. Browser smoke exercises the actual service, all three games, pause/resume, keyboard/touch controls, mode switching, score reload, and work/geometry isolation.

```bash
python -m pip install '.[test,accelerated]'
python -m pytest -q
node --test tests/test_arcade.cjs
```

Optional browser test: install Playwright through npm, install its Chromium, then run `node tests/browser_smoke.cjs` from a fresh test workspace. It creates a disposable local database; set `TI_TEST_STATE` to a fresh path for repeated runs. The browser suite expects JAX and uses the actual loopback API.

Build the deterministic standalone source archive with `python tools/package_release.py`. Its `MANIFEST.sha256.json` binds every packaged file except the manifest itself. Release assets include the archive, detached SHA-256, and clean-extraction verification record. These are byte checks, not external authentication.

## Local custody and recovery

The server binds only to `127.0.0.1`, validates Host/Origin, and requires a process-local session token for writes. It performs no external requests. The voice cannot alter arithmetic, execute scripts or grant permissions. Receipts detect local inconsistency; an attacker able to rewrite the entire database can also forge a new internally consistent chain. This is not an externally authenticated ledger.

**Export full history** produces inspectable JSON. For a byte-preserving backup, stop the app and copy `work.sqlite` together with any remaining `work.sqlite-wal` and `work.sqlite-shm` files. Restore the copies to a separate directory and launch with `--state` pointing to the copied database. Keep original files until restoration is checked. There is no automatic JSON-import/migration claim.

The service is a desktop research application; it has not been hardened for multiuser or internet hosting. It has no email, bookings, financial-account access, autonomous action, or LLM integration. Windows/WSL installation instructions are provided; this release's execution evidence is Linux CPU.

## License and publication

AGPL-3.0-only, following BLOOMCORE's default license for integrated runtimes. This demo adds source code under `demos/ti-agi83-plus/`. The second publication is a tagged GitHub Release with this README as the release body and a standalone source package. The exact original `TI-AGI83+.html` is preserved in `lineage/`.

**No scars yet. The machine is almost disappointed.**
