/**
 * Devais - Handheld AI Assistant PCB (Vertical Main Board)
 *
 * Board: 28x140mm, mounted vertically in chassis half along right wall.
 * Coordinate mapping: board Y = enclosure Z - 75mm
 *
 * Front side (facing inward): all ICs, passives, JST connectors
 * Back side (facing wall): USB-C port, power button, PTT microswitch
 *
 * Back-side components poke through enclosure wall cutouts:
 *   USB-C at Z=31mm (board Y=-44)
 *   Power button at Z=44mm (board Y=-31)
 *   PTT switch at Z=105mm (board Y=+30)
 *
 * Mounting: 6x M2 holes — 2 flanking USB-C zone, 2 flanking PTT zone,
 *           2 at top corners. All stress points supported.
 */

export default () => (
  <board width="28mm" height="140mm" autorouter="sequential-trace">

    {/* ═══════════════════════════════════════════════════════
        BACK SIDE — components facing enclosure wall
        ═══════════════════════════════════════════════════════ */}

    {/* ── USB-C receptacle (Z=31mm, Y=-44) ────────────────── */}
    {/* TYPE-C 6P CB1.6 mid-mount, JLCPCB C2858274 */}
    <chip name="J_USB" footprint="soic8"
      pcbX={0} pcbY={-44} layer="bottom" schX={-15} schY={0}
      supplierPartNumbers={{ jlcpcb: ["C2858274"] }}
      pinLabels={{
        pin1: "GND1", pin2: "VBUS1", pin3: "CC1", pin4: "CC2",
        pin5: "VBUS2", pin6: "GND2", pin7: "SHIELD1", pin8: "SHIELD2",
      }} />
    <trace from=".J_USB > .GND1"    to="net.GND" />
    <trace from=".J_USB > .GND2"    to="net.GND" />
    <trace from=".J_USB > .VBUS1"   to="net.VBUS" />
    <trace from=".J_USB > .VBUS2"   to="net.VBUS" />
    <trace from=".J_USB > .SHIELD1" to="net.GND" />
    <trace from=".J_USB > .SHIELD2" to="net.GND" />

    {/* CC resistors (5.1k to GND for USB-C sink identification) */}
    <resistor name="R_CC1" resistance="5.1k" footprint="0603"
      pcbX={-8} pcbY={-44}
      supplierPartNumbers={{ jlcpcb: ["C23186"] }} />
    <trace from=".J_USB > .CC1" to=".R_CC1 > .pin1" />
    <trace from=".R_CC1 > .pin2" to="net.GND" />

    <resistor name="R_CC2" resistance="5.1k" footprint="0603"
      pcbX={8} pcbY={-44}
      supplierPartNumbers={{ jlcpcb: ["C23186"] }} />
    <trace from=".J_USB > .CC2" to=".R_CC2 > .pin1" />
    <trace from=".R_CC2 > .pin2" to="net.GND" />

    {/* ── Power button (Z=44mm, Y=-31) ────────────────────── */}
    <chip name="SW_PWR" footprint="pushbutton"
      pcbX={0} pcbY={-31} layer="bottom" schX={5} schY={-8}
      supplierPartNumbers={{ jlcpcb: ["C2837531"] }}
      pinLabels={{ pin1: "A", pin2: "B" }} />
    <trace from=".SW_PWR > .A" to="net.BTN_PWR" />
    <trace from=".SW_PWR > .B" to="net.GND" />

    <resistor name="R_PWR" resistance="10k" footprint="0603"
      pcbX={8} pcbY={-31} pcbRotation={90}
      supplierPartNumbers={{ jlcpcb: ["C25804"] }} />
    <trace from=".R_PWR > .pin1" to="net.VCC3V3" />
    <trace from=".R_PWR > .pin2" to="net.BTN_PWR" />

    {/* ── PTT microswitch (Z=105mm, Y=+30) ───────────────── */}
    {/* Omron D2F-01F, 75gf, 1M cycles, SPDT 3-pin THT */}
    <chip name="SW_PTT" footprint="pinrow3"
      pcbX={0} pcbY={30} layer="bottom" schX={5} schY={-5}
      supplierPartNumbers={{ jlcpcb: ["C403989"] }}
      pinLabels={{ pin1: "COM", pin2: "NO", pin3: "NC" }} />
    <trace from=".SW_PTT > .COM" to="net.GND" />
    <trace from=".SW_PTT > .NO"  to="net.BTN_PTT" />
    {/* NC pin left unconnected */}

    <resistor name="R_PTT" resistance="10k" footprint="0603"
      pcbX={8} pcbY={30} pcbRotation={90}
      supplierPartNumbers={{ jlcpcb: ["C25804"] }} />
    <trace from=".R_PTT > .pin1" to="net.VCC3V3" />
    <trace from=".R_PTT > .pin2" to="net.BTN_PTT" />

    {/* ═══════════════════════════════════════════════════════
        FRONT SIDE — LOWER ZONE (alongside battery, Z=5-65mm)
        Max component height ~3.4mm (SOT-223, SOIC-8, passives)
        ═══════════════════════════════════════════════════════ */}

    {/* ── Y=-65 (Z=10mm): Battery connector ───────────────── */}
    <chip name="J_BAT" footprint="pinrow2"
      pcbX={0} pcbY={-65} schX={-10} schY={-5}
      pinLabels={{ pin1: "BAT_P", pin2: "BAT_N" }} />
    <trace from=".J_BAT > .BAT_P" to="net.VBAT" />
    <trace from=".J_BAT > .BAT_N" to="net.GND" />

    <capacitor name="C_BAT" capacitance="10uF" footprint="0805"
      pcbX={8} pcbY={-65}
      supplierPartNumbers={{ jlcpcb: ["C15850"] }} />
    <trace from=".C_BAT > .pin1" to="net.VBAT" />
    <trace from=".C_BAT > .pin2" to="net.GND" />

    {/* ── Y=-51 (Z=24mm): TP4056 charger ──────────────────── */}
    <chip name="U_CHG" footprint="soic8"
      pcbX={0} pcbY={-51} schX={-10} schY={0}
      supplierPartNumbers={{ jlcpcb: ["C16581"] }}
      pinLabels={{
        pin1: "TEMP", pin2: "PROG", pin3: "GND", pin4: "VCC",
        pin5: "BAT", pin6: "STDBY", pin7: "CHRG", pin8: "CE",
      }} />
    <trace from=".U_CHG > .VCC"  to="net.VBUS" />
    <trace from=".U_CHG > .GND"  to="net.GND" />
    <trace from=".U_CHG > .BAT"  to="net.VBAT" />
    <trace from=".U_CHG > .CE"   to="net.VBUS" />
    <trace from=".U_CHG > .TEMP" to="net.GND" />

    <resistor name="R_PROG" resistance="1.2k" footprint="0603"
      pcbX={-8} pcbY={-51} pcbRotation={90}
      supplierPartNumbers={{ jlcpcb: ["C22765"] }} />
    <trace from=".U_CHG > .PROG" to=".R_PROG > .pin1" />
    <trace from=".R_PROG > .pin2" to="net.GND" />

    <capacitor name="C_USB" capacitance="10uF" footprint="0805"
      pcbX={8} pcbY={-51}
      supplierPartNumbers={{ jlcpcb: ["C15850"] }} />
    <trace from=".C_USB > .pin1" to="net.VBUS" />
    <trace from=".C_USB > .pin2" to="net.GND" />

    {/* ── Y=-20 (Z=55mm): Voltage regulator ───────────────── */}
    <chip name="U_REG" footprint="sot223"
      pcbX={0} pcbY={-20} schX={-5} schY={0}
      supplierPartNumbers={{ jlcpcb: ["C6186"] }}
      pinLabels={{ pin1: "GND", pin2: "VOUT", pin3: "VIN", pin4: "VOUT_TAB" }} />
    <trace from=".U_REG > .VIN"      to="net.VBAT" />
    <trace from=".U_REG > .VOUT"     to="net.VCC3V3" />
    <trace from=".U_REG > .VOUT_TAB" to="net.VCC3V3" />
    <trace from=".U_REG > .GND"      to="net.GND" />

    <capacitor name="C_REGIN" capacitance="10uF" footprint="0805"
      pcbX={-10} pcbY={-20} pcbRotation={90}
      supplierPartNumbers={{ jlcpcb: ["C15850"] }} />
    <trace from=".C_REGIN > .pin1" to="net.VBAT" />
    <trace from=".C_REGIN > .pin2" to="net.GND" />

    <capacitor name="C_REGOUT" capacitance="22uF" footprint="0805"
      pcbX={10} pcbY={-22} pcbRotation={90}
      supplierPartNumbers={{ jlcpcb: ["C45783"] }} />
    <trace from=".C_REGOUT > .pin1" to="net.VCC3V3" />
    <trace from=".C_REGOUT > .pin2" to="net.GND" />

    <capacitor name="C_REGDEC" capacitance="100nF" footprint="0603"
      pcbX={10} pcbY={-17}
      supplierPartNumbers={{ jlcpcb: ["C14663"] }} />
    <trace from=".C_REGDEC > .pin1" to="net.VCC3V3" />
    <trace from=".C_REGDEC > .pin2" to="net.GND" />

    {/* ═══════════════════════════════════════════════════════
        FRONT SIDE — UPPER ZONE (above battery, Z=65-145mm)
        Full interior depth available
        ═══════════════════════════════════════════════════════ */}

    {/* ── Y=-2 (Z=73mm): Audio section ────────────────────── */}
    <chip name="J_MIC" footprint="pinrow5"
      pcbX={-8} pcbY={-2} pcbRotation={90} schX={8} schY={-5}
      pinLabels={{
        pin1: "MIC_VCC", pin2: "MIC_GND", pin3: "MIC_WS",
        pin4: "MIC_SCK", pin5: "MIC_SD",
      }} />
    <trace from=".J_MIC > .MIC_VCC" to="net.VCC3V3" />
    <trace from=".J_MIC > .MIC_GND" to="net.GND" />
    <trace from=".J_MIC > .MIC_WS"  to="net.I2S_WS" />
    <trace from=".J_MIC > .MIC_SCK" to="net.I2S_SCK" />
    <trace from=".J_MIC > .MIC_SD"  to="net.I2S_SDI" />

    <capacitor name="C_MIC" capacitance="100nF" footprint="0603"
      pcbX={-2} pcbY={-6}
      supplierPartNumbers={{ jlcpcb: ["C14663"] }} />
    <trace from=".C_MIC > .pin1" to="net.VCC3V3" />
    <trace from=".C_MIC > .pin2" to="net.GND" />

    <chip name="U_AMP" footprint="qfn16"
      pcbX={6} pcbY={-2} schX={8} schY={5}
      supplierPartNumbers={{ jlcpcb: ["C910544"] }}
      pinLabels={{
        pin1: "SD_MODE", pin2: "GAIN", pin3: "GND1",
        pin4: "DIN", pin5: "BCLK", pin6: "GND2",
        pin7: "LRCLK", pin8: "VDD",
        pin9: "OUT_P", pin10: "NC1", pin11: "NC2", pin12: "OUT_N",
        pin13: "GND3", pin14: "NC3", pin15: "NC4", pin16: "GND4",
      }} />
    <trace from=".U_AMP > .VDD"     to="net.VCC3V3" />
    <trace from=".U_AMP > .GND1"    to="net.GND" />
    <trace from=".U_AMP > .GND2"    to="net.GND" />
    <trace from=".U_AMP > .GND3"    to="net.GND" />
    <trace from=".U_AMP > .GND4"    to="net.GND" />
    <trace from=".U_AMP > .BCLK"    to="net.I2S_SCK" />
    <trace from=".U_AMP > .LRCLK"   to="net.I2S_WS" />
    <trace from=".U_AMP > .DIN"     to="net.I2S_SDO" />
    <trace from=".U_AMP > .OUT_P"   to=".J_SPK > .SPK_P" />
    <trace from=".U_AMP > .OUT_N"   to=".J_SPK > .SPK_N" />
    <trace from=".U_AMP > .SD_MODE" to="net.VCC3V3" />
    <trace from=".U_AMP > .GAIN"    to="net.GND" />

    <capacitor name="C_AMP1" capacitance="10uF" footprint="0805"
      pcbX={10} pcbY={3}
      supplierPartNumbers={{ jlcpcb: ["C15850"] }} />
    <trace from=".C_AMP1 > .pin1" to="net.VCC3V3" />
    <trace from=".C_AMP1 > .pin2" to="net.GND" />

    <capacitor name="C_AMP2" capacitance="100nF" footprint="0603"
      pcbX={10} pcbY={-7}
      supplierPartNumbers={{ jlcpcb: ["C14663"] }} />
    <trace from=".C_AMP2 > .pin1" to="net.VCC3V3" />
    <trace from=".C_AMP2 > .pin2" to="net.GND" />

    {/* ── Y=+13 (Z=88mm): MCU ─────────────────────────────── */}
    <chip name="U_MCU" footprint="dip14"
      pcbX={0} pcbY={13} schX={0} schY={0}
      pinLabels={{
        pin1: "D0", pin2: "D1", pin3: "D2", pin4: "D3",
        pin5: "D4", pin6: "D5", pin7: "D6",
        pin8: "D7", pin9: "D8", pin10: "D9", pin11: "D10",
        pin12: "3V3", pin13: "GND", pin14: "5V",
      }} />
    <trace from=".U_MCU > .3V3" to="net.VCC3V3" />
    <trace from=".U_MCU > .GND" to="net.GND" />
    <trace from=".U_MCU > .5V"  to="net.VBUS" />
    <trace from=".U_MCU > .D6" to="net.I2S_SCK" />
    <trace from=".U_MCU > .D7" to="net.I2S_WS" />
    <trace from=".U_MCU > .D2" to="net.I2S_SDI" />
    <trace from=".U_MCU > .D3" to="net.I2S_SDO" />
    <trace from=".U_MCU > .D4" to="net.BTN_PTT" />
    <trace from=".U_MCU > .D5" to="net.BTN_PWR" />
    <trace from=".U_MCU > .D8" to="net.LED_DATA" />
    <trace from=".U_MCU > .D9" to="net.LED_EN" />

    <capacitor name="C_MCU1" capacitance="100nF" footprint="0603"
      pcbX={-11} pcbY={13}
      supplierPartNumbers={{ jlcpcb: ["C14663"] }} />
    <trace from=".C_MCU1 > .pin1" to="net.VCC3V3" />
    <trace from=".C_MCU1 > .pin2" to="net.GND" />

    <capacitor name="C_MCU2" capacitance="10uF" footprint="0805"
      pcbX={11} pcbY={13}
      supplierPartNumbers={{ jlcpcb: ["C15850"] }} />
    <trace from=".C_MCU2 > .pin1" to="net.VCC3V3" />
    <trace from=".C_MCU2 > .pin2" to="net.GND" />

    {/* ── Y=+55 (Z=130mm): Speaker + LED section ──────────── */}
    <chip name="J_SPK" footprint="pinrow2"
      pcbX={9} pcbY={-12} schX={12} schY={5}
      pinLabels={{ pin1: "SPK_P", pin2: "SPK_N" }} />

    <chip name="J_LED" footprint="pinrow3"
      pcbX={6} pcbY={63} schX={12} schY={0}
      pinLabels={{ pin1: "VDD_LED", pin2: "GND", pin3: "LED_DATA" }} />
    <trace from=".J_LED > .GND" to="net.GND" />
    <trace from=".J_LED > .LED_DATA" to="net.LED_DATA" />
    <trace from=".J_LED > .VDD_LED" to="net.VDD_LED" />

    {/* LED MOSFET + gate resistor */}
    <chip name="Q1" footprint="sot23"
      pcbX={-5} pcbY={55} schX={10} schY={0}
      supplierPartNumbers={{ jlcpcb: ["C8545"] }}
      pinLabels={{ pin1: "GATE", pin2: "SOURCE", pin3: "DRAIN" }} />
    <trace from=".Q1 > .GATE"   to="net.LED_EN" />
    <trace from=".Q1 > .SOURCE" to="net.GND" />
    <trace from=".Q1 > .DRAIN"  to="net.VDD_LED" />

    <resistor name="R_GATE" resistance="10k" footprint="0603"
      pcbX={5} pcbY={55}
      supplierPartNumbers={{ jlcpcb: ["C25804"] }} />
    <trace from=".R_GATE > .pin1" to="net.LED_EN" />
    <trace from=".R_GATE > .pin2" to="net.GND" />

    {/* ═══════════════════════════════════════════════════════
        MOUNTING HOLES — 6x M2, supporting mechanical stress
        ═══════════════════════════════════════════════════════ */}

    {/* Bottom pair: supports USB-C zone (Z≈18mm, Y=-57) */}
    <hole name="MH1" diameter="2.2mm" pcbX={-11} pcbY={-57} />
    <hole name="MH2" diameter="2.2mm" pcbX={11}  pcbY={-57} />

    {/* Mid pair: between USB-C and power button (Z≈38mm, Y=-37) */}
    <hole name="MH3" diameter="2.2mm" pcbX={-11} pcbY={-37} />
    <hole name="MH4" diameter="2.2mm" pcbX={11}  pcbY={-37} />

    {/* Mid-upper pair: between MCU and PTT (Z≈97mm, Y=+22) */}
    <hole name="MH5" diameter="2.2mm" pcbX={-11} pcbY={22} />
    <hole name="MH6" diameter="2.2mm" pcbX={11}  pcbY={22} />

    {/* Upper pair: flanks PTT switch (Z≈115mm, Y=+40) */}
    <hole name="MH7" diameter="2.2mm" pcbX={-11} pcbY={40} />
    <hole name="MH8" diameter="2.2mm" pcbX={11}  pcbY={40} />

    {/* Top pair: near top of board (Z≈140mm, Y=+65) */}
    <hole name="MH9"  diameter="2.2mm" pcbX={-11} pcbY={67} />
    <hole name="MH10" diameter="2.2mm" pcbX={11}  pcbY={67} />
  </board>
)
