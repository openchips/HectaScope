#!/usr/bin/env python3

#
# This file is part of FastScope.
#
# Copyright (C) 2012-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023-2024 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import time

from litex import RemoteClient

bus = RemoteClient()
bus.open()

# # #

print("Disable JESD PHYs/Core.")
bus.regs.adc08dj_jesd_phy0_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy1_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy2_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy3_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy4_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy5_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy6_tx_enable.write(0)
bus.regs.adc08dj_jesd_phy7_tx_enable.write(0)

bus.regs.adc08dj_jesd_phy0_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy1_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy2_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy3_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy4_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy5_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy6_rx_enable.write(0)
bus.regs.adc08dj_jesd_phy7_rx_enable.write(0)

bus.regs.adc08dj_jesd_rx_control_control.write(0)
time.sleep(1)

print("Enable JESD TX PHYs.")
bus.regs.adc08dj_jesd_phy0_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy1_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy2_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy3_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy4_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy5_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy6_tx_enable.write(1)
bus.regs.adc08dj_jesd_phy7_tx_enable.write(1)
time.sleep(1)

print("Enable JESD RX PHYs.")
bus.regs.adc08dj_jesd_phy0_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy1_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy2_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy3_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy4_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy5_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy6_rx_enable.write(1)
bus.regs.adc08dj_jesd_phy7_rx_enable.write(1)

time.sleep(1)

print("Enable JESD RX Core")
bus.regs.adc08dj_jesd_rx_control_control.write(1 | (1 << 8)) # FIXME: Disable ILAS Check for now, need to check parameters.
time.sleep(1)

# # #

bus.close()
