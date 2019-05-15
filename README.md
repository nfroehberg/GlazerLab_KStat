# KStat open source potentiostat

The KStat is an adaptation with small changes to the firmware and PCB design of the open source DStat potentiostat by Michael Dryden for use with Hg/Au microelectrodes in in-situ meaurements.

Documentation for the original design: http://microfluidics.utoronto.ca/gitlab/dstat/dstat-documentation/wikis/home

For the KStat, the potential range of the potentiostat was increased from 3 to 4 (+- 2) V and the shape of the board changed from square to rectangular for easier integration in underwater housings.
As it is intended to be used in conjunction with other sensors and manipulators, the KStat uses a command-line python interface instead of the original GUI. For data analysis, a TKinter GUI was developed to display cyclic voltammograms, fit and/or remove a polynomial baseline, filter out A/C noise and measure peak heights.
Additional scripts include pH measurement and various tests used during the development.

Adaptations to firmware and PCB design by Stanley Lio.
Development of Python Interface by Nico Fröhberg.
