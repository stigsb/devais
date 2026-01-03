"""
I2S Audio Subsystem for Devais
- INMP441 MEMS I2S microphone
- MAX98357A Class D I2S amplifier
- Shared I2S clock signals (efficient architecture)
"""

from circuit_synth import Component, Net, circuit


@circuit(name="I2S_Microphone")
def i2s_microphone(vcc, sck, ws, sd, gnd):
    """
    INMP441 MEMS I2S microphone

    Args:
        vcc: 3.3V power
        sck: I2S bit clock (shared with amplifier)
        ws: I2S word select / LR clock (shared with amplifier)
        sd: Serial data output from microphone
        gnd: Ground
    """
    mic = Component(
        symbol="Audio:INMP441",
        ref="MIC",
        footprint="Audio:INMP441_Breakout"
    )

    mic["VDD"] += vcc
    mic["SCK"] += sck
    mic["WS"] += ws
    mic["SD"] += sd
    mic["GND"] += gnd

    # L/R selection (GND = left channel)
    mic["L/R"] += gnd

    # Decoupling capacitor for microphone
    cap_mic = Component(
        symbol="Device:C",
        ref="C",
        value="100nF",
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    cap_mic[1] += vcc
    cap_mic[2] += gnd


@circuit(name="I2S_Amplifier")
def i2s_amplifier(vcc, sck, ws, sd, spk_p, spk_n, gnd):
    """
    MAX98357A Class D I2S amplifier

    Args:
        vcc: 3.3V power
        sck: I2S bit clock (shared with microphone)
        ws: I2S word select / LR clock (shared with microphone)
        sd: Serial data input to amplifier
        spk_p: Speaker positive output
        spk_n: Speaker negative output
        gnd: Ground
    """
    amp = Component(
        symbol="Audio:MAX98357A",
        ref="U",
        footprint="Audio:MAX98357A_Breakout"
    )

    amp["VIN"] += vcc
    amp["BCLK"] += sck
    amp["LRC"] += ws
    amp["DIN"] += sd
    amp["GND"] += gnd
    amp["OUT+"] += spk_p
    amp["OUT-"] += spk_n

    # SD_MODE tied to VCC for I2S mode
    amp["SD"] += vcc

    # GAIN setting (GND = 9dB, VCC = 15dB, floating = 12dB)
    # Using 9dB for battery efficiency
    amp["GAIN"] += gnd

    # Decoupling capacitors
    cap_amp_bulk = Component(
        symbol="Device:C",
        ref="C",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_amp_bulk[1] += vcc
    cap_amp_bulk[2] += gnd

    cap_amp_decouple = Component(
        symbol="Device:C",
        ref="C",
        value="100nF",
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    cap_amp_decouple[1] += vcc
    cap_amp_decouple[2] += gnd


@circuit(name="Speaker")
def speaker_output(spk_p, spk_n):
    """
    Speaker connection

    Args:
        spk_p: Speaker positive terminal
        spk_n: Speaker negative terminal
    """
    speaker = Component(
        symbol="Device:Speaker",
        ref="LS",
        footprint="Audio:Speaker_Round_28mm"
    )

    speaker["+"] += spk_p
    speaker["-"] += spk_n


@circuit(name="Audio_System")
def audio_system(vcc_3v3, i2s_sck, i2s_ws, i2s_sd_in, i2s_sd_out, gnd):
    """
    Complete I2S audio system with shared clock architecture

    This implements the efficient I2S bus design:
    - SCK and WS are shared between microphone and amplifier
    - SD_IN carries mic data to nRF52840
    - SD_OUT carries audio data from nRF52840 to amplifier

    Args:
        vcc_3v3: 3.3V power supply
        i2s_sck: I2S bit clock (to/from nRF52840)
        i2s_ws: I2S word select (to/from nRF52840)
        i2s_sd_in: Mic serial data (to nRF52840)
        i2s_sd_out: Amp serial data (from nRF52840)
        gnd: Ground
    """
    # Speaker nets
    spk_p = Net('SPK+')
    spk_n = Net('SPK-')

    # Microphone with shared clock signals
    i2s_microphone(vcc_3v3, i2s_sck, i2s_ws, i2s_sd_in, gnd)

    # Amplifier with shared clock signals
    i2s_amplifier(vcc_3v3, i2s_sck, i2s_ws, i2s_sd_out, spk_p, spk_n, gnd)

    # Speaker
    speaker_output(spk_p, spk_n)
