"""
Power Management Subsystem for Devais
- 18650 Li-ion battery
- USB-C charging
- 3.3V voltage regulation for nRF52840 and peripherals
"""

from circuit_synth import Component, Net, circuit


@circuit(name="USB_C_Power")
def usb_c_power_input(vbus, gnd):
    """
    USB-C power input with basic protection

    Returns:
        vbus: 5V from USB-C
        gnd: Ground
    """
    # USB-C connector
    usb_c = Component(
        symbol="Connector:USB_C_Receptacle_USB2.0",
        ref="J",
        footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12"
    )

    # Connect VBUS pins (A4, A9, B4, B9 are VBUS on USB-C)
    usb_c["A4"] += vbus
    usb_c["A9"] += vbus
    usb_c["B4"] += vbus
    usb_c["B9"] += vbus

    # Connect GND pins
    usb_c["A1"] += gnd
    usb_c["A12"] += gnd
    usb_c["B1"] += gnd
    usb_c["B12"] += gnd
    usb_c["S1"] += gnd  # Shield

    # CC resistors for USB-C detection (5.1k for power sink)
    cc1_resistor = Component(
        symbol="Device:R",
        ref="R",
        value="5.1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    cc2_resistor = Component(
        symbol="Device:R",
        ref="R",
        value="5.1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

    cc1_resistor[1] += usb_c["A5"]  # CC1
    cc1_resistor[2] += gnd

    cc2_resistor[1] += usb_c["B5"]  # CC2
    cc2_resistor[2] += gnd

    # Input protection capacitor
    input_cap = Component(
        symbol="Device:C",
        ref="C",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    input_cap[1] += vbus
    input_cap[2] += gnd


@circuit(name="Battery_Management")
def battery_management(vbat, vbus, gnd):
    """
    18650 Li-ion battery with charging circuit

    Args:
        vbat: Battery voltage output
        vbus: 5V from USB-C
        gnd: Ground
    """
    # Battery connector/holder
    battery = Component(
        symbol="Device:Battery_Cell",
        ref="BT",
        footprint="Battery:BatteryHolder_Keystone_1042_1x18650"
    )
    battery["+"] += vbat
    battery["-"] += gnd

    # TP4056 Li-ion battery charger (or similar)
    charger = Component(
        symbol="Power_Management:TP4056",
        ref="U",
        footprint="Package_TO_SOT_SMD:SOT-23-5"
    )

    charger["VCC"] += vbus
    charger["BAT"] += vbat
    charger["GND"] += gnd

    # Programming resistor for charge current (1.2k = 1A charge)
    rprog = Component(
        symbol="Device:R",
        ref="R",
        value="1.2k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    rprog[1] += charger["PROG"]
    rprog[2] += gnd

    # Battery decoupling capacitor
    bat_cap = Component(
        symbol="Device:C",
        ref="C",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    bat_cap[1] += vbat
    bat_cap[2] += gnd


@circuit(name="Voltage_Regulator")
def voltage_regulator_3v3(vin, vout_3v3, gnd):
    """
    3.3V LDO regulator for nRF52840 and peripherals

    Args:
        vin: Input voltage (3.7V from battery or 5V from USB)
        vout_3v3: Regulated 3.3V output
        gnd: Ground
    """
    # 3.3V LDO regulator (e.g., AMS1117-3.3 or XC6206P332MR)
    regulator = Component(
        symbol="Regulator_Linear:AMS1117-3.3",
        ref="U",
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )

    regulator["VI"] += vin
    regulator["VO"] += vout_3v3
    regulator["GND"] += gnd

    # Input capacitor
    cap_in = Component(
        symbol="Device:C",
        ref="C",
        value="10uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_in[1] += vin
    cap_in[2] += gnd

    # Output capacitor
    cap_out = Component(
        symbol="Device:C",
        ref="C",
        value="22uF",
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    cap_out[1] += vout_3v3
    cap_out[2] += gnd

    # Additional decoupling capacitor
    cap_decouple = Component(
        symbol="Device:C",
        ref="C",
        value="100nF",
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    cap_decouple[1] += vout_3v3
    cap_decouple[2] += gnd


@circuit(name="Power_System")
def power_system(vcc_3v3, gnd):
    """
    Complete power management system

    Provides regulated 3.3V from either USB-C or 18650 battery

    Args:
        vcc_3v3: 3.3V output for system
        gnd: Ground
    """
    vbus = Net('VBUS')
    vbat = Net('VBAT')

    # USB-C input
    usb_c_power_input(vbus, gnd)

    # Battery with charging
    battery_management(vbat, vbus, gnd)

    # Power source selection (battery when no USB, USB when connected)
    # Simple diode OR for now (could use ideal diode controller)
    usb_diode = Component(
        symbol="Device:D_Schottky",
        ref="D",
        footprint="Diode_SMD:D_SOD-323"
    )
    bat_diode = Component(
        symbol="Device:D_Schottky",
        ref="D",
        footprint="Diode_SMD:D_SOD-323"
    )

    vin = Net('VIN')
    usb_diode["A"] += vbus
    usb_diode["K"] += vin
    bat_diode["A"] += vbat
    bat_diode["K"] += vin

    # 3.3V regulation
    voltage_regulator_3v3(vin, vcc_3v3, gnd)
