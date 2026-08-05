#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""spectral_authority_combined.py

BLOOMCORE Engine — Spectral Choice + Spectral Authority + Flight Recorder Link

Adds:
  - Δ^τ-SPECTRAL_LINK.v1 receipt: cross-links choice → packet_commit → step context
  - Wired to ReceiptHook (same seam), with hard "no arrays in receipts" enforcement

Design intent
-------------
This module is an OSS-safe seam that keeps *selection alive* while keeping
ECA/IP-bearing parameterization behind a `PacketRecipeProvider` boundary.

Receipts emitted here are non-leaking by construction: no raw arrays, ever.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Dict, Mapping, Optional, Protocol, Sequence, Tuple, List, Literal
import hashlib
import json
import time
import random

try:
    import numpy as _np  # used only for robust "no array in receipts" checks
except Exception:  # pragma: no cover
    _np = None

try:
    import jax
    import jax.numpy as jnp
except Exception:  # pragma: no cover
    jax = None
    jnp = None


# =========================
# Types + public primitives
# =========================

PacketKind = Literal["psi_drive"]
PotentialKind = Literal["abs", "abs2", "logabs2"]


@dataclass(frozen=True)
class SpectralPacketMeta:
    """Safe metadata surface for receipts/audits."""

    kind: PacketKind
    schema_v: str
    created_unix_s: int
    seed_tag: str
    authority_id: str
    packet_commit: str
    summary: Dict[str, float]


@dataclass(frozen=True)
class SpectralPacket:
    """Sealed packet. Raw arrays must never be serialized into receipts."""

    meta: SpectralPacketMeta

    omega: "jnp.ndarray"  # (N,)
    kx: "jnp.ndarray"     # (N,)
    ky: "jnp.ndarray"     # (N,)
    amp: "jnp.ndarray"    # (N,)
    phase: "jnp.ndarray"  # (N,)

    omega_bounds: Tuple[float, float]
    k_bounds: Tuple[float, float]
    amp_l1_max: float
    amp_linf_max: float
    friend_guard: float
    potential_kind: PotentialKind
    psi_gain: float


class ReceiptHook(Protocol):
    def emit(self, payload: Mapping[str, Any]) -> None:
        ...


# ===================================
# Spectral Choice (alive, non-leaking)
# ===================================


@dataclass(frozen=True)
class ChoiceCandidate:
    cid: str
    weight: float = 1.0
    tags: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SpectralChoiceConfig:
    novelty_alpha: float = 0.25
    epsilon: float = 1e-9
    softmax_temp: float = 1.0
    choose_top_p: float = 1.0
    seed_stream_tag: str = "choice"


@dataclass(frozen=True)
class SpectralChoiceState:
    novelty: Mapping[str, float]
    t: int

    def get_novelty(self, cid: str) -> float:
        return float(self.novelty.get(cid, 0.0))


@dataclass(frozen=True)
class ChoiceResult:
    chosen_cid: str
    probs: Dict[str, float]
    logits: Dict[str, float]
    rng_tag: str
    state_before_hash: str
    state_after_hash: str


def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _canon_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def hash_choice_state(st: SpectralChoiceState) -> str:
    payload = {"t": st.t, "novelty": {k: float(v) for k, v in sorted(st.novelty.items())}}
    return _sha256_hex(_canon_json(payload))


def _softmax(xs: List[float], temp: float) -> List[float]:
    if temp <= 0:
        raise ValueError("softmax_temp must be > 0")
    m = max(xs)
    exps = [pow(2.718281828459045, (x - m) / temp) for x in xs]
    s = sum(exps) if exps else 1.0
    return [e / s for e in exps]


def _top_p_truncate(cids: List[str], probs: List[float], top_p: float) -> Tuple[List[str], List[float]]:
    if top_p >= 1.0:
        return cids, probs
    pairs = sorted(zip(cids, probs), key=lambda x: x[1], reverse=True)
    kept: List[Tuple[str, float]] = []
    mass = 0.0
    for cid, p in pairs:
        kept.append((cid, p))
        mass += p
        if mass >= top_p:
            break
    total = sum(p for _, p in kept) or 1.0
    return [c for c, _ in kept], [p / total for _, p in kept]


