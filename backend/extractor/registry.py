"""
Extraction Registry.

Manages extractor registration, dependency resolution, and execution ordering.
ExtractionService must NEVER instantiate extractors directly - use this registry.
"""

import time
from collections import defaultdict
from typing import Any, Optional

from backend.core.domain.extraction import (
    ExtractionOptions,
    ExtractorCapability,
    ExtractorContext,
)
from backend.core.interfaces.extractor import (
    IExtractor,
    IExtractionRegistry,
    IRuleProvider,
)
from backend.extractor.exceptions import (
    DependencyCycleError,
    ExtractorNotFoundError,
    ExtractorRegistrationError,
    RegistryError,
)


class ExtractionRegistry(IExtractionRegistry):
    """Registry for managing extractors with dependency resolution."""

    def __init__(self, rule_provider: Optional[IRuleProvider] = None):
        """
        Initialize extraction registry.

        Args:
            rule_provider: Optional rule provider for extractors
        """
        self._extractors: dict[str, IExtractor] = {}
        self._capabilities: dict[str, ExtractorCapability] = {}
        self._rule_provider = rule_provider

    def register_extractor(self, extractor: IExtractor) -> None:
        """
        Register an extractor.

        Args:
            extractor: Extractor instance to register

        Raises:
            ExtractorRegistrationError: If registration fails
        """
        extractor_name = extractor.get_name()

        # Check if already registered
        if extractor_name in self._extractors:
            raise ExtractorRegistrationError(extractor_name, "Extractor already registered")

        # Validate extractor
        try:
            self._validate_extractor(extractor)
        except Exception as e:
            raise ExtractorRegistrationError(extractor_name, str(e)) from e

        # Register extractor
        self._extractors[extractor_name] = extractor

        # Store capability
        self._capabilities[extractor_name] = extractor.get_capability()

    def unregister_extractor(self, extractor_name: str) -> None:
        """
        Unregister an extractor.

        Args:
            extractor_name: Name of the extractor to unregister
        """
        if extractor_name in self._extractors:
            del self._extractors[extractor_name]

        if extractor_name in self._capabilities:
            del self._capabilities[extractor_name]

    def get_extractor(self, extractor_name: str) -> Optional[IExtractor]:
        """
        Get an extractor by name.

        Args:
            extractor_name: Name of the extractor

        Returns:
            Extractor instance or None if not found
        """
        return self._extractors.get(extractor_name)

    def get_all_extractors(self) -> dict[str, IExtractor]:
        """
        Get all registered extractors.

        Returns:
            Dictionary of extractor name to extractor instance
        """
        return self._extractors.copy()

    def get_enabled_extractors(self, options: ExtractionOptions) -> list[IExtractor]:
        """
        Get all enabled extractors.

        Args:
            options: Extraction options

        Returns:
            List of enabled extractors in execution order
        """
        execution_order = self.get_execution_order()
        enabled_extractors = []

        for extractor_name in execution_order:
            extractor = self._extractors.get(extractor_name)
            if extractor and extractor.is_enabled(options):
                enabled_extractors.append(extractor)

        return enabled_extractors

    def get_extractor_capabilities(self) -> dict[str, ExtractorCapability]:
        """
        Get capabilities of all registered extractors.

        Returns:
            Dictionary of extractor name to capability
        """
        return self._capabilities.copy()

    def validate_dependencies(self) -> list[str]:
        """
        Validate all extractor dependencies.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for missing dependencies
        for extractor_name, extractor in self._extractors.items():
            dependencies = extractor.get_dependencies()
            for dep_name in dependencies:
                if dep_name not in self._extractors:
                    errors.append(
                        f"Extractor '{extractor_name}' depends on '{dep_name}' "
                        f"which is not registered"
                    )

        # Check for circular dependencies
        try:
            self.get_execution_order()
        except DependencyCycleError as e:
            errors.append(str(e))

        return errors

    def get_execution_order(self) -> list[str]:
        """
        Get the execution order based on dependencies.

        Returns:
            List of extractor names in execution order

        Raises:
            DependencyCycleError: If circular dependencies are detected
        """
        # Build dependency graph
        graph: dict[str, set[str]] = defaultdict(set)
        in_degree: dict[str, int] = {}

        # Initialize graph
        for extractor_name in self._extractors:
            graph[extractor_name] = set()
            in_degree[extractor_name] = 0

        # Add edges
        for extractor_name, extractor in self._extractors.items():
            dependencies = extractor.get_dependencies()
            for dep_name in dependencies:
                if dep_name in self._extractors:
                    graph[dep_name].add(extractor_name)
                    in_degree[extractor_name] = in_degree.get(extractor_name, 0) + 1

        # Topological sort (Kahn's algorithm)
        queue: list[str] = [name for name, degree in in_degree.items() if degree == 0]
        execution_order: list[str] = []

        while queue:
            # Sort by priority (higher priority first)
            queue.sort(key=lambda x: self._extractors[x].get_priority(), reverse=True)

            # Process extractor
            current = queue.pop(0)
            execution_order.append(current)

            # Update in-degree for dependents
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(execution_order) != len(self._extractors):
            # Find cycle
            remaining = set(self._extractors.keys()) - set(execution_order)
            cycle = self._find_cycle(remaining)
            raise DependencyCycleError(cycle)

        return execution_order

    def get_extractor_statistics(self) -> dict[str, Any]:
        """
        Get statistics about registered extractors.

        Returns:
            Dictionary of statistics
        """
        stats = {
            "total_extractors": len(self._extractors),
            "extractor_names": list(self._extractors.keys()),
            "dependency_graph": {},
            "execution_order": self.get_execution_order(),
        }

        # Build dependency graph for statistics
        for extractor_name, extractor in self._extractors.items():
            stats["dependency_graph"][extractor_name] = {
                "dependencies": extractor.get_dependencies(),
                "priority": extractor.get_priority(),
                "capability": {
                    "supported_types": [
                        t.value for t in extractor.get_capability().supported_types
                    ],
                    "deterministic": extractor.get_capability().deterministic,
                },
            }

        return stats

    def find_extractors_by_capability(self, entity_type: str) -> list[str]:
        """
        Find extractors that can extract a specific entity type.

        Args:
            entity_type: Entity type to search for

        Returns:
            List of extractor names
        """
        capable_extractors = []

        for extractor_name, capability in self._capabilities.items():
            supported_types = [t.value for t in capability.supported_types]
            if entity_type in supported_types:
                capable_extractors.append(extractor_name)

        return capable_extractors

    def has_dependency_cycle(self) -> bool:
        """
        Check if there are any dependency cycles.

        Returns:
            True if cycles exist, False otherwise
        """
        try:
            self.get_execution_order()
            return False
        except DependencyCycleError:
            return True

    def _validate_extractor(self, extractor: IExtractor) -> None:
        """
        Validate an extractor before registration.

        Args:
            extractor: Extractor to validate

        Raises:
            ExtractorRegistrationError: If validation fails
        """
        # Check required methods
        required_methods = [
            "get_name",
            "get_version",
            "get_capability",
            "can_extract",
            "extract",
            "is_enabled",
            "get_dependencies",
            "get_priority",
        ]

        for method in required_methods:
            if not hasattr(extractor, method):
                raise ExtractorRegistrationError(
                    extractor.get_name(), f"Missing required method: {method}"
                )

        # Validate capability
        capability = extractor.get_capability()
        if not capability.name:
            raise ExtractorRegistrationError(
                extractor.get_name(), "Capability name cannot be empty"
            )

        # Validate priority
        priority = extractor.get_priority()
        if not isinstance(priority, int) or priority < 0:
            raise ExtractorRegistrationError(
                extractor.get_name(), "Priority must be a non-negative integer"
            )

        # Validate dependencies
        dependencies = extractor.get_dependencies()
        for dep in dependencies:
            if not isinstance(dep, str):
                raise ExtractorRegistrationError(
                    extractor.get_name(), f"Invalid dependency name: {dep}"
                )

    def _find_cycle(self, remaining: set[str]) -> list[str]:
        """
        Find a cycle in the dependency graph.

        Args:
            remaining: Set of extractor names not in execution order

        Returns:
            List of extractor names forming the cycle
        """
        # Build subgraph for remaining extractors
        subgraph: dict[str, list[str]] = defaultdict(list)

        for extractor_name in remaining:
            extractor = self._extractors[extractor_name]
            dependencies = extractor.get_dependencies()
            for dep in dependencies:
                if dep in remaining:
                    subgraph[extractor_name].append(dep)

        # DFS to find cycle
        visited: set[str] = set()
        path: list[str] = []
        cycle: list[str] = []

        def dfs(node: str) -> bool:
            nonlocal cycle

            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                return True

            if node in visited:
                return False

            visited.add(node)
            path.append(node)

            for neighbor in subgraph.get(node, []):
                if dfs(neighbor):
                    return True

            path.pop()
            return False

        for node in remaining:
            if dfs(node):
                break

        return cycle if cycle else list(remaining)
