# -*- coding: utf-8 -*-
"""Cross-package interop tests for the SDyPy ecosystem.

Exercises four end-to-end integration areas that span multiple sibling
packages, all accessed exclusively through the ``sdypy.*`` namespace.

Area 1 - lumped → EMA
    Build a 2-DOF lumped-parameter model, compute its analytical FRF, run
    LSCF identification, and verify that the identified natural frequencies
    and damping ratios match within 2% relative tolerance.

Area 2 - flagship chain
    pseudo_random excitation (sdypy.excitation) → time-domain response
    (sdypy.model.lumped) → H1 FRF estimate (sdypy.FRF) → EMA identification
    (sdypy.EMA).  Natural frequencies are verified within 5% rtol; damping
    identification is attempted but the test falls back to frequencies-only
    if instability is detected.

Area 3 - io round-trip
    FRF-like complex numpy array → UFF dataset-58 dict via
    ``sdypy.io.uff.prepare_58`` → write with ``sdypy.io.uff.UFF.write_sets``
    → ``read_sets`` → ``np.allclose`` against original data.

Area 4 - sep005 smoke
    Verify that ``sdypy.FRF.assert_sep005`` accepts a minimal valid sep005
    dict and raises on an invalid one (missing compulsory key).
"""

import numpy as np
import pytest

import sdypy


# ---------------------------------------------------------------------------
# Area 1: lumped → EMA
# ---------------------------------------------------------------------------

class TestLumpedToEMA:
    """Build 2-DOF model, compute analytical FRF, identify poles via LSCF."""

    @pytest.fixture(scope="class")
    def lumped_model(self):
        np.random.seed(6020)
        n_dof = 2
        masses = np.random.uniform(0.1, 1, n_dof)
        stiffnesses = np.random.uniform(500e3, 1e6, n_dof)
        damping = np.random.uniform(10, 100, n_dof)
        lm = sdypy.model.lumped.Model(
            n_dof=n_dof,
            mass=masses,
            stiffness=stiffnesses,
            damping=damping,
            boundaries="left",
        )
        return lm

    @pytest.fixture(scope="class")
    def ema_result(self, lumped_model):
        lm = lumped_model
        f_nat_true = lm.get_eig_freq()
        zeta_true = lm.get_damping_ratios()

        freq = np.linspace(30, 1500, 1000)
        # get_FRF_matrix returns (n_dof, n_dof, n_freq); slice input dof 0
        FRF_matrix = lm.get_FRF_matrix(freq=freq, frf_method="f")[0, :, :]

        model = sdypy.EMA.Model(
            frf=FRF_matrix,
            freq=freq,
            lower=freq[0],
            upper=freq[-1],
            pol_order_high=30,
        )
        model.get_poles(method="lscf", show_progress=False)
        model.select_closest_poles(f_nat_true)
        model.get_constants(whose_poles="own", FRF_ind="all")

        return model, f_nat_true, zeta_true

    def test_identified_nat_freq_within_2pct(self, ema_result):
        """Identified natural frequencies must lie within rtol=2e-2 of truth."""
        model, f_nat_true, _ = ema_result
        nat_freq_id = np.sort(model.nat_freq)
        f_true_sorted = np.sort(f_nat_true)
        np.testing.assert_allclose(
            nat_freq_id, f_true_sorted, rtol=2e-2,
            err_msg="Identified nat. freq. deviate more than 2%% from analytical values"
        )

    def test_identified_damping_within_2pct(self, ema_result):
        """Identified damping ratios must lie within rtol=2e-2 of truth."""
        model, f_nat_true, zeta_true = ema_result
        # sort by frequency order to align identified vs. analytical damping
        id_order = np.argsort(model.nat_freq)
        true_order = np.argsort(f_nat_true)
        nat_xi_id = model.nat_xi[id_order]
        zeta_sorted = zeta_true[true_order]
        np.testing.assert_allclose(
            nat_xi_id, zeta_sorted, rtol=2e-2,
            err_msg="Identified damping ratios deviate more than 2%% from analytical values"
        )


