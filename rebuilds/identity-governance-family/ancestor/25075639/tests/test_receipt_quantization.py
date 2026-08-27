from bloomcore_nlse_antigovernor.receipts.build import build_anti_governor_receipts


def test_receipts_hash_is_stable_under_tiny_float_noise():
    # Two payload series that differ by tiny epsilon should hash identically after quantization.
    V_prev_a = [1.0000000001, 1.1]
    V_curr_a = [0.9999999999, 1.2]
    dV_a = [V_curr_a[0] - V_prev_a[0], V_curr_a[1] - V_prev_a[1]]
    tau_a = [0.0, 0.0]
    viol_a = [True, False]

    V_prev_b = [1.0000000002, 1.1 + 1e-12]
    V_curr_b = [0.9999999998, 1.2 - 1e-12]
    dV_b = [V_curr_b[0] - V_prev_b[0], V_curr_b[1] - V_prev_b[1]]
    tau_b = [0.0, 0.0]
    viol_b = [True, False]

    rA = build_anti_governor_receipts(V_prev=V_prev_a, V_curr=V_curr_a, dV=dV_a, tau_export=tau_a, violation=viol_a)
    rB = build_anti_governor_receipts(V_prev=V_prev_b, V_curr=V_curr_b, dV=dV_b, tau_export=tau_b, violation=viol_b)

    assert rA[0]["hash"] == rB[0]["hash"]
    assert rA[1]["hash"] == rB[1]["hash"]
