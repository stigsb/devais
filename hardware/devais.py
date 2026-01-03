"""
Devais - Handheld AI Assistant Device
Main circuit composition

This brings together all subsystems:
- Power management (USB-C, battery, 3.3V regulation)
- Audio (I2S microphone and amplifier)
- User interface (buttons and LEDs)
- nRF52840 microcontroller

Based on component selections from:
- Seeed XIAO nRF52840
- INMP441 I2S microphone
- MAX98357A I2S amplifier
- 18650 Li-ion battery
"""

from circuit_synth import Component, Net, circuit

from power_management import power_system
from audio import audio_system
from user_interface import user_interface


@circuit(name="nRF52840_Controller")
def nrf52840_controller(
    vcc_3v3,
    # I2S bus
    i2s_sck,
    i2s_ws,
    i2s_sd_in,
    i2s_sd_out,
    # User interface
    btn_ptt,
    btn_power,
    led_power,
    led_ble,
    led_activity,
    # Programming/debug
    swdio,
    swclk,
    reset,
    gnd
):
    """
    Seeed XIAO nRF52840 microcontroller module

    Note: The XIAO nRF52840 is a complete module with:
    - nRF52840 MCU
    - USB-C connector (for programming/debug)
    - Reset button
    - Voltage regulator
    - Battery charging circuit

    For the production design, we're treating it as a module.
    In the future, this could be replaced with discrete nRF52840 chip.

    Args:
        vcc_3v3: 3.3V power input
        i2s_*: I2S audio bus signals
        btn_*: Button GPIO inputs
        led_*: LED GPIO outputs
        swdio, swclk: SWD programming interface
        reset: Reset pin
        gnd: Ground
    """
    # XIAO nRF52840 module
    mcu = Component(
        symbol="MCU:Seeed_XIAO_nRF52840",
        ref="U",
        footprint="Module:Seeed_XIAO_nRF52840"
    )

    # Power
    mcu["3V3"] += vcc_3v3
    mcu["GND"] += gnd

    # I2S audio bus (using nRF52840 I2S peripheral)
    # Pin assignments based on typical I2S configuration
    mcu["P0.26"] += i2s_sck  # I2S SCK
    mcu["P0.27"] += i2s_ws  # I2S WS (LRCK)
    mcu["P0.28"] += i2s_sd_in  # I2S SDI (mic data in)
    mcu["P0.29"] += i2s_sd_out  # I2S SDO (amp data out)

    # User interface
    mcu["P0.02"] += btn_ptt  # Push-to-talk button (interrupt capable)
    mcu["P0.03"] += btn_power  # Power/mode button (interrupt capable)

    mcu["P0.06"] += led_power  # Power status LED
    mcu["P0.07"] += led_ble  # BLE connection LED
    mcu["P0.08"] += led_activity  # Activity indicator LED

    # SWD programming interface
    mcu["SWDIO"] += swdio
    mcu["SWCLK"] += swclk
    mcu["RESET"] += reset

    # SWD header for programming/debugging
    swd_header = Component(
        symbol="Connector:Conn_ARM_JTAG_SWD_10",
        ref="J",
        footprint="Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical"
    )

    swd_header["VCC"] += vcc_3v3
    swd_header["SWDIO"] += swdio
    swd_header["SWCLK"] += swclk
    swd_header["RESET"] += reset
    swd_header["GND"] += gnd

    # Pull-up on reset line
    reset_pullup = Component(
        symbol="Device:R",
        ref="R",
        value="10k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    reset_pullup[1] += vcc_3v3
    reset_pullup[2] += reset

    # Decoupling capacitors for MCU
    cap_mcu_1 = Component(
        symbol="Device:C",
        ref="C",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_mcu_1[1] += vcc_3v3
    cap_mcu_1[2] += gnd

    cap_mcu_2 = Component(
        symbol="Device:C",
        ref="C",
        value="100nF",
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    cap_mcu_2[1] += vcc_3v3
    cap_mcu_2[2] += gnd


@circuit(name="Devais")
def devais_main():
    """
    Main Devais circuit

    Complete handheld AI assistant device with:
    - Power management (USB-C charging, 18650 battery, 3.3V regulation)
    - Audio system (I2S microphone and amplifier with shared clock)
    - User interface (push-to-talk, power button, status LEDs)
    - nRF52840 BLE microcontroller
    """
    # Global nets
    gnd = Net('GND')
    vcc_3v3 = Net('VCC_3V3')

    # I2S audio bus nets
    i2s_sck = Net('I2S_SCK')
    i2s_ws = Net('I2S_WS')
    i2s_sd_in = Net('I2S_SDI')  # Mic to MCU
    i2s_sd_out = Net('I2S_SDO')  # MCU to Amp

    # User interface nets
    btn_ptt = Net('BTN_PTT')
    btn_power = Net('BTN_PWR')
    led_power = Net('LED_PWR')
    led_ble = Net('LED_BLE')
    led_activity = Net('LED_ACT')

    # Programming interface nets
    swdio = Net('SWDIO')
    swclk = Net('SWCLK')
    reset = Net('RESET')

    # Subsystems
    power_system(vcc_3v3, gnd)

    audio_system(vcc_3v3, i2s_sck, i2s_ws, i2s_sd_in, i2s_sd_out, gnd)

    user_interface(
        vcc_3v3,
        btn_ptt,
        btn_power,
        led_power,
        led_ble,
        led_activity,
        gnd
    )

    nrf52840_controller(
        vcc_3v3,
        i2s_sck,
        i2s_ws,
        i2s_sd_in,
        i2s_sd_out,
        btn_ptt,
        btn_power,
        led_power,
        led_ble,
        led_activity,
        swdio,
        swclk,
        reset,
        gnd
    )


if __name__ == "__main__":
    # Generate KiCad project
    circuit = devais_main()

    print("Generating Devais KiCad project...")

    # Generate schematic and PCB
    circuit.generate_kicad_project(
        "devais_v1",
        force_regenerate=False  # Preserve manual changes to KiCad files
    )

    print("✓ KiCad project generated: devais_v1/")
    print("  - devais_v1.kicad_pro")
    print("  - devais_v1.kicad_sch")
    print("  - devais_v1.kicad_pcb")
    print()
    print("Next steps:")
    print("1. Open in KiCad: open devais_v1/devais_v1.kicad_pro")
    print("2. Assign footprints (if needed)")
    print("3. Layout PCB components")
    print("4. Route traces")
    print("5. Generate Gerbers: circuit.generate_gerbers('devais_v1')")