def spectral_choose_readonly(
    *,
    cfg: SpectralChoiceConfig,
    st: SpectralChoiceState,
    candidates: Sequence[ChoiceCandidate],
    seed_material: str,
) -> Tuple[ChoiceResult, str]:
    if not candidates:
        raise ValueError("No candidates provided")

    seed = int(_sha256_hex(seed_material.encode("utf-8"))[:16], 16)
    rng = random.Random(seed)

    cids = [c.cid for c in candidates]
    logits_list: List[float] = []
    logits_map: Dict[str, float] = {}
    for c in candidates:
        novelty_penalty = cfg.novelty_alpha * st.get_novelty(c.cid)
        logit = float(c.weight) - novelty_penalty
        logits_list.append(logit)
        logits_map[c.cid] = logit

    probs_list = _softmax(logits_list, cfg.softmax_temp)
    cids2, probs2 = _top_p_truncate(cids, probs_list, cfg.choose_top_p)

    r = rng.random()
    acc = 0.0
    chosen = cids2[-1]
    for cid, p in zip(cids2, probs2):
        acc += p
        if r <= acc:
            chosen = cid
            break

    probs_map = {cid: float(p) for cid, p in zip(cids2, probs2)}

    before = hash_choice_state(st)
    st_after = apply_choice_spectral(cfg=cfg, st=st, chosen_cid=chosen)
    after = hash_choice_state(st_after)

    res = ChoiceResult(
        chosen_cid=chosen,
        probs=probs_map,
        logits={k: float(v) for k, v in logits_map.items()},
        rng_tag=f"{cfg.seed_stream_tag}:{seed_material[:24]}",
        state_before_hash=before,
        state_after_hash=after,
    )
    return res, chosen


def apply_choice_spectral(*, cfg: SpectralChoiceConfig, st: SpectralChoiceState, chosen_cid: str) -> SpectralChoiceState:
    decay = 0.98
    novelty2: Dict[str, float] = {cid: float(v) * decay for cid, v in st.novelty.items()}
    novelty2[chosen_cid] = float(novelty2.get(chosen_cid, 0.0)) + 1.0
    return SpectralChoiceState(novelty=novelty2, t=int(st.t) + 1)


def choice_receipt_payload(choice: ChoiceResult) -> Dict[str, Any]:
    return {
        "kind": "Δ^τ-CHOICE_SPECTRAL.v1",
        "chosen_cid": choice.chosen_cid,
        "probs": choice.probs,
        "logits": choice.logits,
        "rng_tag": choice.rng_tag,
        "state_before": choice.state_before_hash,
        "state_after": choice.state_after_hash,
    }


# ======================================
# Packet recipes (ECA seam; IP lives here)
# ======================================


class PacketRecipeProvider(Protocol):
    def materialize(
        self,
        *,
        cid: str,
        kind: PacketKind,
        ctx: Mapping[str, Any],
        key: "jax.Array",
    ) -> Dict[str, Any]:
        ...


# =========================================
# Spectral Authority (seal + validate + log)
# =========================================


@dataclass(frozen=True)
class SpectralAuthorityConfig:
    schema_v: str = "SPECTRAL_PACKET.v1"
    packet_kind: PacketKind = "psi_drive"
    authority_id: str = "OSS_AUTH.v1"
    forbid_arrays_in_receipts: bool = True


def _ensure_jax():
    if jnp is None or jax is None:
        raise RuntimeError("JAX is required for spectral packet operations")


def safe_packet_summary(pkt: SpectralPacket) -> Dict[str, float]:
    _ensure_jax()
    k_mag = jnp.sqrt(pkt.kx * pkt.kx + pkt.ky * pkt.ky)
    a = jnp.abs(pkt.amp)
    p = a / (jnp.sum(a) + 1e-12)
    entropy = -jnp.sum(p * jnp.log(p + 1e-12))
    return {
        "N": float(pkt.omega.shape[0]),
        "psi_gain": float(pkt.psi_gain),
        "amp_l1": float(jnp.sum(a)),
        "amp_l2": float(jnp.sqrt(jnp.sum(pkt.amp * pkt.amp))),
        "amp_linf": float(jnp.max(a)),
        "k_rms": float(jnp.sqrt(jnp.mean(k_mag * k_mag))),
        "omega_rms": float(jnp.sqrt(jnp.mean(pkt.omega * pkt.omega))),
        "amp_entropy": float(entropy),
    }


