"""Run with: python -m streamlit run app.py"""

from fractions import Fraction

import streamlit as st

from explanations import (failure_reasons, interval_text, number, receiver_label,
                          receiver_working, sender_label)
from models import ACTIONS, KEYS, SIGNALS, Game, homework_game
from solver import (assess, bayes_belief, best_responses, enumerate_candidates,
                    intuitive_criterion, optimal_beliefs, receiver_payoffs)
from visualization import game_tree

from styling import CSS, MASCOT

st.set_page_config(page_title="MicroLab · Signalling", page_icon="🌸", layout="wide")
st.markdown(CSS + MASCOT, unsafe_allow_html=True)

if "game" not in st.session_state:
    st.session_state.game = homework_game()
    st.session_state.editor_version = 0
game = st.session_state.game

st.markdown('<div class="eyebrow">MICROLAB / YOUR LITTLE ECONOMICS LAB ♡</div>', unsafe_allow_html=True)
st.title("A little signal. A little clarity.")
st.write("An interactive signalling lab for Advanced Microeconomics · Seminar 3, Question 1")
st.caption("Pure strategies only · Payoffs are (Player 1, Player 2) · bₛ = P(x | signal s)")
animations = st.toggle("Celebration animations", value=False, key="animations")
if game != homework_game():
    st.info("You are exploring an edited game. Pure-strategy PBE calculations are active; the Intuitive Criterion is supported only for the original homework.")

tree_tab, solver_tab, study_tab, experiment_tab = st.tabs(
    ["01  Game tree", "02  Equilibrium solver", "03  Study mode", "04  Experiment"])

SENDERS = (("L", "R"), ("R", "L"), ("L", "L"), ("R", "R"))
def clear_reveal():
    st.session_state.pop("revealed_profile", None)


def change_case():
    case = st.session_state.tree_case
    selected = st.session_state.get("tree_sender", SENDERS[0])
    if case == "Separating" and selected[0] == selected[1]:
        st.session_state.tree_sender = SENDERS[0]
    elif case == "Pooling" and selected[0] != selected[1]:
        st.session_state.tree_sender = SENDERS[2]
    clear_reveal()


with tree_tab:
    st.subheader("The signalling garden 🌷")
    st.caption("Chance chooses the private type. Player 1 sends a signal; Player 2 sees the signal, never the type.")
    diagram, controls = st.columns([2.5, 1], gap="large")
    with controls, st.container(border=True, key="strategy_card"):
        case = st.radio("Explore a case", ("All cases", "Separating", "Pooling"),
                        key="tree_case", on_change=change_case)
        senders = [s for s in SENDERS if case == "All cases" or
                   (s[0] != s[1]) == (case == "Separating")]
        selected_sender = st.selectbox("Player 1's strategy", senders, format_func=sender_label,
                                      key="tree_sender", on_change=clear_reveal)
        after_l = st.radio("Player 2 after L", ACTIONS, horizontal=True, key="tree_l", on_change=clear_reveal)
        after_r = st.radio("Player 2 after R", ACTIONS, horizontal=True, key="tree_r", on_change=clear_reveal)
        equilibria = [c for c in enumerate_candidates(game) if c.is_pbe and c.sender in senders]
        def highlight(index=0):
            c = equilibria[index]
            st.session_state.tree_sender = c.sender
            st.session_state.tree_l, st.session_state.tree_r = c.receiver
            st.session_state.revealed_profile = (c.sender, c.receiver)
        st.button("Reveal equilibrium branches", on_click=highlight, disabled=not equilibria,
                  type="primary", width="stretch")
        if not equilibria:
            st.caption("No pure-strategy PBE exists in this case for the current game.")
        if st.session_state.get("revealed_profile") or st.session_state.get("solution_mode"):
            if equilibria:
                choice = st.selectbox("Explore a calculated PBE", range(len(equilibria)),
                    format_func=lambda i: sender_label(equilibria[i].sender) + " · " + receiver_label(equilibria[i].receiver))
                st.button("Highlight this equilibrium", on_click=highlight, args=(choice,))
        st.markdown("**Resulting terminal payoffs**")
        responses = dict(zip(SIGNALS, (after_l, after_r)))
        for kind, signal in zip(("x", "y"), selected_sender):
            action = responses[signal]
            pair = game.payoffs[kind, signal, action]
            st.write(f"{kind} → {signal} → {action}: **({number(pair[0])}, {number(pair[1])})**")
    candidate = assess(game, selected_sender, (after_l, after_r))
    confirmed = (candidate.is_pbe and st.session_state.get("revealed_profile") ==
                 (selected_sender, (after_l, after_r)))
    with diagram, st.container(border=True, key="diagram_card"):
        st.plotly_chart(game_tree(game, selected_sender, (after_l, after_r), confirmed=confirmed),
                        width="stretch", config={"displayModeBar": False})
        st.caption("Pink: selected branches · Mint: revealed equilibrium paths · Lavender: alternatives. "
                   "Dashed pink: Player 2's selected action at an unreached node. Purple dotted lines: information sets.")
    if confirmed:
        st.success("🌸 Equilibrium revealed! Both types' incentives and the receiver's best responses hold.")
        for signal in SIGNALS:
            st.write(f"Beliefs after {signal}: **{interval_text(candidate.beliefs[signal], 'b_'+signal)}**")
    with st.expander("How to read the diagram"):
        st.write("Start at Chance in the centre. Follow x upwards or y downwards, then L left or R right. "
                 "At each Player 2 node, u leads to the upper terminal and d to the lower terminal. "
                 "The two L nodes share one information set; the two R nodes share another. "
                 "A receiver action applies at both nodes in its information set, including off-path nodes. "
                 "Terminal pairs always list Player 1's payoff first.")


