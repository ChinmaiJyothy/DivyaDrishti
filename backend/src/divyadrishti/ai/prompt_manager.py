"""Prompt Manager for external AI prompt templates."""

import re
from pathlib import Path

from typing import Any

from jinja2 import Template, UndefinedError

from divyadrishti.ai.models import PromptTemplate


class PromptManager:
    """Load, version, validate, and render Jinja2 prompt templates from a directory."""

    def __init__(self, prompt_dir: Path | str) -> None:
        self.prompt_dir = Path(prompt_dir)
        self._templates: dict[str, PromptTemplate] = {}
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load prompt manifest if present."""
        manifest_path = self.prompt_dir / "manifest.json"
        if manifest_path.exists():
            import json

            return json.loads(manifest_path.read_text(encoding="utf-8"))
        return {}

    def load(self, name: str) -> PromptTemplate:
        """Load a prompt template by name."""
        if name in self._templates:
            return self._templates[name]

        file_path = self.prompt_dir / f"{name}.md"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        template, variables = self._extract_template(content)
        version = self._manifest.get(name, {}).get("version", "1.0")

        prompt = PromptTemplate(name=name, version=version, template=template, variables=variables)
        self._templates[name] = prompt
        return prompt

    def render(self, name: str, variables: dict[str, Any], validate: bool = False) -> str:
        """Render a prompt template with variables."""
        if validate:
            self.validate(name, variables)
        prompt = self.load(name)
        return Template(prompt.template).render(**variables)

    def validate(self, name: str, variables: dict[str, Any]) -> None:
        """Ensure all required variables are provided."""
        prompt = self.load(name)
        missing = [v for v in prompt.variables if v not in variables]
        if missing:
            raise ValueError(f"Missing prompt variables for {name}: {missing}")

    def _extract_template(self, content: str) -> tuple[str, list[str]]:
        """Extract the template block and variable list from a prompt file."""
        template = self._extract_code_block(content) or content
        variables = self._extract_variables(content)
        return template, variables

    def _extract_code_block(self, content: str) -> str | None:
        """Extract the first code block under ## Template."""
        match = re.search(r"## Template\s*\n```(?:text)?\n(.*?)```", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_variables(self, content: str) -> list[str]:
        """Extract variable names from the ## Variables section."""
        match = re.search(r"## Variables\s*\n((?:- .+\n?)+)", content)
        if not match:
            return self._extract_jinja_variables(content)

        variables = []
        for line in match.group(1).strip().splitlines():
            line = line.strip()
            if line.startswith("-"):
                var = line.lstrip("-").strip().strip("`")
                variables.append(var)
        return variables

    def _extract_jinja_variables(self, template: str) -> list[str]:
        """Fallback: extract {{ variable }} references from the template."""
        return sorted({name.strip() for name in re.findall(r"\{\{\s*(\w+)\s*\}\}", template)})
