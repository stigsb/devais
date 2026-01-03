"""
User Interface Subsystem for Devais
- Push-to-talk button
- Power/mode button
- Status LEDs (power, connectivity, activity)
"""

from circuit_synth import Component, Net, circuit


@circuit(name="Push_Button")
def push_button(gpio, gnd):
    """
    Tactile push button with pull-up configuration

    Args:
        gpio: GPIO pin for button input (internal pull-up enabled)
        gnd: Ground
    """
    button = Component(
        symbol="Switch:SW_Push",
        ref="SW",
        footprint="Button_Switch_SMD:SW_SPST_TL3342"
    )

    button[1] += gpio
    button[2] += gnd

    # External pull-up resistor (in case internal pull-up not used)
    # Can be marked DNP (Do Not Populate) if using internal pull-up
    # pullup = Component(
    #     symbol="Device:R",
    #     ref="R",
    #     value="10k",
    #     footprint="Resistor_SMD:R_0603_1608Metric"
    # )
    # pullup[1] += vcc
    # pullup[2] += gpio


@circuit(name="Status_LED")
def status_led(gpio, gnd):
    """
    Status LED with current-limiting resistor

    Args:
        gpio: GPIO pin for LED control (active high)
        gnd: Ground
    """
    led = Component(
        symbol="Device:LED",
        ref="D",
        footprint="LED_SMD:LED_0603_1608Metric"
    )

    resistor = Component(
        symbol="Device:R",
        ref="R",
        value="1k",
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

    # GPIO -> Resistor -> LED -> GND
    resistor[1] += gpio
    resistor[2] += led["A"]  # Anode
    led["K"] += gnd  # Cathode


@circuit(name="User_Interface")
def user_interface(
    vcc_3v3,
    btn_ptt_gpio,
    btn_power_gpio,
    led_power_gpio,
    led_ble_gpio,
    led_activity_gpio,
    gnd
):
    """
    Complete user interface system

    Args:
        vcc_3v3: 3.3V power supply
        btn_ptt_gpio: Push-to-talk button GPIO
        btn_power_gpio: Power/mode button GPIO
        led_power_gpio: Power status LED GPIO
        led_ble_gpio: BLE connectivity LED GPIO
        led_activity_gpio: Activity indicator LED GPIO
        gnd: Ground
    """
    # Push-to-talk button
    push_button(btn_ptt_gpio, gnd)

    # Power/mode button
    push_button(btn_power_gpio, gnd)

    # Status LEDs
    status_led(led_power_gpio, gnd)  # Power LED (green)
    status_led(led_ble_gpio, gnd)  # BLE status LED (blue)
    status_led(led_activity_gpio, gnd)  # Activity LED (amber/yellow)
