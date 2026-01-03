"""
Devais - Simplified Starter Version
Uses only standard KiCad library symbols for quick generation

This is a simplified version that will generate immediately.
See devais.py for the complete circuit with all subsystems.
"""

from circuit_synth import Component, Net, circuit


@circuit(name="Devais_Simplified")
def devais_simplified():
    """
    Simplified starter circuit with basic components

    This uses only standard KiCad symbols to get you started quickly.
    You can then customize and add the full subsystems from:
    - power_management.py
    - audio.py
    - user_interface.py
    - devais.py (complete version)
    """
    # Global nets
    gnd = Net('GND')
    vcc_3v3 = Net('VCC_3V3')
    vbat = Net('VBAT')

    # Simple 3.3V regulator
    regulator = Component(
        symbol="Regulator_Linear:AMS1117-3.3",
        ref="U1",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    regulator["VI"] += vbat
    regulator["VO"] += vcc_3v3
    regulator["GND"] += gnd

    # Regulator capacitors
    cap_in = Component(
        symbol="Device:C",
        ref="C1",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_in[1] += vbat
    cap_in[2] += gnd

    cap_out = Component(
        symbol="Device:C",
        ref="C2",
        value="22uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_out[1] += vcc_3v3
    cap_out[2] += gnd

    # Battery
    battery = Component(
        symbol="Device:Battery_Cell",
        ref="BT1",
        footprint="Battery:BatteryHolder_Keystone_1042_1x18650"
    )
    battery["+"] += vbat
    battery["-"] += gnd

    # USB-C connector (simplified - just power)
    usb_c = Component(
        symbol="Connector:USB_C_Receptacle",
        ref="J1",
        footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12"
    )

    # Connect VBUS
    vbus = Net('VBUS')
    usb_c["VBUS"] += vbus
    usb_c["GND"] += gnd

    # CC resistors for USB-C
    cc1_r = Component(
        symbol="Device:R",
        ref="R1",
        value="5.1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    cc2_r = Component(
        symbol="Device:R",
        ref="R2",
        value="5.1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    cc1_r[1] += usb_c["CC1"]
    cc1_r[2] += gnd
    cc2_r[1] += usb_c["CC2"]
    cc2_r[2] += gnd

    # Status LED
    led = Component(
        symbol="Device:LED",
        ref="D1",
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    led_r = Component(
        symbol="Device:R",
        ref="R3",
        value="1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    led_r[1] += vcc_3v3
    led_r[2] += led["A"]
    led["K"] += gnd

    # Push button
    button = Component(
        symbol="Switch:SW_Push",
        ref="SW1",
        footprint="Button_Switch_SMD:SW_SPST_TL3342"
    )
    btn_gpio = Net('BTN_GPIO')
    button[1] += btn_gpio
    button[2] += gnd

    print("\n" + "="*60)
    print("SIMPLIFIED DEVAIS CIRCUIT")
    print("="*60)
    print("\nThis is a minimal starter circuit with:")
    print("  ✓ 18650 battery")
    print("  ✓ USB-C connector (power only)")
    print("  ✓ 3.3V regulator (AMS1117)")
    print("  ✓ Status LED")
    print("  ✓ Push button")
    print("\nNext steps:")
    print("  1. Generate this simplified version to verify setup")
    print("  2. Add microcontroller (nRF52840 module)")
    print("  3. Add audio system from audio.py")
    print("  4. Add full power management from power_management.py")
    print("  5. Migrate to devais.py for complete design")
    print("\nComponent symbols to add/customize:")
    print("  - Seeed XIAO nRF52840 (create custom symbol)")
    print("  - INMP441 microphone (use generic or create)")
    print("  - MAX98357A amplifier (use generic or create)")
    print("="*60 + "\n")


if __name__ == "__main__":
    circuit = devais_simplified()

    print("Generating simplified Devais KiCad project...")
    circuit.generate_kicad_project("devais_simplified")

    print("\n✓ KiCad project generated: devais_simplified/")
    print("\nOpen with: open devais_simplified/devais_simplified.kicad_pro")
