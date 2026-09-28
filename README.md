# Ternary Diagrams

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

Desktop application in Python to draw ternary phase diagrams with a monophasic
region (1F) and a biphasic region (2F) separated by a fitted phase boundary.

## Requirements

- Python 3.9 or newer
- Tkinter (on some Linux distributions install `python3-tk`)
- NumPy, SciPy and Matplotlib

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python ternary_gui.py
```

The interface language is selected in the **Language / Idioma** combo box
(`pt` or `en`); all labels are updated immediately.

## Input data

Enter the three component names separated by commas (`A, B, C` by default).
Each data row contains the mole fraction of A, the mole fraction of B and the
experimental classification `1F` or `2F`. The third fraction is calculated as:

`Xc = 1 − (Xa + Xb)`

Data rules:

- every fraction must be between 0 and 1, and `Xa + Xb` cannot exceed 1;
- comma, semicolon or space are accepted as separators;
- rows starting with `#` are ignored;
- the **Number of points** field must match the number of filled rows;
- at least 3 valid points, including at least 2 points `2F` with different
  fractions of A.

### Example

```text
0.70, 0.15, 1F
0.62, 0.30, 1F
0.55, 0.20, 1F
0.05, 0.10, 2F
0.10, 0.45, 2F
0.08, 0.80, 2F
0.20, 0.25, 2F
0.18, 0.65, 2F
```

## Phase boundary

The curve is fitted **only to the `2F` points**:

1. the `2F` points are sorted by their horizontal position in the triangle;
2. for each abscissa the highest `2F` point is kept, so no `2F` point is left
   above the curve;
3. a PCHIP spline (monotone on each segment) connects those points without
   overshoot and passes exactly through them;
4. outside the range of the points the curve follows the tangent of the
   corresponding end until it reaches the edges of the triangle.

The classification follows the curve: **below the curve the phase is 2F and
above it is 1F**. Because the PCHIP spline never overshoots, every `2F` point
lies exactly on the boundary and none of them is painted as `1F`; `1F` points
are drawn but do not take part in the fit. The shape of the curve depends on
the distribution of the `2F` points, so measurements close to the boundary
refine the result.

## The plot

**Generate plot** draws the classic ternary phase diagram:

- equilateral triangle with a black frame and the two regions filled with grey
  tones;
- percentages from 10 to 90 on the base (fraction of B), on the right edge
  (fraction of A) and on the left edge (fraction of C);
- dashed grid every 10 %, with one family of parallel lines per fraction
  joining the edges of the triangle, like isometric paper;
- component name at each vertex and the `A - B - C` title above the triangle;
- phase label (`1-phase` / `2-phase`) inside each region;
- legend with colour samples placed on the left, outside the triangle;
- the measured points are drawn as circles in the colour of their phase, and the
  phase boundary as a black line in the selected style.

**Save plot** exports the current figure to PNG, JPEG, SVG or PostScript. The
built-in toolbar allows zooming and panning, and **About** shows the version,
author, date and affiliations.

Colours of the two regions and the line style of the boundary can be changed in
the **Appearance** group.

## Project files

| File | Description |
| --- | --- |
| `ternary_gui.py` | Application: interface, data validation, boundary fit and plot |
| `requirements.txt` | Python dependencies |
| `README.md` / `README.pt-BR.md` | This documentation (English / Brazilian Portuguese) |
| `ternary-plot-phase-diagram.png` | Layout used as reference for the plot |

## About

- Version 1.0.0
- Author: Dr. Arlan da Silva Gonçalves
- Federal Institute of Education, Science and Technology of Espírito Santo –
  Vila Velha / Vitória Campuses
- Federal University of Espírito Santo – PPGQ / UFES
