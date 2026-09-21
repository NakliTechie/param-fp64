# SOURCES — every published or reconstructed cell resolves here

`bench.py check` requires each `citation` in `results/published.csv` to match a `### \`key\`` heading below.
Tiers follow the strand handoff: **primary** (stated plainly) · **secondary** (source named) · **attributed** (a claim, quoted as a claim, never in a table cell).

## Primary

### `tn06`
Inmos Technical Note 6, *IMS T800 Architecture*, Inmos Bristol, January 1988. Archived at transputer.net: <http://www.transputer.net/tn/06/tn06.html> (PDF: <http://www.transputer.net/tn/06/tn06.pdf>). Fetched 2026-09-21.
Quoted: "As a simple example of overlapping consider the implementation of Livermore Loop 7 (see appendix). The IMS T800-30 achieves a speed of 2.25 Mflops on this benchmark; for comparison the IMS T800-20 achieves 1.5 Mflops, the T414-20 achieves 0.09 Mflops and a VAX 11/780 (with fpa) achieves 0.54 Mflops."
**Precision: single-length (FP32).** The compiled-code walkthrough that follows the figure uses `floating load indexed single` and the occam fragment is typed against REAL32. These four cells are therefore FP32 and carry that label in the table; they are not FP64 numbers. The document's T800 abstract figure "capable of sustaining 2.25 MFlops" is the same single-length LL7 number.

### `dongarra-2014`
Jack J. Dongarra, *Performance of Various Computers Using Standard Linear Equations Software*, CS-89-85, University of Tennessee / ORNL, edition dated June 15, 2014. <https://www.netlib.org/benchmark/performance.pdf>. Fetched 2026-09-21. Table 1 ("LINPACK Benchmark", n=100, no source changes permitted; "Toward Peak", n=1000, best effort; "Theoretical Peak"). Precision: full precision, 64-bit ("On some machines full precision may be single precision, such as the Cray" — Cray single = 64-bit).
Rows used, as printed:
- `Cray X-MP/14se (10 ns)   cf77 3.0   53   184   210`
- `Cray X-MP/416 (1 proc. 8.5 ns)   CF77 5.0 -Zp -Wd-e68   121   218   235`
- `Inmos T800 (20 MHz)   Fortran 3L -:o0   .37` (n=100 only)
- `CSA w/T800C-20   Fortran 3L   .37` (same figure, second listing)
Note: the machine India was refused in 1987 was an X-MP/24 and the machine installed at NCMRWF in 1988–89 was an X-MP/14; Dongarra's table lists the X-MP/14se (10 ns clock). The 1985 Cray brochure gives the X-MP/1 clock as 9.5 ns; 2 results/clock × 105.3 MHz = 210.5 MFLOPS, which is the 210 peak printed. We cite the /14se row as the nearest published single-CPU X-MP figure and label the machine id accordingly.

### `cray-1985-brochure`
Cray Research, *The CRAY X-MP Series of Computer Systems*, 1985, MP-0102. Computer History Museum: <http://s3data.computerhistory.org/brochures/cray.x-mp.1985.102646183.pdf>. Fetched 2026-09-21. Used only for the 9.5 ns clock and 64-bit word size of the X-MP/1 models; the brochure text does not state a MFLOPS figure.

## Secondary (source named)

### `kahaner-1996`
D. K. Kahaner, "Parallel computing in India", *IEEE Parallel & Distributed Technology* 4(3), 1996, pp. 7–11, doi:10.1109/88.532134, as summarised in the Wikipedia article *PARAM* (revision fetched 2026-09-21), which attributes to it: "A 64-node machine was delivered in August 1991"; "A 256-node machine had a theoretical performance of 1 GFLOPS, however in practice had a sustained performance of 100–200 MFLOPS." The Wikipedia article co-cites L. M. Patnaik, *High Performance Computing in India and Far-East* (UNIDO) for the same figures; the UNIDO link now redirects and was not retrievable on 2026-09-21. The `sustained` cell is entered as 150, the midpoint of the quoted 100–200 range, and is a 256-node figure — not a 64-node one. **I did not read the IEEE paper itself**; the figures are relayed via Wikipedia's citation and should be upgraded once the paper is in hand.

## Reconstructed

### `param-64-ceiling`
PARAM 8000 64-node LINPACK n=100: **64 × 0.37 MFLOPS = 23.7 MFLOPS**, where 0.37 is the single T800-20 figure from `dongarra-2014`. This is an arithmetic ceiling — 64 independent single-node solves with zero communication — not a measured parallel LINPACK, which would be lower. It is entered so that the table has a PARAM cell at all and is marked `reconstructed`. v1.2 replaces it with an emulated run.

## Attributed — claims, quoted as claims, never in a cell

- "28 times more powerful than the Cray X-MP that the government originally requested, for the same $10 million cost" — V. Rajaraman, *Super computers*, Universities Press (India), 1999, p. 75, as cited by Wikipedia *PARAM*. Rajaraman was a C-DAC-adjacent academic; the claim originates in C-DAC's own account.
- "of the machines that ran at the [1990 Zurich Super-computing Show] it came second only to one from the United States" — *Outlook Business*, "God, Man And Machine", 1 July 1998, as cited by Wikipedia *PARAM*. Wikipedia's own editorial note: the event is probably CONPAR 90 – VAPP IV (Zurich, 10–13 September 1990) and "the statement is difficult to fully attest to other than the referenced article."
- Exports "to Germany, United Kingdom and Russia" — *The Hindu Business Line*, 26 February 2001, and C-DAC's own ICAD Moscow page, as cited by Wikipedia *PARAM*. Self-reported by C-DAC in part.
- "attracted 14 other buyers with its relatively low price tag of $350,000" — *Washington Post* archive, as cited by Wikipedia *PARAM*.
