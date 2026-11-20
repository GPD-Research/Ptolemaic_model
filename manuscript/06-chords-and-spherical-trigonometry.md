# Chapter PT-6: Chords and Spherical Trigonometry

Ptolemy had no sine function. Book I builds trigonometry on the **chord**: the straight line subtending an arc of a circle of radius 60 parts,

$$\mathrm{crd}(\alpha) = 120 \sin(\alpha/2).$$

## The table of chords (Almagest I.11)
He tabulated chords for every half degree from ½° to 180°, in base 60 to seconds (crd 1° = 1;2,50), with a column of "sixtieths" for interpolating to one minute of arc. He derived the values geometrically: from the regular pentagon and decagon, Ptolemy's theorem on cyclic quadrilaterals (which contains the angle-sum and difference formulas), and the half-angle construction. His values are good to within a few seconds, about one part in 100,000 of the radius, far finer than naked-eye observation needs. `src/trigonometry.py` recomputes it in his format.

## Menelaus's theorem on the sphere (I.13-16)
For arcs of great circles, Menelaus's theorem relates the chords of the segments cut by a transversal. Ptolemy uses it to turn ecliptic longitude into declination, crd(2δ) = crd(2ε)·crd(2λ)/120 (sin δ = sin ε sin λ), and into right ascension. These conversions, with his obliquity ε = 23°51′20″, give the tables of rising times that let an observer at any latitude find when a point of the ecliptic rises. They are the ancestors of today's coordinate transformations.