# ---------------------------------------------------------------------------
# Area 2: flagship end-to-end chain
# ---------------------------------------------------------------------------

class TestFlagshipChain:
    """pseudo_random → response → H1 FRF → EMA identification.

    Chain description
    -----------------
    1. Generate a pseudo-random excitation signal with ``sdypy.excitation.pseudo_random``.
    2. Compute the time-domain response of the 2-DOF lumped model with
       ``sdypy.model.lumped.Model.get_response``.
    3. Estimate the H1 FRF with ``sdypy.FRF.FRF``.
    4. Identify natural frequencies with ``sdypy.EMA.Model``.
    5. Assert frequencies within 5% rtol; damping within 5% rtol if stable.

    Notes
    -----
    - A long pseudo-random block (N_samples = 65536 at 5000 Hz) provides
      good frequency resolution and broadband content for both modes.
    - Damping from H1 of a single long segment can be noisy; the test
      falls back to frequencies-only when the identified damping values
      are unphysical (negative or > 0.5).  The reason is noted in the
      docstring per the task specification.
    """

    SAMPLING_RATE = 5000  # Hz
    N_SAMPLES = 65536     # long block; good resolution (~0.076 Hz/bin)
    SEED = 7777

    @pytest.fixture(scope="class")
    def chain_result(self):
        rng = np.random.default_rng(self.SEED)

        # --- 2-DOF model (same seed block keeps determinism) ---------------
        np.random.seed(6020)
        n_dof = 2
        masses = np.random.uniform(0.1, 1, n_dof)
        stiffnesses = np.random.uniform(500e3, 1e6, n_dof)
        damping = np.random.uniform(10, 100, n_dof)
        lm = sdypy.model.lumped.Model(
            n_dof=n_dof,
            mass=masses,
            stiffness=stiffnesses,
            damping=damping,
            boundaries="left",
        )
        f_nat_true = lm.get_eig_freq()  # (n_dof,)
        zeta_true = lm.get_damping_ratios()  # (n_dof,) - same model, single source of truth

        # --- pseudo-random excitation signal --------------------------------
        # sdypy.excitation.pseudo_random(N, rg) -> 1-D ndarray, peak = 1
        exc = sdypy.excitation.pseudo_random(N=self.N_SAMPLES, rg=rng)

        # --- compute time-domain response -----------------------------------
        # get_response returns (n_resp_dof, N_samples) by default
        resp = lm.get_response(
            exc_dof=np.array([0]),
            exc=exc,
            sampling_rate=self.SAMPLING_RATE,
            return_t_axis=False,
        )  # shape (2, N_SAMPLES)

        # --- H1 FRF estimate ------------------------------------------------
        # pyFRF interprets 2-D arrays as (n_measurements, time), so for a
        # SIMO system (1 exc DOF, 2 resp DOFs) we must pass 3-D arrays:
        #   exc:  (1 measurement, 1 exc DOF,  N_samples)
        #   resp: (1 measurement, 2 resp DOFs, N_samples)
        exc3d = exc[np.newaxis, np.newaxis, :]   # (1, 1, N)
        resp3d = resp[np.newaxis, :, :]          # (1, 2, N)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # suppress divide-by-zero at DC
            frf_obj = sdypy.FRF.FRF(
                sampling_freq=self.SAMPLING_RATE,
                exc=exc3d,
                resp=resp3d,
            )
        # get_FRF() returns (n_resp_dof, n_exc_dof, n_freq) = (2, 1, N_freq)
        H1 = frf_obj.get_FRF(type="H1")[:, 0, :]   # (2, N_freq)
        freq_axis = frf_obj.get_f_axis()             # (N_freq,)

        # restrict to frequency band covering both modes (30..1500 Hz)
        f_lo, f_hi = 30.0, 1500.0
        mask = (freq_axis >= f_lo) & (freq_axis <= f_hi)
        freq_band = freq_axis[mask]
        H1_band = H1[:, mask]                        # (2, N_band)

        # --- EMA identification ---------------------------------------------
        ema = sdypy.EMA.Model(
            frf=H1_band,
            freq=freq_band,
            lower=freq_band[0],
            upper=freq_band[-1],
            pol_order_high=40,
        )
        ema.get_poles(method="lscf", show_progress=False)
        ema.select_closest_poles(f_nat_true)
        ema.get_constants(whose_poles="own", FRF_ind="all")

        # damping stability check: unphysical values signal instability
        xi_id = ema.nat_xi
        damping_stable = bool(np.all(xi_id > 0) and np.all(xi_id < 0.5))

        return ema, f_nat_true, zeta_true, damping_stable

    def test_chain_nat_freq_within_5pct(self, chain_result):
        """Identified natural frequencies must lie within rtol=5e-2 of truth
        after the full pseudo_random -> response -> H1 -> EMA chain."""
        ema, f_nat_true, _, _ = chain_result
        id_order = np.argsort(ema.nat_freq)
        true_order = np.argsort(f_nat_true)
        nat_freq_id = ema.nat_freq[id_order]
        f_true_sorted = f_nat_true[true_order]
        np.testing.assert_allclose(
            nat_freq_id, f_true_sorted, rtol=5e-2,
            err_msg=(
                "Chain-identified nat. freq. deviate more than 5%% from truth; "
                "excitation, response or FRF stage may have a mismatch"
            ),
        )

    def test_chain_damping_within_5pct_or_flag_instability(self, chain_result):
        """Identified damping ratios must lie within rtol=5e-2 of truth when
        the chain is numerically stable; flags deviation otherwise.

        Deviation note: single-segment H1 from broadband pseudo-random
        excitation can yield noisy damping estimates.  When the identified
        damping values are unphysical (negative or > 0.5) the test is skipped
        with an informative message rather than failing, per the task spec
        fallback rule.
        """
        ema, f_nat_true, zeta_true, damping_stable = chain_result
        if not damping_stable:
            pytest.skip(
                "Flagship chain: damping identification numerically unstable "
                "(H1 from single broadband block); frequency check still passes."
            )
        id_order = np.argsort(ema.nat_freq)
        true_order = np.argsort(f_nat_true)
        xi_id = ema.nat_xi[id_order]
        zeta_sorted = zeta_true[true_order]
        np.testing.assert_allclose(
            xi_id, zeta_sorted, rtol=5e-2,
            err_msg="Chain-identified damping ratios deviate more than 5%% from truth",
        )


