#
# This file is part of FastScope.
#
# Copyright (C) 2012-2024 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2023-2024 John Simons <jammsimons@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.genlib.cdc import PulseSynchronizer, MultiReg

from litex.gen import *

from litex.build.xilinx.common import DifferentialInput

from litex.soc.cores.clock import *
from litex.soc.interconnect.csr import *

from liteiclink.serdes.gth4_ultrascale import GTH4QuadPLL, GTH4

from litejesd204b.common import *
from litejesd204b.core import LiteJESD204BCoreTX
from litejesd204b.core import LiteJESD204BCoreRX
from litejesd204b.core import LiteJESD204BCoreControl

# ADC08DJ5200RF Core -------------------------------------------------------------------------------

class ADC08DJ5200RFCore(LiteXModule):
    def __init__(self, platform, sys_clk_freq,
        adc08dj_jesd_lanes,
        adc08dj_refclk_freq,
        adc08dj_jesd_linerate,
        adc08dj_phy_rx_order,
        adc08dj_phy_rx_polarity,
        scrambling  = True,
        stpl_random = True,
        framing     = False,
    ):
        # JESD Configuration -----------------------------------------------------------------------
        if adc08dj_jesd_lanes == 4:
            ps_rx = JESD204BPhysicalSettings(l=4, m=4, n=8, np=8)
        if adc08dj_jesd_lanes == 8:
            ps_rx = JESD204BPhysicalSettings(l=8, m=8, n=8, np=8)
        ts_rx = JESD204BTransportSettings(f=2, s=1, k=32, cs=0)
        settings_rx = JESD204BSettings(ps_rx, ts_rx, did=0x5a, bid=0x5, framing=framing, scrambling=scrambling)

        # JESD Clocking (Device) -------------------------------------------------------------------
        userclk_freq = adc08dj_jesd_linerate/40 # 6.25GHz / 40 = 156.25 MHz
        self.cd_jesd   = ClockDomain()
        self.cd_refclk = ClockDomain()

        refclk_pads      = platform.request("adc08dj5200rf_refclk")
        refclk           = Signal()
        refclk_div2      = Signal()
        refclk_div2_bufg = Signal()
        self.specials += Instance("IBUFDS_GTE4",
            p_REFCLK_HROW_CK_SEL = 0b01,
            i_CEB   = 0,
            i_I     = refclk_pads.p,
            i_IB    = refclk_pads.n,
            o_O     = refclk,
            o_ODIV2 = refclk_div2,
        )
        bufg_gt_ce  = Signal()
        bufg_gt_clr = Signal()
        self.specials += Instance("BUFG_GT_SYNC",
            i_CLK     = refclk_div2,
            i_CE      = 1,
            i_CLR     = 0,
            o_CESYNC  = bufg_gt_ce,
            o_CLRSYNC = bufg_gt_clr,
        )
        self.specials += Instance("BUFG_GT",
            i_CE  = bufg_gt_ce,
            i_CLR = bufg_gt_clr,
            i_I   = refclk_div2,
            o_O   = refclk_div2_bufg,
        )
        self.submodules.pll = pll = USPMMCM(speedgrade=-2)
        pll.register_clkin(refclk_div2_bufg, adc08dj_refclk_freq/2)
        pll.create_clkout(self.cd_jesd, userclk_freq, with_reset=False)
        pll.create_clkout(self.cd_refclk, adc08dj_refclk_freq)
        platform.add_period_constraint(refclk_div2, 1e9/(adc08dj_refclk_freq/2))

        # JESD Clocking (SysRef) -------------------------------------------------------------------
        self.sysref = sysref = Signal()
        sysref_pads = platform.request("adc08dj5200rf_sysref")
        self.specials += DifferentialInput(sysref_pads.p, sysref_pads.n, sysref)

        # JESD PHYs --------------------------------------------------------------------------------
        self.jesd_phys = jesd_phys = []
        for i in range(adc08dj_jesd_lanes):
            # GTH4QuadPLL (1 shared per quad).
            if (i%4 == 0):
                jesd_pll = GTH4QuadPLL(refclk, adc08dj_refclk_freq, adc08dj_jesd_linerate)
                self.submodules += jesd_pll
                print(jesd_pll)
            # GTH4.
            jesd_tx_pads = platform.request("adc08dj5200rf_jesd_tx", i)
            jesd_rx_pads = platform.request("adc08dj5200rf_jesd_rx", i)
            jesd_phy = GTH4(jesd_pll, jesd_tx_pads, jesd_rx_pads, sys_clk_freq,
                data_width       = 40,
                clock_aligner    = False,
                tx_buffer_enable = True,
                rx_buffer_enable = True,
                tx_polarity      = 0,
                rx_polarity      = adc08dj_phy_rx_polarity[i],
                tx_clk           = None if (i == 0) else jesd_phys[0].cd_tx.clk,
                rx_clk           = None if (i == 0) else jesd_phys[0].cd_rx.clk,
            )
            jesd_phy.add_stream_endpoints()
            jesd_phy.add_controls(auto_enable=False)
            jesd_phy.n = i
            setattr(self.submodules, "jesd_phy" + str(i), jesd_phy)
            platform.add_period_constraint(jesd_phy.cd_tx.clk, 1e9/jesd_phy.tx_clk_freq)
            platform.add_period_constraint(jesd_phy.cd_rx.clk, 1e9/jesd_phy.rx_clk_freq)
            platform.add_false_path_constraints(
                LiteXContext.top.crg.cd_sys.clk,
                self.cd_jesd.clk,
                jesd_phy.cd_tx.clk,
                jesd_phy.cd_rx.clk)
            jesd_phys.append(jesd_phy)

        jesd_phys_tx_init_done = reduce(and_, [phy.tx_init.done for phy in jesd_phys])
        jesd_phys_rx_init_done = reduce(and_, [phy.rx_init.done for phy in jesd_phys])
        self.specials += AsyncResetSynchronizer(self.cd_jesd, ~(jesd_phys_tx_init_done & jesd_phys_rx_init_done))

        jesd_phys_rx = [jesd_phys[adc08dj_phy_rx_order[n]] for n in range(adc08dj_jesd_lanes)]

        # JESD RX ----------------------------------------------------------------------------------
        self.submodules.jesd_rx_core    = LiteJESD204BCoreRX(jesd_phys_rx, settings_rx,
            converter_data_width = adc08dj_jesd_lanes*8,
            scrambling           = scrambling,
            stpl_random          = stpl_random,
        )
        self.submodules.jesd_rx_control = LiteJESD204BCoreControl(self.jesd_rx_core, sys_clk_freq)
        self.jesd_rx_core.register_jsync(platform.request("adc08dj5200rf_sync"))
        self.jesd_rx_core.register_jref(sysref)

        # JESD Link Status -------------------------------------------------------------------------
        self.jesd_link_status = Signal()
        self.comb += self.jesd_link_status.eq(
            (self.jesd_rx_core.enable & self.jesd_rx_core.jsync) &
            (self.jesd_rx_core.enable & self.jesd_rx_core.jsync))

        # Clk Measurements -------------------------------------------------------------------------

        class ClkMeasurement(LiteXModule):
            def __init__(self, clk, increment=1):
                self.latch = CSR()
                self.value = CSRStatus(64)

                # # #

                # Create Clock Domain.
                self.cd_counter = ClockDomain()
                self.comb += self.cd_counter.clk.eq(clk)
                self.specials += AsyncResetSynchronizer(self.cd_counter, ResetSignal())

                # Free-running Clock Counter.
                counter = Signal(64)
                self.sync.counter += counter.eq(counter + increment)

                # Latch Clock Counter.
                latch_value = Signal(64)
                latch_sync  = PulseSynchronizer("sys", "counter")
                self.submodules += latch_sync
                self.comb += latch_sync.i.eq(self.latch.re)
                self.sync.counter += If(latch_sync.o, latch_value.eq(counter))
                self.specials += MultiReg(latch_value, self.value.status)

        self.refclk_measurement = ClkMeasurement(clk=self.cd_refclk.clk)