def assert_packet_constraints(pkt: SpectralPacket, *, friend: float) -> None:
    _ensure_jax()
    N = int(pkt.omega.shape[0])
    if N <= 0:
        raise ValueError("SpectralPacket N must be > 0")
    if pkt.kx.shape != (N,) or pkt.ky.shape != (N,) or pkt.amp.shape != (N,) or pkt.phase.shape != (N,):
        raise ValueError("SpectralPacket arrays must all be shape (N,)")

    w_min, w_max = pkt.omega_bounds
    k_min, k_max = pkt.k_bounds
    k_mag = jnp.sqrt(pkt.kx * pkt.kx + pkt.ky * pkt.ky)
    a = jnp.abs(pkt.amp)

    if bool(jnp.any(~jnp.isfinite(pkt.omega))) or bool(jnp.any(~jnp.isfinite(k_mag))) or bool(jnp.any(~jnp.isfinite(a))):
        raise ValueError("SpectralPacket contains non-finite values")

    if bool(jnp.any(pkt.omega < w_min)) or bool(jnp.any(pkt.omega > w_max)):
        raise ValueError("omega violates omega_bounds")
    if bool(jnp.any(k_mag < k_min)) or bool(jnp.any(k_mag > k_max)):
        raise ValueError("k violates k_bounds")

    if float(jnp.sum(a)) > float(pkt.amp_l1_max) + 1e-9:
        raise ValueError("amp violates amp_l1_max")
    if float(jnp.max(a)) > float(pkt.amp_linf_max) + 1e-9:
        raise ValueError("amp violates amp_linf_max")

    _ = friend  # friend guard behavior handled upstream


def compute_packet_commit(pkt: SpectralPacket, *, secret_salt: bytes) -> str:
    _ensure_jax()

    def arr_bytes(x: "jnp.ndarray") -> bytes:
        x = jnp.asarray(x).astype(jnp.float32)
        hdr = f"f32|{x.shape}".encode("utf-8")
        return hdr + b"|" + bytes(x.tobytes())

    material = b"|".join(
        [
            pkt.meta.kind.encode("utf-8"),
            pkt.meta.schema_v.encode("utf-8"),
            pkt.meta.seed_tag.encode("utf-8"),
            pkt.meta.authority_id.encode("utf-8"),
            arr_bytes(pkt.omega),
            arr_bytes(pkt.kx),
            arr_bytes(pkt.ky),
            arr_bytes(pkt.amp),
            arr_bytes(pkt.phase),
            _canon_json(
                {
                    "omega_bounds": pkt.omega_bounds,
                    "k_bounds": pkt.k_bounds,
                    "amp_l1_max": float(pkt.amp_l1_max),
                    "amp_linf_max": float(pkt.amp_linf_max),
                    "friend_guard": float(pkt.friend_guard),
                    "potential_kind": pkt.potential_kind,
                    "psi_gain": float(pkt.psi_gain),
                }
            ),
            secret_salt,
        ]
    )
    return _sha256_hex(material)


def packet_receipt_payload(pkt: SpectralPacket) -> Dict[str, Any]:
    return {
        "kind": "Δ^τ-SPECTRAL_PACKET.COMMIT.v1",
        "schema_v": pkt.meta.schema_v,
        "packet_kind": pkt.meta.kind,
        "created_unix_s": pkt.meta.created_unix_s,
        "seed_tag": pkt.meta.seed_tag,
        "authority_id": pkt.meta.authority_id,
        "packet_commit": pkt.meta.packet_commit,
        "summary": dict(pkt.meta.summary),
        "constraints": {
            "omega_bounds": pkt.omega_bounds,
            "k_bounds": pkt.k_bounds,
            "amp_l1_max": float(pkt.amp_l1_max),
            "amp_linf_max": float(pkt.amp_linf_max),
            "friend_guard": float(pkt.friend_guard),
            "potential_kind": pkt.potential_kind,
            "psi_gain": float(pkt.psi_gain),
        },
    }


