from types import SimpleNamespace as M

from backend.app.stacks.chat_public.context.relevant_history_v101 import (
    select_relevant_history,
)


def msg(role, content):
    return M(role=role, content=content)


def test_old_project_recalled_after_unrelated_turns():
    history = [
        msg("user", "We chose Rust for our command-line project."),
        msg("assistant", "Rust is the chosen project language."),
    ]
    for i in range(20):
        history += [
            msg("user", f"Cooking question {i} about soup."),
            msg("assistant", f"Cooking answer {i}."),
        ]
    result = select_relevant_history(
        history,
        "Back to our project, which language did we choose?",
    )
    text = " ".join(m.content for m in result)
    assert "We chose Rust" in text
    assert "chosen project language" in text
    assert "Cooking question 19" in text


def test_correction_order_preserved():
    history = [
        msg("user", "Website design should be red."),
        msg("assistant", "Red is selected."),
        msg("user", "Actually website design should be blue."),
        msg("assistant", "Blue replaces red."),
    ]
    result = select_relevant_history(
        history, "What is our website design?"
    )
    assert [m.content for m in result] == [
        m.content for m in history
    ]


def test_other_topic_not_selected_from_old_history():
    history = [
        msg("user", "My private cooking instructions."),
        msg("assistant", "Recipe discussed."),
    ]
    history += [
        msg("user", "Programming project uses Rust."),
        msg("assistant", "We chose Rust."),
    ] * 12

    result = select_relevant_history(
        history,
        "Which programming project language?",
    )
    assert "My private cooking instructions." not in [
        m.content for m in result
    ]


def test_empty_and_budget_boundaries():
    assert select_relevant_history([], "Hello") == []
    history = [
        msg("user", "long " * 1000),
        msg("assistant", "Short answer."),
    ]
    result = select_relevant_history(
        history, "What happened?", character_budget=300
    )
    assert sum(len(m.content) + 20 for m in result) <= 300


def test_original_objects_not_rewritten():
    history = [
        msg("user", "The server uses PostgreSQL."),
        msg("assistant", "PostgreSQL was discussed."),
    ]
    result = select_relevant_history(
        history, "Which server database?"
    )
    assert all(any(x is original for original in history) for x in result)
