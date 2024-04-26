#!/usr/bin/env python3

#
# This file is part of FastScope.
#
# Copyright (C) 2012-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023-2024 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import time
import argparse
import threading

from litex import RemoteClient

# Board Monitor  -----------------------------------------------------------------------------------

def run_board_monitor(csr_csv, port):
    import dearpygui.dearpygui as dpg

    bus = RemoteClient(csr_csv=csr_csv, port=port)
    bus.open()

    # Create Main Window.
    dpg.create_context()
    dpg.create_viewport(title="AXAU15-ADC08DJ5200RF Board Monitor", max_width=800, always_on_top=True)
    dpg.setup_dearpygui()

    def get_identifier():
        identifier = ""
        for i in range(256):
            c = chr(bus.read(bus.bases.identifier_mem + 4*i) & 0xff)
            identifier += c
            if c == "\0":
                break
        return identifier

    def get_phy_tx_polarity(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_tx_polarity").read() & 0x1

    def get_phy_tx_enable(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_tx_enable").read() & 0x1

    def get_phy_tx_ready(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_tx_ready").read()  & 0x1

    def get_phy_rx_polarity(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_rx_polarity").read() & 0x1

    def get_phy_rx_enable(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_rx_enable").read() & 0x1

    def get_phy_rx_ready(n):
        return getattr(bus.regs, f"adc08dj_jesd_phy{n}_rx_ready").read()  & 0x1

    def get_core_tx_enable():
        return getattr(bus.regs, f"adc08dj_jesd_tx_control_control").read() & 0x1

    def get_core_rx_enable():
        return getattr(bus.regs, f"adc08dj_jesd_rx_control_control").read() & 0x1

    def get_core_tx_ready():
        return getattr(bus.regs, f"adc08dj_jesd_tx_control_status").read() & 0x1

    def get_core_rx_ready():
        return getattr(bus.regs, f"adc08dj_jesd_rx_control_status").read() & 0x1

    # Create JESD Window.
    with dpg.window(label="AXAU15-ADC08DJ5200RF Control/Status"):
        dpg.add_text("SoC")
        dpg.add_text(f"Identifier: {get_identifier()}")

        dpg.add_text("")
        with dpg.group(horizontal=True):
            dpg.add_text("RefClk: ")
            dpg.add_text(" - MHz", tag=f"refclk_freq")

        dpg.add_text("")
        dpg.add_text("PHY TX    0   1   2   3")
        with dpg.group(horizontal=True):
            dpg.add_text("Polarity ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_tx_polarity{i}")
        with dpg.group(horizontal=True):
            dpg.add_text("Enable   ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_tx_enable{i}")
        with dpg.group(horizontal=True):
            dpg.add_text("Ready    ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_tx_ready{i}")

        dpg.add_text("")
        dpg.add_text("PHY RX    0   1   2   3")
        with dpg.group(horizontal=True):
            dpg.add_text("Polarity ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_rx_polarity{i}")
        with dpg.group(horizontal=True):
            dpg.add_text("Enable   ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_rx_enable{i}")
        with dpg.group(horizontal=True):
            dpg.add_text("Ready    ")
            for i in range(4):
                dpg.add_checkbox(tag=f"phy_rx_ready{i}")

        dpg.add_text("")
        dpg.add_text("Core RX")
        with dpg.group(horizontal=True):
            dpg.add_text("Enable ")
            dpg.add_checkbox(tag=f"core_rx_enable")
        with dpg.group(horizontal=True):
            dpg.add_text("Ready  ")
            dpg.add_checkbox(tag=f"core_rx_ready")

    def timer_callback(refresh=1e-1, xadc_points=100):
        refclk_last = 0
        time_last   = 0
        iteration   = 0
        while dpg.is_dearpygui_running():
            # RefClk.
            if (iteration%10 == 9):
                bus.regs.adc08dj_refclk_measurement_latch.write(1)
                refclk_curr = bus.regs.adc08dj_refclk_measurement_value.read()
                time_curr   = time.time()
                refclk      = (refclk_curr - refclk_last)/(time_curr - time_last)
                time_last   = time_curr
                dpg.set_value("refclk_freq", f"{refclk/1e6} MHz")
                refclk_last = refclk_curr
            iteration += 1

            # PHY TX.
            for i in range(4):
                dpg.set_value(f"phy_tx_polarity{i}", bool(get_phy_tx_polarity(i)))
            for i in range(4):
                dpg.set_value(f"phy_tx_enable{i}", bool(get_phy_tx_enable(i)))
            for i in range(4):
                dpg.set_value(f"phy_tx_ready{i}", bool(get_phy_tx_ready(i)))
            # PHY RX.
            for i in range(4):
                dpg.set_value(f"phy_rx_polarity{i}", bool(get_phy_rx_polarity(i)))
            for i in range(4):
                dpg.set_value(f"phy_rx_enable{i}", bool(get_phy_rx_enable(i)))
            for i in range(4):
                dpg.set_value(f"phy_rx_ready{i}", bool(get_phy_rx_ready(i)))
            # Core RX.
            dpg.set_value(f"core_rx_enable", bool(get_core_rx_enable()))
            dpg.set_value(f"core_rx_ready", bool(get_core_rx_ready()))

            time.sleep(refresh)

    timer_thread = threading.Thread(target=timer_callback)
    timer_thread.start()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    bus.close()

# Run ----------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXAU15-ADC08DJ5200RF Board Monitor.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--csr-csv", default="csr.csv", help="CSR configuration file")
    parser.add_argument("--port",    default="1234",    help="Host bind port.")
    args = parser.parse_args()

    csr_csv = args.csr_csv
    port    = int(args.port, 0)

    run_board_monitor(csr_csv=csr_csv, port=port)

if __name__ == "__main__":
    main()

