"""Fixed seminar-style coordinates; no solver imports or automatic tree layout.

Chance is central, type x above and y below. Signals travel left/right;
vertical dotted information sets connect equal signals across the two types.
"""
import plotly.graph_objects as go
from explanations import number
from models import ACTIONS, SIGNALS, TYPES

FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif'
PINK, MINT, LAVENDER, INK = "#E85D9F", "#77BFA3", "#EBDCF8", "#503447"
CHANCE = (.5, .5)
TYPE_NODES = {"x": (.5, .79), "y": (.5, .21)}
RECEIVER_NODES = {(t, s): (.25 if s == "L" else .75, TYPE_NODES[t][1])
                  for t in TYPES for s in SIGNALS}


def game_tree(game, sender, receiver, *, confirmed=False):
    """Pink shows choices, mint a caller-confirmed PBE. Off-path choices stay visible."""
    fig = go.Figure()
    annotations = []
    responses = dict(zip(SIGNALS, receiver))
    active_color = MINT if confirmed else PINK

    def label(x, y, text, size=14, color=INK):
        annotations.append(dict(x=x, y=y, text=text, showarrow=False,
                                font=dict(size=size, color=color), bgcolor="white", borderpad=3))

    def edge(start, end, selected, name, reached=True):
        fig.add_trace(go.Scatter(x=[start[0], end[0]], y=[start[1], end[1]],
            mode="lines", name=name,
            line=dict(color=active_color if selected and reached else PINK if selected else LAVENDER,
                      width=4 if selected else 2, dash="dash" if selected and not reached else "solid"),
            hovertemplate=name + (" · off path" if not reached else "") + "<extra></extra>", showlegend=False))

    def node(position, name, color=INK):
        fig.add_trace(go.Scatter(x=[position[0]], y=[position[1]], mode="markers",
            name=name, marker=dict(size=12, color=color, line=dict(color="white", width=2)),
            hovertemplate=name+"<extra></extra>", showlegend=False))

    # Information sets are drawn first and never hidden or recoloured by selection.
    for signal, x in (("L", .25), ("R", .75)):
        fig.add_shape(type="line", x0=x, x1=x, y0=.21, y1=.79,
                      line=dict(color="#A78DBD", width=2.5, dash="dot"))
        label(x, .5, f"<b>Player 2</b><br>observes {signal}<br>type unknown", 12)
    node(CHANCE, "Chance")
    label(.5, .5, "<b>Chance</b>", 16)
    for kind, chosen in zip(TYPES, sender):
        position = TYPE_NODES[kind]
        edge(CHANCE, position, False, f"Chance → {kind}")
        probability = game.prior if kind == "x" else 1-game.prior
        label(.56, (position[1]+.5)/2, f"{kind}: {number(probability)}", 13)
        node(position, f"Player 1 · type {kind}")
        label(.5, position[1]+(.065 if kind == "x" else -.065), f"<b>Player 1 · {kind}</b>")
        for signal in SIGNALS:
            receiver_node = RECEIVER_NODES[kind, signal]
            reached = chosen == signal
            edge(position, receiver_node, reached, f"{kind} → {signal}")
            label((position[0]+receiver_node[0])/2, position[1]+.035, f"<b>{signal}</b>")
            node(receiver_node, f"Player 2 · {kind}/{signal}", "#A78DBD")
            for action in ACTIONS:
                terminal = (.065 if signal == "L" else .935,
                            position[1]+(.13 if action == "u" else -.13))
                selected = responses[signal] == action
                edge(receiver_node, terminal, selected, f"{kind}/{signal} → {action}", reached)
                label((receiver_node[0]+terminal[0])/2,
                      (receiver_node[1]+terminal[1])/2, action, 14)
                pair = game.payoffs[kind, signal, action]
                text = f"({number(pair[0])}, {number(pair[1])})"
                label(terminal[0], terminal[1], f"<b>{text}</b>" if reached and selected else text,
                      15, active_color if reached and selected else INK)
    fig.update_layout(height=600, margin=dict(l=12, r=12, t=12, b=12),
        paper_bgcolor="white", plot_bgcolor="white", annotations=annotations,
        xaxis=dict(range=[-.025, 1.025], visible=False, fixedrange=True),
        yaxis=dict(range=[-.01, 1.01], visible=False, fixedrange=True),
        font=dict(family=FONT, color=INK), dragmode=False)
    return fig
