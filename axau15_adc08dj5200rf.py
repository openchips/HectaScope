#!/usr/bin/env python3

#
# This file is part of FastScope.
#
# Copyright (c) 2023-2024 John Simons <jammsimons@gmail.com>
# Copyright (C) 2012-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Test:
# - Configure ADC08DJ52000RFEVM with TI's EVM GUI.
# - ./axau15_adc08dj5200rf.py --build --load
# - ping 192.168.1.50
# - litex_server --udp
# - cd test
# - ./board_monitor.py
# - ./test_jesd.py
# - litescope_cli

import os
import argparse

from migen import *

from litex.gen import *

from litex_boards.platforms import alinx_axau15
from litex.build.generic_platform import *

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.interconnect.csr import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.usrgmii import LiteEthPHYRGMII

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

from litescope import LiteScopeAnalyzer

from gateware.adc08dj import ADC08DJ5200RFCore

# ADC08DJ5200RF FMC IOs ----------------------------------------------------------------------------

adc08dj5200rf_fms_ios = [
    # GTH Reference Clk (156.25 MHz).
    # -------------------------------
    ("adc08dj5200rf_refclk", 0,
        Subsignal("p", Pins("HPC:GBTCLK0_M2C_P")),
        Subsignal("n", Pins("HPC:GBTCLK0_M2C_N")),
    ),
    # GTH RX Lanes.
    # -------------
    ("adc08dj5200rf_jesd_rx", 0,
        Subsignal("p",  Pins("HPC:DP0_M2C_P")),
        Subsignal("n",  Pins("HPC:DP0_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 1,
        Subsignal("p",  Pins("HPC:DP1_M2C_P")),
        Subsignal("n",  Pins("HPC:DP1_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 2,
        Subsignal("p",  Pins("HPC:DP2_M2C_P")),
        Subsignal("n",  Pins("HPC:DP2_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 3,
        Subsignal("p",  Pins("HPC:DP3_M2C_P")),
        Subsignal("n",  Pins("HPC:DP3_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 4,
        Subsignal("p",  Pins("HPC:DP4_M2C_P")),
        Subsignal("n",  Pins("HPC:DP4_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 5,
        Subsignal("p",  Pins("HPC:DP5_M2C_P")),
        Subsignal("n",  Pins("HPC:DP5_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 6,
        Subsignal("p",  Pins("HPC:DP6_M2C_P")),
        Subsignal("n",  Pins("HPC:DP6_M2C_N")),
    ),
    ("adc08dj5200rf_jesd_rx", 7,
        Subsignal("p",  Pins("HPC:DP7_M2C_P")),
        Subsignal("n",  Pins("HPC:DP7_M2C_N")),
    ),
    # GTH TX Lanes.(Not used, but still need to be provided to LiteICLink PHY).
    # -------------------------------------------------------------------------
    ("adc08dj5200rf_jesd_tx", 0,
        Subsignal("p",  Pins("HPC:DP0_C2M_P")),
        Subsignal("n",  Pins("HPC:DP0_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 1,
        Subsignal("p",  Pins("HPC:DP1_C2M_P")),
        Subsignal("n",  Pins("HPC:DP1_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 2,
        Subsignal("p",  Pins("HPC:DP2_C2M_P")),
        Subsignal("n",  Pins("HPC:DP2_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 3,
        Subsignal("p",  Pins("HPC:DP3_C2M_P")),
        Subsignal("n",  Pins("HPC:DP3_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 4,
        Subsignal("p",  Pins("HPC:DP4_C2M_P")),
        Subsignal("n",  Pins("HPC:DP4_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 5,
        Subsignal("p",  Pins("HPC:DP5_C2M_P")),
        Subsignal("n",  Pins("HPC:DP5_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 6,
        Subsignal("p",  Pins("HPC:DP6_C2M_P")),
        Subsignal("n",  Pins("HPC:DP6_C2M_N")),
    ),
    ("adc08dj5200rf_jesd_tx", 7,
        Subsignal("p",  Pins("HPC:DP7_C2M_P")),
        Subsignal("n",  Pins("HPC:DP7_C2M_N")),
    ),

    # Jsync.
    # ------
    ("adc08dj5200rf_sync", 0, Pins("HPC:LA28_P"), IOStandard("LVCMOS18")),

    # SysRef.
    # -------
    ("adc08dj5200rf_sysref", 0,
        Subsignal("p", Pins("HPC:LA03_P"), IOStandard("LVDS")),
        Subsignal("n", Pins("HPC:LA03_N"), IOStandard("LVDS"))
    ),

    # SPI.
    # ----
    ("adc08dj5200rf_spi", 0,
        # FIXME: Not yet use in design since configuring ADC through EVM GUI.
        Subsignal("cs_n",   Pins("HPC:LA04_N FMC1_HPC:LA05_P")),
        Subsignal("miso",   Pins("HPC:LA04_P"), Misc("PULLUP TRUE")),
        Subsignal("mosi",   Pins("HPC:LA03_N")),
        Subsignal("clk",    Pins("HPC:LA03_P")),
        Subsignal("spi_en", Pins("HPC:LA05_N")),
        IOStandard("LVCMOS18")
    ),
]

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        # Clk.
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        self.idelayctrl = USIDELAYCTRL(cd_ref=self.cd_idelay, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCMini):
    def __init__(self, sys_clk_freq=int(175e6),
        with_led_chaser  = True,
        with_pcie        = False,
        jesd_lanes       = 4,
        jesd_framing     = True,
        jesd_scrambling  = True,
        jesd_stpl_random = False,
    ):
        assert jesd_lanes in [4, 8]

        # Platform ---------------------------------------------------------------------------------
        platform = alinx_axau15.Platform()
        platform.add_extension(adc08dj5200rf_fms_ios)

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq, ident="FastScope Test SoC on AXAU15.")

        # UARTBone ---------------------------------------------------------------------------------
        self.add_uartbone()

        # Etherbone --------------------------------------------------------------------------------
        self.ethphy = LiteEthPHYRGMII(
            clock_pads = self.platform.request("eth_clocks"),
            pads       = self.platform.request("eth"),
            tx_delay   = 1e-9,
            rx_delay   = 1e-9,
            usp        = True
        )
        self.add_etherbone(phy=self.ethphy, ip_address="192.168.1.50")

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                speed      = "gen3",
                data_width = 128,
                bar0_size  = 0x20000)
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)
            
        # JESD204B ---------------------------------------------------------------------------------
        if jesd_lanes == 4:
            adc08dj_phy_rx_order    = [3, 0, 2, 1]
            adc08dj_phy_rx_polarity = [0, 0, 0, 0]
        if jesd_lanes == 8:
            adc08dj_phy_rx_order    = [3, 0, 2, 1, 7, 4, 6, 5]
            adc08dj_phy_rx_polarity = [0, 0, 0, 0, 1, 1, 1, 1]
        self.adc08dj = ADC08DJ5200RFCore(platform, sys_clk_freq,
            jesd_lanes              = jesd_lanes,
            jesd_framing            = jesd_framing,
            jesd_scrambling         = jesd_scrambling,
            jesd_stpl_random        = jesd_stpl_random,
            adc08dj_refclk_freq     = 156.25e6,
            adc08dj_jesd_linerate   = 6.25e9,
            adc08dj_phy_rx_order    = adc08dj_phy_rx_order,
            adc08dj_phy_rx_polarity = adc08dj_phy_rx_polarity,
        )

    # Analyzer -------------------------------------------------------------------------------------

    def add_jesd_rx_probe(self, depth=512):
        analyzer_signals = [
            self.adc08dj.jesd_rx_core.jsync,
            self.adc08dj.jesd_rx_core.jref,
        ]
        for link in self.adc08dj.jesd_rx_core.links:
            analyzer_signals.append(link.aligner.source)
            analyzer_signals.append(link.fsm)
            analyzer_signals.append(link.ilas.valid)
            analyzer_signals.append(link.ilas.done)
        analyzer_signals.append(self.adc08dj.jesd_rx_core.transport.source)
        self.analyzer = LiteScopeAnalyzer(analyzer_signals,
            depth        = depth,
            clock_domain = "jesd",
            csr_csv      = "test/analyzer.csv",
            register     = True,
        )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="FastScope Test SoC on AXAU15.")
    parser.add_argument("--build",           action ="store_true",      help="Build bitstream.")
    parser.add_argument("--load",            action ="store_true",      help="Load bitstream.")
    parser.add_argument("--sys-clk-freq",    default=175e6, type=float, help="System clock frequency.")
    parser.add_argument("--driver",          action="store_true",       help="Generate LitePCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = args.sys_clk_freq,
	)
    soc.add_jesd_rx_probe()

    builder = Builder(soc, csr_csv="test/csr.csv")
    if args.build:
        builder.build()

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