def show_candidate(c, index):
    tag = "PBE" if c.is_pbe else "Not a PBE"
    with st.expander(f"{tag} · {sender_label(c.sender)} · {receiver_label(c.receiver)}"):
        st.markdown("**1. Proposed strategies**")
        st.write(f"Player 1: {sender_label(c.sender)}. Player 2: {receiver_label(c.receiver)}.")
        st.markdown("**2–3. Beliefs and Player 2's best responses**")
        for signal, action in zip(SIGNALS, c.receiver):
            posterior = c.posteriors[signal]
            if posterior is None:
                st.write(f"After {signal}: off path. Bayes' rule does not pin down b_{signal}; initially 0 ≤ b_{signal} ≤ 1.")
            else:
                px = game.prior if c.sender[0] == signal else Fraction(0)
                py = 1-game.prior if c.sender[1] == signal else Fraction(0)
                st.write(f"After {signal}: Bayes' rule gives b_{signal} = {number(px)} / ({number(px)} + {number(py)}) = {number(posterior)}.")
            for line in receiver_working(game, signal, posterior):
                st.code(line, language=None)
            for a in ACTIONS:
                st.write(f"{a} is a best response when {interval_text(optimal_beliefs(game, signal, a), 'b_'+signal)}.")
            st.write(f"For the proposed action {action}, admissible Bayes-consistent beliefs: **{interval_text(c.beliefs[signal], 'b_'+signal)}**.")
        st.markdown("**4. Player 1's incentive constraints**")
        for i, signal in zip(c.incentives, c.sender):
            other = "R" if signal == "L" else "L"
            st.write(f"Type {i.kind}: stay with {signal} → {number(i.stay)}; deviate to {other} → {number(i.deviate)}. "
                     f"{number(i.stay)} ≥ {number(i.deviate)} is {'true ✓' if i.passes else 'false ✗'}.")
        st.caption("When a sender deviates, Player 2 follows the same strategy. Beliefs and responses are not recomputed as if the deviation had been announced.")
        st.markdown("**5–6. Verdict**")
        if c.is_pbe:
            st.success("PBE: receiver optimality, Bayes consistency and both sender incentive constraints hold for the stated beliefs.")
        else:
            for reason in failure_reasons(c):
                st.error(reason)