# ---------------------------------------------------------------------------
# Area 3: io round-trip (UFF dataset-58)
# ---------------------------------------------------------------------------

class TestUFFRoundTrip:
    """Write FRF data to a UFF file and read it back; data must be allclose."""

    def test_uff58_complex_roundtrip(self, tmp_path):
        """FRF-like complex array round-trips through UFF dataset-58 losslessly.

        Uses pytest ``tmp_path`` (avoids NamedTemporaryFile Windows issues).
        Writes with ``sdypy.io.uff.UFF.write_sets``, reads with
        ``read_sets``, and asserts ``np.allclose`` against the original.
        """
        rng = np.random.default_rng(42)
        n_freq = 256
        freq = np.linspace(0.0, 1000.0, n_freq)
        frf_data = (
            rng.standard_normal(n_freq) + 1j * rng.standard_normal(n_freq)
        )

        dset = sdypy.io.uff.prepare_58(
            func_type=4,          # 4 = FRF
            rsp_node=1,
            rsp_dir=1,
            ref_node=1,
            ref_dir=1,
            data=frf_data,
            x=freq,
            id1="test_interop",
            abscissa_spacing=1,
            abscissa_spec_data_type=18,   # frequency
            ordinate_spec_data_type=12,   # force
            orddenom_spec_data_type=13,   # displacement
        )

        uff_path = str(tmp_path / "test_interop.uff")
        uff_obj = sdypy.io.uff.UFF(uff_path)
        uff_obj.write_sets(dset, mode="overwrite")

        # read back
        uff_read = sdypy.io.uff.UFF(uff_path)
        dsets_back = uff_read.read_sets()

        # read_sets returns a dict when there is exactly one set
        if isinstance(dsets_back, dict):
            dset_back = dsets_back
        else:
            dset_back = dsets_back[0]

        data_back = np.asarray(dset_back["data"])
        assert np.allclose(frf_data, data_back, rtol=1e-6, atol=1e-12), (
            "Round-tripped UFF data does not match original within rtol=1e-6; "
            "max abs diff = %g" % np.max(np.abs(frf_data - data_back))
        )

    def test_uff58_real_roundtrip(self, tmp_path):
        """Real (non-complex) array also round-trips correctly."""
        rng = np.random.default_rng(99)
        n_freq = 128
        freq = np.linspace(0.0, 500.0, n_freq)
        data_real = rng.standard_normal(n_freq)

        dset = sdypy.io.uff.prepare_58(
            func_type=1,          # 1 = time response
            rsp_node=2,
            rsp_dir=1,
            ref_node=2,
            ref_dir=1,
            data=data_real,
            x=freq,
            id1="test_interop_real",
            abscissa_spacing=1,
            abscissa_spec_data_type=17,    # time
            ordinate_spec_data_type=12,    # force (generic)
            orddenom_spec_data_type=0,     # unknown / not applicable
        )

        uff_path = str(tmp_path / "test_real.uff")
        sdypy.io.uff.UFF(uff_path).write_sets(dset, mode="overwrite")
        dset_back = sdypy.io.uff.UFF(uff_path).read_sets()

        if isinstance(dset_back, dict):
            data_back = np.asarray(dset_back["data"])
        else:
            data_back = np.asarray(dset_back[0]["data"])

        assert np.allclose(data_real, data_back, rtol=1e-6, atol=1e-12), (
            "Round-tripped real UFF data does not match; max abs diff = %g"
            % np.max(np.abs(data_real - data_back))
        )