# ==========================================
# Flight Recorder link receipt (NEW)
# ==========================================


def spectral_link_receipt_payload(
    *,
    run_id: str,
    step_id: str,
    state_hash_in: str,
    friend: float,
    choice: ChoiceResult,
    packet_commit: str,
    packet_schema_v: str,
    packet_kind: str,
    authority_id: str,
) -> Dict[str, Any]:
    """Cross-links: choice → packet_commit → step context.

    NO arrays. This is the “flight recorder link” that lets you prove
    what happened without disclosing packet contents.
    """

    return {
        "kind": "Δ^τ-SPECTRAL_LINK.v1",
        "run_id": run_id,
        "step_id": step_id,
        "state_hash_in": state_hash_in,
        "friend": float(friend),
        "choice": {
            "chosen_cid": choice.chosen_cid,
            "state_before": choice.state_before_hash,
            "state_after": choice.state_after_hash,
        },
        "packet": {
            "schema_v": packet_schema_v,
            "packet_kind": packet_kind,
            "authority_id": authority_id,
            "packet_commit": packet_commit,
        },
    }


def _contains_array_like(x: Any) -> bool:
    if jnp is not None and isinstance(x, jnp.ndarray):
        return True
    if _np is not None and isinstance(x, _np.ndarray):
        return True
    if jax is not None and hasattr(jax, "Array") and isinstance(x, getattr(jax, "Array")):
        return True
    if isinstance(x, (list, tuple)):
        return any(_contains_array_like(v) for v in x)
    if isinstance(x, dict):
        return any(_contains_array_like(v) for v in x.values())
    return False


def assert_no_arrays_in_receipt(payload: Mapping[str, Any]) -> None:
    if _contains_array_like(payload):
        raise ValueError("Receipt payload contains array-like objects (leak risk)")


# ==========================================
# Combined engine (Choice + Authority + Link)
# ==========================================


@dataclass
class SpectralAuthorityCombined:
    choice_cfg: SpectralChoiceConfig
    choice_state: SpectralChoiceState
    authority_cfg: SpectralAuthorityConfig
    recipes: PacketRecipeProvider
    receipts: Optional[ReceiptHook] = None

    # Flight recorder identifiers (safe, host-chosen)
    run_id: str = "RUN.UNSET"

    def step(
        self,
        *,
        ctx: Mapping[str, Any],
        friend: float,
        candidates: Sequence[ChoiceCandidate],
        key: "jax.Array",
        secret_salt: bytes,
        seed_tag: str,
        state_hash_in: str,
        step_id: str,
    ) -> SpectralPacket:
        _ensure_jax()

        # 1) READ-ONLY choice
        seed_material = f"{self.choice_cfg.seed_stream_tag}|{seed_tag}|t={self.choice_state.t}|state={state_hash_in}"
        choice_res, chosen = spectral_choose_readonly(
            cfg=self.choice_cfg,
            st=self.choice_state,
            candidates=candidates,
            seed_material=seed_material,
        )

        # Choice receipt
        if self.receipts is not None:
            payload = choice_receipt_payload(choice_res)
            if self.authority_cfg.forbid_arrays_in_receipts:
                assert_no_arrays_in_receipt(payload)
            self.receipts.emit(payload)

        # 2) Advance choice state ONLY here
        self.choice_state = apply_choice_spectral(cfg=self.choice_cfg, st=self.choice_state, chosen_cid=chosen)

        # 3) Materialize recipe -> arrays + constraints
        mat = self.recipes.materialize(cid=chosen, kind=self.authority_cfg.packet_kind, ctx=ctx, key=key)

        meta = SpectralPacketMeta(
            kind=self.authority_cfg.packet_kind,
            schema_v=self.authority_cfg.schema_v,
            created_unix_s=int(time.time()),
            seed_tag=seed_tag,
            authority_id=self.authority_cfg.authority_id,
            packet_commit="UNCOMMITTED",
            summary={},
        )

        pkt = SpectralPacket(
            meta=meta,
            omega=mat["omega"],
            kx=mat["kx"],
            ky=mat["ky"],
            amp=mat["amp"],
            phase=mat["phase"],
            omega_bounds=tuple(mat["omega_bounds"]),
            k_bounds=tuple(mat["k_bounds"]),
            amp_l1_max=float(mat["amp_l1_max"]),
            amp_linf_max=float(mat["amp_linf_max"]),
            friend_guard=float(mat["friend_guard"]),
            potential_kind=mat["potential_kind"],
            psi_gain=float(mat["psi_gain"]),
        )

        # 4) Validate public constraints
        assert_packet_constraints(pkt, friend=friend)

        # 5) Seal + summary
        commit = compute_packet_commit(pkt, secret_salt=secret_salt)
        summary = safe_packet_summary(pkt)
        pkt2 = replace(pkt, meta=replace(pkt.meta, packet_commit=commit, summary=summary))

        # 6) Packet commit receipt
        if self.receipts is not None:
            payload = packet_receipt_payload(pkt2)
            if self.authority_cfg.forbid_arrays_in_receipts:
                assert_no_arrays_in_receipt(payload)
            self.receipts.emit(payload)

        # 7) Flight recorder link receipt (NEW)
        if self.receipts is not None:
            payload = spectral_link_receipt_payload(
                run_id=self.run_id,
                step_id=step_id,
                state_hash_in=state_hash_in,
                friend=friend,
                choice=choice_res,
                packet_commit=pkt2.meta.packet_commit,
                packet_schema_v=pkt2.meta.schema_v,
                packet_kind=pkt2.meta.kind,
                authority_id=pkt2.meta.authority_id,
            )
            if self.authority_cfg.forbid_arrays_in_receipts:
                assert_no_arrays_in_receipt(payload)
            self.receipts.emit(payload)

        return pkt2


