# MicroLab v0.1

A local, interactive Python lab for **Advanced Microeconomics, Seminar 3,
Question 1**. Explore the game tree, check every pure-strategy PBE candidate,
practise the calculations, and experiment with payoffs. Solutions start hidden.

## Open and run in VS Code (macOS)

1. Open VS Code. Choose **File → Open Folder** and select this project folder.
2. Install Microsoft's **Python** extension if you do not already have it.
3. Choose **Terminal → New Terminal**. The terminal should be in this folder.
4. The project has a `.venv` virtual environment. A virtual environment keeps
   this project's packages separate from other Python projects. If setting up
   a fresh copy, create it first with `python3 -m venv .venv`.
5. Run:

   ```bash
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

6. Open **http://localhost:8501** in your browser if it does not open automatically.
7. In VS Code, open the command palette (Cmd+Shift+P), choose
   **Python: Select Interpreter**, and select `.venv/bin/python`.

Leave the terminal running while using the app. Press **Ctrl+C** in that
terminal to stop the server. Saving a source file lets Streamlit rerun the app.
You can also run without activating: `.venv/bin/python -m streamlit run app.py`.
On Windows, use `py -m venv .venv` and `.venv\Scripts\Activate.ps1` instead.

## A first experiment

Open **Experiment**, change the Player 1 payoff in the **y / L / u** row from
`0` to `3`, and click **Apply changes**. Then click **Show complete solution**
in the solver. The original separating profile now fails.
Type y would then obtain 3 by switching to L instead of 1 by staying at R.
Expand the candidate to see this inequality calculated.

Click **Reset original homework** to restore all eight pairs and the prior.
Edits are session-local, not saved to disk. To change the source's starting
payoffs, edit `homework_game()` in `models.py`; the tuple order is x/L/u,
x/L/d, x/R/u, x/R/d, y/L/u, y/L/d, y/R/u, y/R/d. Changes to that source also
change the definition of the original game: do not rely on the scoped
refinement proof without updating the mathematical tests and scope checks.
Use Experiment for ordinary payoff exploration.

## What each file does

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit controls, four tabs, hidden solutions, study feedback and session state. |
| `models.py` | Types, signals, actions, payoff data and input validation. |
| `solver.py` | Bayes' rule, receiver best-response intervals, sender constraints, PBE enumeration and the scoped refinement proof. No Streamlit imports. |
| `visualization.py` | Plotly extensive-form tree, information sets and highlighted branches. |
| `explanations.py` | Readable fractions, strategy labels and calculated explanations. |
| `tests/test_solver.py` | Mathematical regression tests, boundary cases and generated edited games. |
| `tests/test_app.py` | Streamlit interaction tests for solutions, study feedback, prior editing and reset. |
| `.streamlit/config.toml` | App colours and typography. |
| `requirements.txt` | The three direct dependencies: Streamlit, Plotly, pytest. |

## Python through the economics

- A **function** such as `bayes_belief(game, sender, signal)` takes inputs and
  returns a result. You can test it without opening the app.
- A **tuple** such as `("L", "R")` is an ordered pair: x's signal first,
  then y's. A receiver tuple instead means response after L, then after R.
- A **dictionary** maps keys to values. `game.payoffs[("x", "L", "u")]`
  retrieves the two payoffs for that terminal node.
- A **dataclass** groups related information. `Game` groups a prior and a
  payoff table; `Candidate` groups strategies, beliefs and incentive checks.
- `Fraction(1, 3)` stores one third exactly. Exact arithmetic prevents a
  floating-point rounding error from turning indifference into a deviation.
- `None` means no value: for a posterior it means an off-path signal; for a
  feasible belief interval it means no belief can support the chosen action.
- A **loop** checks each candidate; a **property** such as `c.is_pbe`
  computes a conclusion from that candidate's checks.
- Streamlit reruns `app.py` when you interact. `st.session_state` preserves
  the edited game and selected solution across those reruns.

Try these lines in a Python terminal opened in the project folder:

```python
from models import homework_game
from solver import enumerate_candidates

game = homework_game()
for candidate in enumerate_candidates(game):
    if candidate.is_pbe:
        print(candidate.sender, candidate.receiver, candidate.beliefs)
```

## Mathematical scope and method

The solver checks four sender strategies and four receiver strategies: **16
profiles**. For reached signals, Bayes' rule fixes P(x | signal). At an unused
signal, the posterior is free in [0,1], subject to receiver optimality.

For receiver action a versus the other action, define Δx and Δy as the payoff
advantages under the two types. The solver solves
`b × Δx + (1 − b) × Δy ≥ 0` exactly. It intersects this closed interval with
the Bayes posterior where required. Thus ties and singleton endpoints count.
Each sender type must weakly prefer staying over deviating, taking the full
receiver strategy as fixed. All those conditions together characterize the
supported pure-strategy PBE assessments in this two-type, two-signal game.

The original game has one separating profile and two pooling receiver
profiles, with off-path beliefs forming intervals. Both signals are reached
in separation. Under pooling on R, neither type can strictly gain by moving
to L even under its best receiver response. This verifies survival of the
original PBEs under the Intuitive Criterion; it is **not a general refinement
algorithm**. The criterion is disabled after changing payoffs or the prior.

Edited finite payoffs are supported for pure PBE. Both types must be possible:
the model requires `0 < prior < 1` (the UI offers 0.001–0.999). Zero-probability
types, mixed-strategy equilibria, arbitrary signal/type sets, and other
microeconomics models are not implemented. Finding no pure PBE does not imply
that no mixed equilibrium exists.

## Run verification

```bash
python -m pytest -q
```

Tests check the exact homework equilibria and belief ranges, profitable
deviations, indifference, refinement gains, edited games, degenerate receiver
preferences, invalid inputs and the interactive Streamlit flows. A seeded
set of 50 edited games checks interval membership against direct expected
payoff comparisons at 21 beliefs, as well as equilibrium incentive checks.
This is useful coverage, not a claim to have tested every possible payoff.

Future modules can reuse this separation between model data, mathematical
solver and interface. Version 0.1 deliberately contains only this signalling
game.

## Pink study interface and fixed-coordinate tree

The tree now places Chance centrally, type x above and type y below, L on
both left branches and R on both right branches. Vertical dotted information
sets always connect the two L nodes and the two R nodes. This arrangement is
based on the written description; matching the seminar screenshot is pending
receipt of that image.

Select **Separating**, **Pooling**, or **All cases** alongside the tree. Choose
both players' strategies to see pink branches and the resulting payoffs for
each possible type. Dashed pink action branches show the receiver's choices
at unreached nodes. **Reveal equilibrium branches** calculates a PBE for the
selected case and colours its reached paths mint. The equilibrium selector
lets you explore the other supported profiles. Manual strategy changes or
payoff edits clear the revealed status; the solver verifies it again.

`styling.py` holds the Helvetica font stack, pastel palette, rounded cards,
and a small inline SVG bunny, with no extra dependencies. `visualization.py`
contains the fixed coordinates and Plotly drawing, with no solver imports.
The UI passes the solver's confirmation to the renderer. Study mode scores
eight checks, gives encouraging feedback, and can show a brief sparkle
animation when all checks pass. **Celebration animations** is off by default
and honours the system's reduced-motion preference.

Verification now includes 31 automated tests, including diagram topology,
eight terminal branches, preserved information sets, off-path highlights,
case switching, automatic reveal and a fully correct study answer.
