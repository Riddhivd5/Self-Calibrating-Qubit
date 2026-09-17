## discriminator_constraints.xdc
##
## Basic timing constraint for the baseline discriminator.
## This defines the clock period Vivado should check your design against.
## Without this file, Vivado has no target and reports meaningless
## "infinite slack" results, as you just saw.
##
## Target: 100 MHz (10 ns period) as a first, comfortable test point —
## well within reach for a design this small (21 LUTs, 2 DSPs), and gives
## you a real number to compare against your ~40ns per-decision budget.
## Once this passes cleanly, you can tighten the period to push toward
## the actual project target and see how much margin you have.

create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]

## Optional but good practice: tell Vivado this is an asynchronous-style
## reset input, not a second clock, so it doesn't try to time-analyze it
## as a clock path.
set_false_path -from [get_ports rst_n]
