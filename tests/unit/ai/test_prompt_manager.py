import pytest
from pathlib import Path

from divyadrishti.ai import PromptManager


def test_prompt_manager_loads_system():
    pm = PromptManager(Path("prompts"))
    prompt = pm.load("system")
    assert "You are" in prompt.template


def test_prompt_manager_renders_with_variables():
    pm = PromptManager(Path("prompts"))
    text = pm.render(
        "system",
        {
            "user_name": "",
            "chart_summary": "",
            "reasoning_trace": "",
            "conversation_history": "",
            "user_question": "",
        },
        validate=True,
    )
    assert "You are" in text


def test_prompt_manager_validation_missing_variable():
    pm = PromptManager(Path("prompts"))
    with pytest.raises(ValueError):
        pm.render("system", {}, validate=True)