with solver_tab:
    st.subheader("Test every candidate")
    st.write("A PBE combines strategies and beliefs. A complete pure receiver strategy specifies what to do after both signals, including an unexpected one.")
    buttons = st.columns(4)
    for col, mode, label in zip(buttons, ("separating", "pooling", "criterion", "complete"),
                                ("Solve separating equilibria", "Solve pooling equilibria", "Apply Intuitive Criterion", "Show complete solution")):
        if col.button(label, width="stretch"):
            st.session_state.solution_mode = mode
    mode = st.session_state.get("solution_mode")
    if mode is None:
        st.info("Solutions are hidden. Choose a calculation above, or try Study mode first.")
    else:
        candidates = enumerate_candidates(game)
        visible = [c for c in candidates if mode not in ("separating", "pooling") or c.separating == (mode == "separating")]
        winners = [c for c in visible if c.is_pbe]
        st.write(f"**{len(winners)} pure strategy profiles supported as PBE** among {len(visible)} checked. Each off-path interval describes a family of beliefs, not a single equilibrium belief.")
        if winners:
            st.table([{"Sender": sender_label(c.sender), "Receiver": receiver_label(c.receiver),
                       "Beliefs after L": interval_text(c.beliefs['L'], 'b_L'),
                       "Beliefs after R": interval_text(c.beliefs['R'], 'b_R')} for c in winners])
        if mode in ("criterion", "complete"):
            st.markdown("### Intuitive Criterion")
            if game != homework_game():
                st.warning("Not supported for edited games in v0.1. Reset the original game to use the tested refinement proof.")
            for c in winners if game == homework_game() else []:
                result = intuitive_criterion(game, c)
                st.write(f"**{sender_label(c.sender)} · {receiver_label(c.receiver)}: {'survives' if result.survives else 'not established'}**")
                st.write(result.explanation)
                for signal, gains in result.gains.items():
                    for kind, gain in gains.items():
                        st.write(f"Type {kind}, deviation to {signal}: max over u,d of deviation payoff − equilibrium payoff = {number(gain)}.")
                if result.gains:
                    st.caption("A mixed receiver response cannot do better for a type than its best pure response. These bounds therefore also cover mixed responses to a deviation.")
        st.markdown("### Step-by-step checks")
        st.caption("Expand any profile, including failures. Sender indifference is allowed; only a strict improvement breaks an incentive constraint.")
        for index, candidate in enumerate(visible):
            show_candidate(candidate, index)
        if st.button("Hide solutions"):
            del st.session_state.solution_mode
            st.rerun()

