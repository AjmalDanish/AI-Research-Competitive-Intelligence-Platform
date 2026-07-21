"""
Rule Loader.

Responsible for loading, validating, and versioning extraction rules.
Never hardcode extraction rules - load from YAML configuration files.
"""

import os
import re
from pathlib import Path
from typing import Any, Optional

import yaml

from backend.core.interfaces.extractor import IRuleLoader
from backend.extractor.exceptions import RuleLoadError, RuleValidationError


class RuleLoader(IRuleLoader):
    """Load and validate extraction rules from YAML files."""

    def __init__(self, rules_directory: Optional[str] = None):
        """
        Initialize rule loader.

        Args:
            rules_directory: Directory containing rule files (default: config/rules)
        """
        if rules_directory is None:
            # Default to config/rules relative to project root
            self.rules_directory = str(Path(__file__).parent.parent.parent / "config" / "rules")
        else:
            self.rules_directory = rules_directory

        # Cache for loaded rules
        self._rule_cache: dict[str, dict[str, Any]] = {}

        # Ensure rules directory exists
        Path(self.rules_directory).mkdir(parents=True, exist_ok=True)

    def get_rules_directory(self) -> str:
        """Get the directory containing rule files."""
        return self.rules_directory

    def load_rules(self, extractor_name: str) -> dict[str, Any]:
        """
        Load rules for an extractor.

        Args:
            extractor_name: Name of the extractor (e.g., "email", "phone")

        Returns:
            Dictionary of rules

        Raises:
            RuleLoadError: If rules cannot be loaded
        """
        # Check cache first
        if extractor_name in self._rule_cache:
            return self._rule_cache[extractor_name]

        # Determine rule file path
        rule_file = self._get_rule_file_path(extractor_name)

        if not os.path.exists(rule_file):
            # Return empty rules if file doesn't exist
            self._rule_cache[extractor_name] = self._get_default_rules(extractor_name)
            return self._rule_cache[extractor_name]

        try:
            with open(rule_file, "r", encoding="utf-8") as f:
                rules = yaml.safe_load(f)

            if rules is None:
                rules = self._get_default_rules(extractor_name)

            # Validate rules
            if not self.validate_rules(rules):
                raise RuleValidationError(
                    f"Rules for '{extractor_name}' failed validation", extractor_name
                )

            # Cache rules
            self._rule_cache[extractor_name] = rules
            return rules

        except yaml.YAMLError as e:
            raise RuleLoadError(f"Failed to parse YAML file '{rule_file}': {e}", rule_file) from e
        except Exception as e:
            raise RuleLoadError(f"Failed to load rules from '{rule_file}': {e}", rule_file) from e

    def validate_rules(self, rules: dict[str, Any]) -> bool:
        """
        Validate rule structure.

        Args:
            rules: Rules to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(rules, dict):
            return False

        # Check required fields
        required_fields = ["version", "rules"]
        for field in required_fields:
            if field not in rules:
                return False

        # Validate version
        if not isinstance(rules["version"], str):
            return False

        # Validate rules
        if not isinstance(rules["rules"], dict):
            return False

        # Validate each rule
        for rule_name, rule_config in rules["rules"].items():
            if not self._validate_single_rule(rule_name, rule_config):
                return False

        return True

    def get_rule_schema(self) -> dict[str, Any]:
        """
        Get the expected rule schema.

        Returns:
            Schema definition
        """
        return {
            "type": "object",
            "required": ["version", "rules"],
            "properties": {
                "version": {"type": "string", "description": "Rule version"},
                "rules": {
                    "type": "object",
                    "description": "Dictionary of rules",
                    "additionalProperties": {
                        "type": "object",
                        "required": ["pattern", "confidence"],
                        "properties": {
                            "pattern": {"type": "string", "description": "Regex pattern"},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "evidence_kind": {"type": "string"},
                            "confidence_source": {"type": "string"},
                            "metadata": {"type": "object"},
                            "enabled": {"type": "boolean"},
                        },
                    },
                },
                "metadata": {"type": "object", "description": "Additional metadata"},
            },
        }

    def reload_rules(self, extractor_name: str) -> dict[str, Any]:
        """
        Reload rules from file (bypass cache).

        Args:
            extractor_name: Name of the extractor

        Returns:
            Dictionary of rules
        """
        # Clear cache for this extractor
        if extractor_name in self._rule_cache:
            del self._rule_cache[extractor_name]

        return self.load_rules(extractor_name)

    def get_rule_version(self, extractor_name: str) -> str:
        """
        Get the version of rules for an extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Version string
        """
        rules = self.load_rules(extractor_name)
        return rules.get("version", "1.0.0")

    def clear_cache(self) -> None:
        """Clear all cached rules."""
        self._rule_cache.clear()

    def _get_rule_file_path(self, extractor_name: str) -> str:
        """
        Get the file path for an extractor's rules.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Full path to the rule file
        """
        return os.path.join(self.rules_directory, f"{extractor_name}_rules.yaml")

    def _validate_single_rule(self, rule_name: str, rule_config: Any) -> bool:
        """
        Validate a single rule configuration.

        Args:
            rule_name: Name of the rule
            rule_config: Rule configuration

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(rule_config, dict):
            return False

        # Check required fields
        if "pattern" not in rule_config:
            return False

        # Validate pattern
        if not isinstance(rule_config["pattern"], str):
            return False

        # Test if pattern is valid regex
        try:
            re.compile(rule_config["pattern"])
        except re.error:
            return False

        # Validate confidence if present
        if "confidence" in rule_config:
            confidence = rule_config["confidence"]
            if not isinstance(confidence, (int, float)):
                return False
            if confidence < 0.0 or confidence > 1.0:
                return False

        return True

    def _get_default_rules(self, extractor_name: str) -> dict[str, Any]:
        """
        Get default rules for an extractor.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Default rule configuration
        """
        return {
            "version": "1.0.0",
            "extractor": extractor_name,
            "rules": {},
            "metadata": {
                "description": f"Default rules for {extractor_name} extractor",
                "created_at": "2026-07-20",
            },
        }