# ---------------------------------------------------------------------------
# Area 4: sep005 smoke test
# ---------------------------------------------------------------------------

class TestSep005Smoke:
    """Verify sdypy.FRF.assert_sep005 validates and rejects sep005 timeseries.

    A SEP-005 timeseries is a *list of channel dicts*; assert_sep005 iterates
    the list and validates each channel. Compulsory channel keys are
    ``data``, ``name`` and ``unit_str``, plus either ``time`` or ``fs``.
    assert_sep005 raises (ValueError/TypeError) on a non-compliant channel.
    """

    def _valid_channel(self):
        """Return a minimal sep005-compliant channel dict."""
        return {
            "data": np.ones(100),
            "name": "test_signal",
            "unit_str": "m/s^2",
            "fs": 1000,
        }

    def test_valid_sep005_list_accepted(self):
        """assert_sep005 accepts a list of valid sep005 channels."""
        channels = [self._valid_channel(), self._valid_channel()]
        sdypy.FRF.assert_sep005(channels)

    def test_missing_data_key_raises(self):
        """Missing 'data' key must cause assert_sep005 to raise."""
        bad = self._valid_channel()
        del bad["data"]
        with pytest.raises((ValueError, TypeError)):
            sdypy.FRF.assert_sep005([bad])

    def test_missing_name_key_raises(self):
        """Missing 'name' key must cause assert_sep005 to raise."""
        bad = self._valid_channel()
        del bad["name"]
        with pytest.raises((ValueError, TypeError)):
            sdypy.FRF.assert_sep005([bad])

    def test_missing_unit_str_key_raises(self):
        """Missing 'unit_str' key must cause assert_sep005 to raise."""
        bad = self._valid_channel()
        del bad["unit_str"]
        with pytest.raises((ValueError, TypeError)):
            sdypy.FRF.assert_sep005([bad])

    def test_missing_fs_and_time_raises(self):
        """Absence of both 'fs' and 'time' keys must raise."""
        bad = self._valid_channel()
        del bad["fs"]
        with pytest.raises((ValueError, TypeError)):
            sdypy.FRF.assert_sep005([bad])

    def test_prohibited_timestamp_key_raises(self):
        """Presence of prohibited 'timestamp' key must raise."""
        bad = self._valid_channel()
        bad["timestamp"] = "2026-01-01"
        with pytest.raises((ValueError, TypeError)):
            sdypy.FRF.assert_sep005([bad])