# ==========================
# OSS demo recipe provider
# ==========================


@dataclass
class OSSRandomRecipeProvider:
    N: int = 64
    omega_bounds: Tuple[float, float] = (0.0, 200.0)
    k_bounds: Tuple[float, float] = (0.0, 40.0)
    amp_l1_max: float = 64.0
    amp_linf_max: float = 2.0
    friend_guard: float = 0.0
    potential_kind: PotentialKind = "abs2"
    psi_gain: float = 1.0

    def materialize(
        self,
        *,
        cid: str,
        kind: PacketKind,
        ctx: Mapping[str, Any],
        key: "jax.Array",
    ) -> Dict[str, Any]:
        _ensure_jax()
        h = int(_sha256_hex(cid.encode("utf-8"))[:8], 16)
        k1 = jax.random.fold_in(key, h)

        N = int(self.N)
        omega = jax.random.uniform(k1, (N,), minval=self.omega_bounds[0], maxval=self.omega_bounds[1])
        k2, k3, k4, k5 = jax.random.split(k1, 4)

        ang = jax.random.uniform(k2, (N,), minval=0.0, maxval=2.0 * jnp.pi)
        kmag = jax.random.uniform(k3, (N,), minval=self.k_bounds[0], maxval=self.k_bounds[1])
        kx = kmag * jnp.cos(ang)
        ky = kmag * jnp.sin(ang)

        amp = jax.random.normal(k4, (N,)) * 0.25
        amp = jnp.clip(amp, -self.amp_linf_max, self.amp_linf_max)
        l1 = jnp.sum(jnp.abs(amp)) + 1e-12
        scale = jnp.minimum(1.0, self.amp_l1_max / l1)
        amp = amp * scale

        phase = jax.random.uniform(k5, (N,), minval=-jnp.pi, maxval=jnp.pi)

        return {
            "omega": omega.astype(jnp.float32),
            "kx": kx.astype(jnp.float32),
            "ky": ky.astype(jnp.float32),
            "amp": amp.astype(jnp.float32),
            "phase": phase.astype(jnp.float32),
            "omega_bounds": self.omega_bounds,
            "k_bounds": self.k_bounds,
            "amp_l1_max": float(self.amp_l1_max),
            "amp_linf_max": float(self.amp_linf_max),
            "friend_guard": float(self.friend_guard),
            "potential_kind": self.potential_kind,
            "psi_gain": float(self.psi_gain),
        }
