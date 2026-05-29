# Project Context

This is a fork of [ORCA](https://github.com/radioglaciology/uhd_radar) (Open Radar Code Architecture), a radar software stack for Ettus USRP SDRs. This fork targets the **Ettus B210** and adds dual-channel independent waveform transmission.

---

## Goal

Transmit two independent waveforms simultaneously from the two TX ports of a B210:

- **RF A (TX/RX port, ch0):** CW tone acting as a local oscillator
- **RF B (TX2 port, ch1):** Linear frequency-modulated chirp

These are mixed externally to produce a downconverted IF chirp.

---

## Key Hardware Constraints (B210 / AD9361)

1. **Shared LO.** The B210 uses a single AD9361 RFIC with one PLL shared between both TX channels. Both `RF0.freq` and `RF1.freq` must be set to the **same value**. Use `lo_offset_sw` in `GENERATE`/`GENERATE1` to position each signal at a different RF frequency digitally.

2. **Shared sample rate.** Both TX channels must use the same sample rate (B210 hardware constraint). `GENERATE1` inherits `sample_rate` from `GENERATE`.

3. **Inter-channel isolation.** The two TX ports share the same die. Isolation is finite (~40–50 dB). When both channels are active, some of each signal leaks into the other port, producing intermodulation distortion products (e.g., 2f₁−f₂ and 2f₂−f₁). This is a hardware limitation and cannot be fixed in software.

4. **Nyquist limit.** `lo_offset_sw + chirp_bandwidth/2` must be strictly less than `sample_rate/2`. Signals at or near the Nyquist edge will alias or roll off. Run at `sample_rate: 56e6` (B210 maximum) to give comfortable headroom.

5. **Analog filter (`bw`).** `RF0.bw` / `RF1.bw` sets the AD9361 analog baseband filter. Set to `0` to use the hardware default (maximum). Setting it to exactly the chirp bandwidth causes rolloff at the band edges.

---

## Working Config Pattern

```yaml
GENERATE:               # CH0: CW at 70 MHz
    sample_rate: &s_rate 56e6
    chirp_bandwidth: 0e6
    lo_offset_sw: -5e6  # 75 MHz LO + (-5 MHz) = 70 MHz RF
    phase_dithering: true

GENERATE1:              # CH1: chirp 70–80 MHz
    chirp_bandwidth: 10e6
    lo_offset_sw: 5e6   # 75 MHz LO + 5 MHz center, ±5 MHz BW = 70–80 MHz RF
    phase_dithering: false

RF0:
    freq: 75e6          # shared LO — must match RF1.freq
    bw: 0               # use hardware default filter
    tx_ant: "TX/RX"

RF1:
    freq: 75e6          # must match RF0.freq on B210
    bw: 0
    tx_ant: "TX/RX"
    transmit: true      # set false to disable ch1 entirely

DEVICE:
    subdev: "A:A A:B"
    clk_rate: 56e6
    tx_channels: "0, 1"
```

---

## Changes Made in This Fork

### New feature: independent per-channel waveforms (`GENERATE1`)

**`preprocessing/generate_chirp.py`**
- Added optional `section` parameter to `generate_chirp()` and `generate_from_yaml_filename()`, defaulting to `"GENERATE"`. All existing callers unchanged.
- `sample_rate` is always read from `GENERATE` regardless of section (B210 hardware constraint).

**`run.py`**
- After generating the ch0 chirp, conditionally generates a ch1 chirp if `GENERATE1` is present and `RF1.transmit: true`.

**`sdr/sdr.hpp` / `sdr/sdr.cpp`**
- Added members: `transmit_ch1`, `phase_dither_ch0`, `phase_dither_ch1` with getters.
- `phase_dithering` moved from `CHIRP` to `GENERATE`/`GENERATE1`. A warning is printed if it is still set under `CHIRP` (old location, now ignored).
- `setupTx()` now filters the TX stream to only include ch1 when `transmit_ch1` is true, preventing ch0's waveform from broadcasting to ch1.
- Sanity checks: Nyquist check (warns if `|lo_offset_sw| + chirp_bw/2 >= sample_rate/2`), analog filter check (warns if signal extends outside `RF.bw` passband).
- Changed pulse length mismatch check (lines 84–87): was a WARNING saying "Both TX channels must transmit the same number of samples"; now an INFO reporting the two durations and noting the shorter will be zero-padded. Different lengths are now intentional and supported.

**`sdr/chirp.hpp` / `sdr/chirp.cpp`**
- Removed `phase_dither` member and `getPhaseDither()` getter. `CHIRP` section is now purely timing/scheduling.

**`sdr/pseudorandom_phase.hpp` / `.cpp`**
- Added `random_generator_ch1` (seed 1, independent from ch0 seed 0) and `get_next_phase_ch1()`.

**`sdr/main.cpp`**
- Loads `chirp1_loc` from `GENERATE1.out_file` when GENERATE1 is present and `RF1.transmit: true`.
- `transmit_worker` allocates separate buffers per channel (`tx_buff_ch0`, `tx_buff_ch1`) and uses `tx_stream->send(vector<void*>, ...)` to send different data to each port.
- Replaced global `num_tx_samps` with three globals: `num_tx_samps_ch0` (from `GENERATE.pulse_length`), `num_tx_samps_ch1` (from `GENERATE1.pulse_length`, 0 if ch1 not used), and `num_tx_samps_burst = max(ch0, ch1)`. Previously both channels used a single count derived from `CHIRP.tx_duration`.
- `transmit_worker`: ch0 and ch1 buffers are now zero-initialized to `num_tx_samps_burst` and each reads only its own `num_tx_samps_chN` samples from file, leaving the tail as zeros. `tx_stream->send()` now sends `num_tx_samps_burst` samples. Previously all buffers were sized and sent as `num_tx_samps`.
- Added startup warning if either channel's `pulse_length / pulse_rep_int > 0.9`.
- TX summary lambda: added `pulse_length_s` parameter; prints "Pulse length : X us" per active channel. Call sites pass `num_tx_samps_chN / getTxRate()` so the displayed value reflects the sample-quantized duration actually transmitted.
- GPS serial port (`/dev/ttyACM0`) is now only opened when `clk_ref: "gpsdo"`. Previously opened unconditionally, causing crashes when using internal clock.

**`sdr/main.hpp`**
- Updated `handleRxBuffer` signature to accept `bool phase_dither` parameter.

**`sdr/rf_settings.cpp`**
- `set_rf_params_multi` now tunes both channels to `RF0.freq`. Warns if `RF1.freq` differs (B210 shared LO — the second `set_tx_freq` call would silently overwrite the first).

**`postprocessing/processing_dask.py`**
- `invert_phase_dithering()` checks `GENERATE` first for `phase_dithering`, then falls back to `CHIRP` for backward compatibility with old datasets.

**`postprocessing/save_data.py`**
- Guards `shutil.move`/`shutil.copy` with `os.path.exists()` checks and prints a warning instead of raising `FileNotFoundError` when the RX samples file is missing.

**`config/default.yaml`** and all other config files
- `phase_dithering` moved from `CHIRP` section to `GENERATE` section.
- `default.yaml` includes a commented-out `GENERATE1` example block.

**`tests/sdr/test_chirp.cpp`**
- Removed stale `EXPECT_EQ(chirp.getPhaseDither(), true)` assertion (`getPhaseDither()` no longer exists on `Chirp`).

---

## Runtime Notes

- Run all Python scripts (`run.py`, test scripts) from the **repo root**, not from subdirectories. Scripts use relative `sys.path.append` calls.
- The binary runs from `sdr/build/` and opens data files relative to `../../` (i.e., the repo root). Ensure `data/` exists at the repo root.
- Real-time thread priority warnings (`pthread_setschedparam`) are fixed by adding the user to a group with `rtprio` permissions in `/etc/security/limits.conf`.
- `clk_ref: "internal"` is the default. GPS serial port is not touched in this mode.


##for user, not you
claude --resume 5ed266c4-9f69-4b76-b127-976a11d52381