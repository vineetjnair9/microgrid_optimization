"""Stage C2: corrected wind power-curve coefficients in App. A (matches the code fix)."""
from texedit import Ed
e = Ed()
e.rep(r"""A & = \frac{1}{v_c^2 - v_r^2} \left(v_c(v_c + v_r) - 4 v_c v_r \left(\frac{(v_c + v_r)}{2v_r}\right)^3 \right), \quad B = \frac{1}{v_c^2 - v_r^2} \left(4 (v_c + v_r) \left(\frac{(v_c + v_r)}{2v_r}\right)^3 - 3(v_c + v_r)\right) \\""",
      r"""A & = \frac{1}{(v_c - v_r)^2} \left(v_c(v_c + v_r) - 4 v_c v_r \left(\frac{(v_c + v_r)}{2v_r}\right)^3 \right), \quad B = \frac{1}{(v_c - v_r)^2} \left(4 (v_c + v_r) \left(\frac{(v_c + v_r)}{2v_r}\right)^3 - (3v_c + v_r)\right) \\""")
e.rep(r"""C & = \frac{1}{v_c^2 - v_r^2} \left(2 - 4 \left(\frac{(v_c + v_r)}{2v_r}\right)^3 \right)""",
      r"""C & = \frac{1}{(v_c - v_r)^2} \left(2 - 4 \left(\frac{(v_c + v_r)}{2v_r}\right)^3 \right)""")
e.save()