with study_tab:
    st.subheader("Reason it through yourself")
    st.write("Choose a candidate, calculate one receiver decision, then check both sender types. Feedback stays hidden until you submit.")
    study_progress = st.progress(0, text="Your next little milestone: check all 8 parts of your reasoning ♡")
    with st.form("study"):
        sender = st.selectbox("1. Propose Player 1's strategy", SENDERS, format_func=sender_label)
        classification = st.radio("What kind of strategy is it?", ("Separating", "Pooling"), horizontal=True)
        c1, c2 = st.columns(2)
        rl = c1.selectbox("2. Response after L", ACTIONS)
        rr = c2.selectbox("Response after R", ACTIONS)
        signal = st.radio("3. Which information set will you calculate?", SIGNALS, horizontal=True)
        st.caption("Enter a proposed belief P(x | your chosen signal). On path, use Bayes' rule. Off path, you may propose any belief in [0,1], then check the response.")
        belief_input = st.text_input("Your belief (decimal or fraction)", "1/2")
        eu_u = st.text_input("Your expected payoff to Player 2 from u", "0")
        eu_d = st.text_input("Your expected payoff to Player 2 from d", "0")
        dx = st.checkbox("4. Type x strictly wants to deviate")
        dy = st.checkbox("Type y strictly wants to deviate")
        verdict = st.radio("Can this strategy profile be supported as a PBE for some valid beliefs?", ("Yes", "No"), horizontal=True)
        submitted = st.form_submit_button("Check my reasoning", type="primary")
    with st.expander("A hint, without the solution"):
        st.write("At a reached signal, divide the probability mass of x sending it by the total probability of that signal. Compute Player 2's payoff as b × payoff if x + (1−b) × payoff if y. For each sender type, compare staying with switching signals, holding Player 2's strategy fixed.")
    if submitted:
        try:
            belief, answer_u, answer_d = map(Fraction, (belief_input, eu_u, eu_d))
            if not 0 <= belief <= 1:
                raise ValueError("A belief must lie between 0 and 1.")
        except (ValueError, ZeroDivisionError):
            st.error("Use finite numbers or fractions such as 1/2; the belief must be between 0 and 1.")
        else:
            candidate = assess(game, sender, (rl, rr))
            posterior = bayes_belief(game, sender, signal)
            expected = receiver_payoffs(game, signal, belief)
            chosen_action = rl if signal == "L" else rr
            checks = [
                (classification == ("Separating" if candidate.separating else "Pooling"), "Strategy classification"),
                (posterior is None or posterior == belief, "Belief is Bayes-consistent"),
                (abs(answer_u-expected['u']) <= Fraction(1, 10000), "Expected payoff from u at your proposed belief"),
                (abs(answer_d-expected['d']) <= Fraction(1, 10000), "Expected payoff from d at your proposed belief"),
                (dx == (not candidate.incentives[0].passes), "Type x's deviation decision"),
                (dy == (not candidate.incentives[1].passes), "Type y's deviation decision"),
                ((verdict == "Yes") == candidate.is_pbe, "PBE verdict"),
            ]
            checks.append((chosen_action in best_responses(game, signal, belief), "Receiver response at your belief"))
            score = sum(passed for passed, _ in checks)
            study_progress.progress(score / len(checks), text=f"{score} of {len(checks)} checks correct ♡")
            if score == len(checks):
                st.success("🌸 Beautiful reasoning — you solved this equilibrium!" if candidate.is_pbe else
                           "🌸 Beautiful reasoning — you correctly ruled out this candidate!")
                if animations:
                    st.markdown('<div class="sparkles" aria-label="Celebration">✧ ♡ ✧ 🌸 ✧ ♡ ✧</div>', unsafe_allow_html=True)
            for passed, label in checks:
                (st.success if passed else st.error)(f"{'🌷 Nice work:' if passed else 'Try again: 🌱'} {label}")
            st.write(f"At your belief {number(belief)}, EU₂(u) = {number(expected['u'])}, EU₂(d) = {number(expected['d'])}. Best responses: {', '.join(best_responses(game, signal, belief))}.")
            if chosen_action not in best_responses(game, signal, belief):
                st.warning("Your receiver action is not optimal at your proposed belief, even if another belief could support this profile.")
            st.caption("Expected payoff answers allow rounding within 0.0001. Beliefs and solver comparisons use exact fractions.")
            show_candidate(candidate, "study")

with experiment_tab:
    st.subheader("Change one assumption")
    st.write("Edit any of the eight payoff pairs or Nature's prior, then apply your changes. The solver and tree will use the new game.")
    st.caption("Both types must have positive probability (0 < P(x) < 1). Mixed-strategy equilibria and refinement of edited games are outside v0.1.")
    def reset_game():
        st.session_state.game = homework_game()
        st.session_state.editor_version += 1
        st.session_state.pop("solution_mode", None)
        clear_reveal()
    st.button("Reset original homework", on_click=reset_game)
    version = st.session_state.editor_version
    with st.form(f"edit_game_{version}"):
        prior = st.number_input("Nature: P(type x)", min_value=0.001, max_value=0.999,
                                value=float(game.prior), step=0.01, format="%.3f")
        rows = [{"Type": t, "Signal": s, "Action": a,
                 "Player 1": float(game.payoff(t, s, a)), "Player 2": float(game.payoff(t, s, a, 1))}
                for t, s, a in KEYS]
        edited = st.data_editor(rows, key=f"payoffs_{version}", hide_index=True, disabled=["Type", "Signal", "Action"],
                                num_rows="fixed", width="stretch",
                                column_config={p: st.column_config.NumberColumn(p, required=True) for p in ("Player 1", "Player 2")})
        applied = st.form_submit_button("Apply changes", type="primary")
    if applied:
        try:
            new_game = Game(prior, {(r["Type"], r["Signal"], r["Action"]): (r["Player 1"], r["Player 2"]) for r in edited})
        except (ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
            st.error(f"Please supply a finite numeric payoff in every cell. {error}")
        else:
            st.session_state.game = new_game
            st.session_state.editor_version += 1
            st.session_state.pop("solution_mode", None)
            clear_reveal()
            st.rerun()
    st.caption("Edits live in this browser session. Reset restores all original values. Reloading a new session starts with the homework game.")

st.divider()
st.caption("♡ MicroLab · Small steps, clear incentives. Your economics study companion.")
