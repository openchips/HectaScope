#!/usr/bin/env python3

import time

from litex import RemoteClient

bus = RemoteClient()
bus.open()

# # #

print("Disable JESD PHYs/Core.")
bus.regs.jesd_phy0_tx_enable.write(0)
bus.regs.jesd_phy1_tx_enable.write(0)
bus.regs.jesd_phy2_tx_enable.write(0)
bus.regs.jesd_phy3_tx_enable.write(0)
bus.regs.jesd_phy0_rx_enable.write(0)
bus.regs.jesd_phy1_rx_enable.write(0)
bus.regs.jesd_phy2_rx_enable.write(0)
bus.regs.jesd_phy3_rx_enable.write(0)
bus.regs.jesd_rx_control_control.write(0)
time.sleep(1)

print("Enable JESD TX PHYs.")
bus.regs.jesd_phy0_tx_enable.write(1)
bus.regs.jesd_phy1_tx_enable.write(1)
bus.regs.jesd_phy2_tx_enable.write(1)
bus.regs.jesd_phy3_tx_enable.write(1)
time.sleep(1)

print("Enable JESD RX PHYs.")
bus.regs.jesd_phy0_rx_enable.write(1)
bus.regs.jesd_phy1_rx_enable.write(1)
bus.regs.jesd_phy2_rx_enable.write(1)
bus.regs.jesd_phy3_rx_enable.write(1)
time.sleep(1)

print("Enable JESD RX Core")
bus.regs.jesd_rx_control_control.write(1 | (1 << 8)) # FIXME: Disable ILAS Check for now, need to check parameters.
time.sleep(1)

# # #

bus.close()
