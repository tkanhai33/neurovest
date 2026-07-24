#!/usr/bin/env python3

"""
Phase 135 blind contract discovery.

Discovers statically declared contracts without importing or executing code:

Python
- dataclasses
- Pydantic models
- TypedDict declarations
- Protocol declarations
- abstract base classes and abstract methods
- enums
- named tuples
- function signatures
- FastAPI request and response model references
- safety, risk, gate, policy, and permission signals

TypeScript / JavaScript
- interfaces
- type aliases
- enums
- exported functions
- API route handler signatures
- DTO, schema, contract, policy, and safety naming signals

This stage discovers evidence only. It does not determine whether contracts are
correct, complete, compatible, enforced, or production-ready.
"""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scripts.phase135.utils.filesystem import safe_read_text


PYTHON_SUFFIXES = {".py"}
WEB_SUFFIXES = {".js", ".jsx", ".mjs", ".ts", ".tsx"}

ARCHIVE_MARKERS = {
    "archive",
    "archives",
    "architecture_backup",
    "backup",
    "backups",
    "deprecated",
    "legacy",
    "old",
    "quarantine",
    "quarantine_artifacts",
}

GENERATED_MARKERS = {
    ".next",
    "build",
    "coverage",
    "dist",
    "generated",
    "htmlcov",
    "node_modules",
    "output",
    "outputs",
    "reports",
    "runtime",
}

TOOLING_MARKERS = {
    "bin",
    "script",
    "scripts",
    "tool",
    "tools",
}

CONTRACT_NAME_MARKERS = {
    "contract",
    "dto",
    "interface",
    "message",
    "model",
    "payload",
    "policy",
    "protocol",
    "request",
    "response",
    "schema",
    "state",
    "type",
}

SAFETY_NAME_MARKERS = {
    "allow",
    "allowed",
    "authorization",
    "authorize",
    "block",
    "blocked",
    "deny",
    "denied",
    "emergency",
    "gate",
    "guard",
    "limit",
    "lock",
    "locked",
    "permission",
    "policy",
    "risk",
    "safe",
    "safety",
    "stop",
    "threshold",
    "validate",
    "validation",
}

PYDANTIC_BASES = {
    "BaseModel",
    "pydantic.BaseModel",
    "BaseSettings",
    "pydantic_settings.BaseSettings",
}

PROTOCOL_BASES = {
    "Protocol",
    "typing.Protocol",
    "typing_extensions.Protocol",
}

TYPED_DICT_BASES = {
    "TypedDict",
    "typing.TypedDict",
    "typing_extensions.TypedDict",
}

ABC_BASES = {
    "ABC",
    "abc.ABC",
}

ENUM_BASES = {
    "Enum",
    "enum.Enum",
    "IntEnum",
    "enum.IntEnum",
    "StrEnum",
    "enum.StrEnum",
}

NAMED_TUPLE_BASES = {
    "NamedTuple",
    "typing.NamedTuple",
}

ABSTRACT_DECORATORS = {
    "abstractmethod",
    "abc.abstractmethod",
}

DATACLASS_DECORATORS = {
    "dataclass",
    "dataclasses.dataclass",
}

FASTAPI_HTTP_METHODS = {
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "trace",
    "websocket",
}

TS_INTERFACE_PATTERN = re.compile(
    r"""
    (?P<export>\bexport\s+)?
    interface\s+
    (?P<name>[A-Za-z_$][A-Za-z0-9_$]*)
    (?:\s+extends\s+(?P<extends>[^{]+))?
    \s*\{
    """,
    re.MULTILINE | re.VERBOSE,
)

TS_TYPE_PATTERN = re.compile(
    r"""
    (?P<export>\bexport\s+)?
    type\s+
    (?P<name>[A-Za-z_$][A-Za-z0-9_$]*)
    (?:\s*<[^;=]+>)?
    \s*=
    """,
    re.MULTILINE | re.VERBOSE,
)

TS_ENUM_PATTERN = re.compile(
    r"""
    (?P<export>\bexport\s+)?
    (?:const\s+)?
    enum\s+
    (?P<name>[A-Za-z_$][A-Za-z0-9_$]*)
    \s*\{
    """,
    re.MULTILINE | re.VERBOSE,
)

TS_FUNCTION_PATTERN = re.compile(
    r"""
    (?P<export>\bexport\s+)?
    (?P<async>\basync\s+)?
    function\s+
    (?P<name>[A-Za-z_$][A-Za-z0-9_$]*)
    \s*
    (?P<generics><[^>]+>\s*)?
    \(
    (?P<parameters>[^)]*)
    \)
    \s*
    (?:
        :\s*(?P<return_type>[^{=\n]+)
    )?
    """,
    re.MULTILINE | re.VERBOSE,
)

TS_EXPORTED_CONST_FUNCTION_PATTERN = re.compile(
    r"""
    \bexport\s+const\s+
    (?P<name>[A-Za-z_$][A-Za-z0-9_$]*)
    \s*
    (?:
        :\s*(?P<declared_type>[^=\n]+)
    )?
    =
    \s*
    (?P<async>async\s+)?
    \(
    (?P<parameters>[^)]*)
    \)
    \s*
    (?:
        :\s*(?P<return_type>[^=]+?)
    )?
    =>
    """,
    re.MULTILINE | re.VERBOSE,
)

TS_ROUTE_HANDLER_PATTERN = re.compile(
    r"""
    \bexport\s+
    (?:
        async\s+function\s+
        |
        const\s+
    )
    (?P<method>GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)
    \b
    """,
    re.MULTILINE | re.VERBOSE,
)

PYTHON_CONTRACT_SUFFIXES = (
    "Contract",
    "DTO",
    "Dto",
    "Interface",
    "Message",
    "Payload",
    "Policy",
    "Protocol",
    "Request",
    "Response",
    "Schema",
    "State",
)


class ContractDiscovery:
    """
    Discover contract evidence across active and non-active source files.
    """

    def __init__(
        self,
        repository_root: Path,
        discovery: dict[str, Any],
        runtime_graph: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.discovery = discovery
        self.runtime_graph = runtime_graph

        self.files: list[dict[str, Any]] = list(
            discovery.get("files", [])
        )

        self.source_paths = {
            record["path"]
            for record in self.files
            if record.get("is_source")
        }

        self.runtime_routes = list(
            runtime_graph.get("routes", [])
        )

    def discover(self) -> dict[str, Any]:
        python = self._scan_python()
        web = self._scan_web()

        contracts = python["contracts"] + web["contracts"]
        functions = python["function_contracts"] + web["function_contracts"]
        route_contracts = self._build_route_contracts(
            python_routes=python["route_contracts"],
            web_routes=web["route_contracts"],
        )
        safety_signals = (
            python["safety_signals"]
            + web["safety_signals"]
        )
        parse_errors = (
            python["parse_errors"]
            + web["parse_errors"]
        )

        contract_kind_counts = Counter(
            item["contract_kind"]
            for item in contracts
        )

        language_counts = Counter(
            item["language"]
            for item in contracts
        )

        classification_counts = Counter(
            item["classification"]
            for item in contracts
        )

        active_contracts = [
            item
            for item in contracts
            if item["classification"] == "active"
        ]

        non_active_contracts = [
            item
            for item in contracts
            if item["classification"] != "active"
        ]

        contract_files = sorted(
            {
                item["source"]
                for item in contracts
            }
        )

        active_contract_files = sorted(
            {
                item["source"]
                for item in active_contracts
            }
        )

        safety_files = sorted(
            {
                item["source"]
                for item in safety_signals
            }
        )

        duplicate_names = self._discover_duplicate_contract_names(
            contracts
        )

        route_coverage = self._build_route_contract_coverage(
            route_contracts
        )

        return {
            "discovery_mode": "static_evidence_based",
            "application_executed": False,
            "architecture_assumed": False,
            "summary": {
                "contracts": len(contracts),
                "active_contracts": len(active_contracts),
                "non_active_contracts": len(non_active_contracts),
                "contract_files": len(contract_files),
                "active_contract_files": len(active_contract_files),
                "function_contracts": len(functions),
                "route_contracts": len(route_contracts),
                "safety_signals": len(safety_signals),
                "safety_files": len(safety_files),
                "duplicate_contract_names": len(duplicate_names),
                "parse_errors": len(parse_errors),
            },
            "contracts": sorted(
                contracts,
                key=lambda item: (
                    item["language"],
                    item["contract_kind"],
                    item["name"],
                    item["source"],
                ),
            ),
            "active_contracts": sorted(
                active_contracts,
                key=lambda item: (
                    item["contract_kind"],
                    item["name"],
                    item["source"],
                ),
            ),
            "non_active_contracts": sorted(
                non_active_contracts,
                key=lambda item: (
                    item["classification"],
                    item["contract_kind"],
                    item["name"],
                    item["source"],
                ),
            ),
            "function_contracts": sorted(
                functions,
                key=lambda item: (
                    item["language"],
                    item["source"],
                    item["name"],
                ),
            ),
            "route_contracts": sorted(
                route_contracts,
                key=lambda item: (
                    item["framework"],
                    item["path"],
                    item["method"],
                    item["source"],
                ),
            ),
            "safety_signals": sorted(
                safety_signals,
                key=lambda item: (
                    item["signal_type"],
                    item["source"],
                    item["name"],
                ),
            ),
            "duplicate_contract_names": duplicate_names,
            "route_contract_coverage": route_coverage,
            "contract_kind_counts": dict(
                sorted(
                    contract_kind_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "language_counts": dict(
                sorted(language_counts.items())
            ),
            "classification_counts": dict(
                sorted(classification_counts.items())
            ),
            "contract_files": contract_files,
            "active_contract_files": active_contract_files,
            "safety_files": safety_files,
            "python": python,
            "javascript_or_typescript": web,
            "parse_errors": sorted(
                parse_errors,
                key=lambda item: item["path"],
            ),
            "limitations": [
                (
                    "Contract discovery identifies declarations and annotations "
                    "but does not prove runtime validation or enforcement."
                ),
                (
                    "Regex-based TypeScript inspection may not fully understand "
                    "complex generic, conditional, mapped, or inferred types."
                ),
                (
                    "Safety-related names are evidence signals only and are not "
                    "proof of effective risk controls."
                ),
                (
                    "No intended NeuroVest ownership or architectural contract "
                    "has been assumed or enforced."
                ),
            ],
        }

    def _scan_python(self) -> dict[str, Any]:
        contracts: list[dict[str, Any]] = []
        function_contracts: list[dict[str, Any]] = []
        route_contracts: list[dict[str, Any]] = []
        safety_signals: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []

        for path_string in sorted(self.source_paths):
            if Path(path_string).suffix.lower() not in PYTHON_SUFFIXES:
                continue

            text = safe_read_text(
                self.repository_root / path_string,
                max_bytes=2_000_000,
            )

            if text is None:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            try:
                tree = ast.parse(text, filename=path_string)
            except SyntaxError as exc:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": (
                            f"SyntaxError line {exc.lineno}: {exc.msg}"
                        ),
                    }
                )
                continue

            classification = self._classify_path(path_string)
            aliases = self._build_alias_index(tree)

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    contract = self._python_class_contract(
                        node=node,
                        source=path_string,
                        classification=classification,
                        aliases=aliases,
                    )

                    if contract:
                        contracts.append(contract)

                    safety_signals.extend(
                        self._python_class_safety_signals(
                            node=node,
                            source=path_string,
                            classification=classification,
                        )
                    )

                elif isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    function_contracts.append(
                        self._python_function_contract(
                            node=node,
                            source=path_string,
                            classification=classification,
                            owner=None,
                        )
                    )

                    route_contract = self._python_route_contract(
                        node=node,
                        source=path_string,
                        classification=classification,
                    )

                    if route_contract:
                        route_contracts.append(route_contract)

                    safety_signal = self._name_safety_signal(
                        name=node.name,
                        source=path_string,
                        classification=classification,
                        language="python",
                        signal_type="function_name",
                        line=getattr(node, "lineno", None),
                    )

                    if safety_signal:
                        safety_signals.append(safety_signal)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            signal = self._name_safety_signal(
                                name=target.id,
                                source=path_string,
                                classification=classification,
                                language="python",
                                signal_type="assigned_name",
                                line=getattr(node, "lineno", None),
                            )

                            if signal:
                                safety_signals.append(signal)

                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        signal = self._name_safety_signal(
                            name=node.target.id,
                            source=path_string,
                            classification=classification,
                            language="python",
                            signal_type="annotated_name",
                            line=getattr(node, "lineno", None),
                        )

                        if signal:
                            safety_signals.append(signal)

        return {
            "contracts": self._deduplicate(
                contracts,
                ("source", "name", "contract_kind"),
            ),
            "function_contracts": self._deduplicate(
                function_contracts,
                ("source", "owner", "name", "line"),
            ),
            "route_contracts": self._deduplicate(
                route_contracts,
                ("source", "method", "path", "handler"),
            ),
            "safety_signals": self._deduplicate(
                safety_signals,
                ("source", "name", "signal_type", "line"),
            ),
            "parse_errors": parse_errors,
        }

    def _python_class_contract(
        self,
        node: ast.ClassDef,
        source: str,
        classification: str,
        aliases: dict[str, str],
    ) -> dict[str, Any] | None:
        bases = [
            self._canonical_name(
                self._expression_name(base),
                aliases,
            )
            for base in node.bases
        ]

        decorators = [
            self._canonical_name(
                self._decorator_name(decorator),
                aliases,
            )
            for decorator in node.decorator_list
        ]

        contract_kind = self._class_contract_kind(
            name=node.name,
            bases=bases,
            decorators=decorators,
        )

        if contract_kind is None:
            return None

        fields: list[dict[str, Any]] = []
        methods: list[dict[str, Any]] = []
        abstract_methods: list[str] = []

        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                field_name = (
                    child.target.id
                    if isinstance(child.target, ast.Name)
                    else self._expression_name(child.target)
                )

                fields.append(
                    {
                        "name": field_name,
                        "annotation": self._annotation(child.annotation),
                        "has_default": child.value is not None,
                    }
                )

            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        fields.append(
                            {
                                "name": target.id,
                                "annotation": None,
                                "has_default": True,
                            }
                        )

            elif isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                method_contract = self._python_function_contract(
                    node=child,
                    source=source,
                    classification=classification,
                    owner=node.name,
                )
                methods.append(method_contract)

                method_decorators = {
                    self._canonical_name(
                        self._decorator_name(decorator),
                        aliases,
                    )
                    for decorator in child.decorator_list
                }

                if method_decorators.intersection(
                    ABSTRACT_DECORATORS
                ):
                    abstract_methods.append(child.name)

        return {
            "language": "python",
            "source": source,
            "classification": classification,
            "name": node.name,
            "contract_kind": contract_kind,
            "bases": bases,
            "decorators": decorators,
            "field_count": len(fields),
            "fields": fields,
            "method_count": len(methods),
            "methods": methods,
            "abstract_methods": sorted(abstract_methods),
            "line": getattr(node, "lineno", None),
            "name_signal": self._contract_name_signal(node.name),
        }

    def _class_contract_kind(
        self,
        name: str,
        bases: list[str],
        decorators: list[str],
    ) -> str | None:
        base_set = set(bases)
        decorator_set = set(decorators)

        if decorator_set.intersection(DATACLASS_DECORATORS):
            return "dataclass"

        if base_set.intersection(PYDANTIC_BASES):
            return "pydantic_model"

        if base_set.intersection(PROTOCOL_BASES):
            return "protocol"

        if base_set.intersection(TYPED_DICT_BASES):
            return "typed_dict"

        if base_set.intersection(ENUM_BASES):
            return "enum"

        if base_set.intersection(NAMED_TUPLE_BASES):
            return "named_tuple"

        if base_set.intersection(ABC_BASES):
            return "abstract_base_class"

        if name.endswith(PYTHON_CONTRACT_SUFFIXES):
            return "name_inferred_contract"

        lowered = name.lower()

        if any(marker in lowered for marker in CONTRACT_NAME_MARKERS):
            return "name_inferred_contract"

        return None

    def _python_function_contract(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source: str,
        classification: str,
        owner: str | None,
    ) -> dict[str, Any]:
        parameters: list[dict[str, Any]] = []

        positional = list(node.args.posonlyargs) + list(node.args.args)
        positional_defaults = (
            [None] * (len(positional) - len(node.args.defaults))
            + list(node.args.defaults)
        )

        for argument, default in zip(
            positional,
            positional_defaults,
        ):
            parameters.append(
                {
                    "name": argument.arg,
                    "kind": "positional",
                    "annotation": self._annotation(argument.annotation),
                    "has_default": default is not None,
                }
            )

        if node.args.vararg:
            parameters.append(
                {
                    "name": node.args.vararg.arg,
                    "kind": "var_positional",
                    "annotation": self._annotation(
                        node.args.vararg.annotation
                    ),
                    "has_default": False,
                }
            )

        for argument, default in zip(
            node.args.kwonlyargs,
            node.args.kw_defaults,
        ):
            parameters.append(
                {
                    "name": argument.arg,
                    "kind": "keyword_only",
                    "annotation": self._annotation(argument.annotation),
                    "has_default": default is not None,
                }
            )

        if node.args.kwarg:
            parameters.append(
                {
                    "name": node.args.kwarg.arg,
                    "kind": "var_keyword",
                    "annotation": self._annotation(
                        node.args.kwarg.annotation
                    ),
                    "has_default": False,
                }
            )

        return {
            "language": "python",
            "source": source,
            "classification": classification,
            "owner": owner,
            "name": node.name,
            "async": isinstance(node, ast.AsyncFunctionDef),
            "parameters": parameters,
            "parameter_count": len(parameters),
            "return_annotation": self._annotation(node.returns),
            "line": getattr(node, "lineno", None),
        }

    def _python_route_contract(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        source: str,
        classification: str,
    ) -> dict[str, Any] | None:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            decorator_name = self._expression_name(
                decorator.func
            )
            method = decorator_name.rsplit(".", 1)[-1].lower()

            if method not in FASTAPI_HTTP_METHODS:
                continue

            path_value = (
                self._literal_value(decorator.args[0])
                if decorator.args
                else "<dynamic_or_missing>"
            )

            response_model = None

            for keyword in decorator.keywords:
                if keyword.arg == "response_model":
                    response_model = self._expression_name(
                        keyword.value
                    )

            function_contract = self._python_function_contract(
                node=node,
                source=source,
                classification=classification,
                owner=None,
            )

            request_models = sorted(
                {
                    parameter["annotation"]
                    for parameter in function_contract["parameters"]
                    if parameter["annotation"]
                    and parameter["annotation"]
                    not in {
                        "Request",
                        "fastapi.Request",
                        "WebSocket",
                        "fastapi.WebSocket",
                    }
                }
            )

            return {
                "framework": "FastAPI",
                "language": "python",
                "source": source,
                "classification": classification,
                "method": method.upper(),
                "path": (
                    path_value
                    if isinstance(path_value, str)
                    else repr(path_value)
                ),
                "handler": node.name,
                "request_models": request_models,
                "response_model": response_model,
                "return_annotation": function_contract[
                    "return_annotation"
                ],
                "line": getattr(node, "lineno", None),
            }

        return None

    def _python_class_safety_signals(
        self,
        node: ast.ClassDef,
        source: str,
        classification: str,
    ) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []

        class_signal = self._name_safety_signal(
            name=node.name,
            source=source,
            classification=classification,
            language="python",
            signal_type="class_name",
            line=getattr(node, "lineno", None),
        )

        if class_signal:
            signals.append(class_signal)

        for child in node.body:
            if isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                signal = self._name_safety_signal(
                    name=child.name,
                    source=source,
                    classification=classification,
                    language="python",
                    signal_type="method_name",
                    line=getattr(child, "lineno", None),
                )

                if signal:
                    signals.append(signal)

            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    signal = self._name_safety_signal(
                        name=child.target.id,
                        source=source,
                        classification=classification,
                        language="python",
                        signal_type="class_field",
                        line=getattr(child, "lineno", None),
                    )

                    if signal:
                        signals.append(signal)

        return signals

    def _scan_web(self) -> dict[str, Any]:
        contracts: list[dict[str, Any]] = []
        function_contracts: list[dict[str, Any]] = []
        route_contracts: list[dict[str, Any]] = []
        safety_signals: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []

        for path_string in sorted(self.source_paths):
            if Path(path_string).suffix.lower() not in WEB_SUFFIXES:
                continue

            text = safe_read_text(
                self.repository_root / path_string,
                max_bytes=2_000_000,
            )

            if text is None:
                parse_errors.append(
                    {
                        "path": path_string,
                        "error": "file_unreadable_or_too_large",
                    }
                )
                continue

            classification = self._classify_path(path_string)

            for match in TS_INTERFACE_PATTERN.finditer(text):
                name = match.group("name")

                contracts.append(
                    {
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "name": name,
                        "contract_kind": "typescript_interface",
                        "exported": bool(match.group("export")),
                        "extends": self._split_types(
                            match.group("extends")
                        ),
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                        "name_signal": self._contract_name_signal(name),
                    }
                )

                signal = self._name_safety_signal(
                    name=name,
                    source=path_string,
                    classification=classification,
                    language="javascript_or_typescript",
                    signal_type="interface_name",
                    line=self._line_number(text, match.start()),
                )

                if signal:
                    safety_signals.append(signal)

            for match in TS_TYPE_PATTERN.finditer(text):
                name = match.group("name")

                contracts.append(
                    {
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "name": name,
                        "contract_kind": "typescript_type_alias",
                        "exported": bool(match.group("export")),
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                        "name_signal": self._contract_name_signal(name),
                    }
                )

                signal = self._name_safety_signal(
                    name=name,
                    source=path_string,
                    classification=classification,
                    language="javascript_or_typescript",
                    signal_type="type_alias_name",
                    line=self._line_number(text, match.start()),
                )

                if signal:
                    safety_signals.append(signal)

            for match in TS_ENUM_PATTERN.finditer(text):
                name = match.group("name")

                contracts.append(
                    {
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "name": name,
                        "contract_kind": "typescript_enum",
                        "exported": bool(match.group("export")),
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                        "name_signal": self._contract_name_signal(name),
                    }
                )

            for match in TS_FUNCTION_PATTERN.finditer(text):
                function_contracts.append(
                    {
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "owner": None,
                        "name": match.group("name"),
                        "async": bool(match.group("async")),
                        "exported": bool(match.group("export")),
                        "parameters_text": (
                            match.group("parameters") or ""
                        ).strip(),
                        "return_annotation": (
                            match.group("return_type") or ""
                        ).strip() or None,
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                    }
                )

            for match in TS_EXPORTED_CONST_FUNCTION_PATTERN.finditer(text):
                function_contracts.append(
                    {
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "owner": None,
                        "name": match.group("name"),
                        "async": bool(match.group("async")),
                        "exported": True,
                        "parameters_text": (
                            match.group("parameters") or ""
                        ).strip(),
                        "declared_type": (
                            match.group("declared_type") or ""
                        ).strip() or None,
                        "return_annotation": (
                            match.group("return_type") or ""
                        ).strip() or None,
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                    }
                )

            for match in TS_ROUTE_HANDLER_PATTERN.finditer(text):
                route_contracts.append(
                    {
                        "framework": "Next.js",
                        "language": "javascript_or_typescript",
                        "source": path_string,
                        "classification": classification,
                        "method": match.group("method"),
                        "path": self._next_route_path(
                            Path(path_string)
                        ),
                        "handler": match.group("method"),
                        "request_models": [],
                        "response_model": None,
                        "return_annotation": None,
                        "line": self._line_number(
                            text,
                            match.start(),
                        ),
                    }
                )

            safety_signals.extend(
                self._web_text_safety_signals(
                    text=text,
                    source=path_string,
                    classification=classification,
                )
            )

        return {
            "contracts": self._deduplicate(
                contracts,
                ("source", "name", "contract_kind"),
            ),
            "function_contracts": self._deduplicate(
                function_contracts,
                ("source", "name", "line"),
            ),
            "route_contracts": self._deduplicate(
                route_contracts,
                ("source", "method", "path", "handler"),
            ),
            "safety_signals": self._deduplicate(
                safety_signals,
                ("source", "name", "signal_type", "line"),
            ),
            "parse_errors": parse_errors,
        }

    def _web_text_safety_signals(
        self,
        text: str,
        source: str,
        classification: str,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        identifier_pattern = re.compile(
            r"\b[A-Za-z_$][A-Za-z0-9_$]*\b"
        )

        seen: set[tuple[str, int]] = set()

        for match in identifier_pattern.finditer(text):
            name = match.group(0)
            lowered = name.lower()

            if not any(
                marker in lowered
                for marker in SAFETY_NAME_MARKERS
            ):
                continue

            line = self._line_number(text, match.start())
            key = (name, line)

            if key in seen:
                continue

            seen.add(key)

            results.append(
                {
                    "language": "javascript_or_typescript",
                    "source": source,
                    "classification": classification,
                    "name": name,
                    "signal_type": "identifier_name",
                    "matched_markers": sorted(
                        marker
                        for marker in SAFETY_NAME_MARKERS
                        if marker in lowered
                    ),
                    "line": line,
                }
            )

        return results

    def _build_route_contracts(
        self,
        python_routes: list[dict[str, Any]],
        web_routes: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        discovered = python_routes + web_routes

        indexed: dict[
            tuple[str, str, str],
            dict[str, Any],
        ] = {
            (
                item["source"],
                item["method"],
                item["path"],
            ): item
            for item in discovered
        }

        for route in self.runtime_routes:
            key = (
                route["source"],
                route["method"],
                route["path"],
            )

            if key not in indexed:
                indexed[key] = {
                    "framework": route["framework"],
                    "language": (
                        "python"
                        if route["framework"] == "FastAPI"
                        else "javascript_or_typescript"
                    ),
                    "source": route["source"],
                    "classification": route.get(
                        "classification",
                        self._classify_path(route["source"]),
                    ),
                    "method": route["method"],
                    "path": route["path"],
                    "handler": route.get("handler"),
                    "request_models": [],
                    "response_model": None,
                    "return_annotation": None,
                    "line": route.get("line"),
                }

        return list(indexed.values())

    @staticmethod
    def _build_route_contract_coverage(
        route_contracts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        with_request_model = []
        with_response_model = []
        with_return_annotation = []
        without_explicit_contract = []

        for route in route_contracts:
            request_models = route.get("request_models") or []
            response_model = route.get("response_model")
            return_annotation = route.get("return_annotation")

            if request_models:
                with_request_model.append(route)

            if response_model:
                with_response_model.append(route)

            if return_annotation:
                with_return_annotation.append(route)

            if not (
                request_models
                or response_model
                or return_annotation
            ):
                without_explicit_contract.append(route)

        total = len(route_contracts)

        return {
            "total_routes": total,
            "routes_with_request_models": len(with_request_model),
            "routes_with_response_models": len(with_response_model),
            "routes_with_return_annotations": len(
                with_return_annotation
            ),
            "routes_without_explicit_contract": len(
                without_explicit_contract
            ),
            "explicit_contract_coverage_percent": (
                round(
                    (
                        (
                            total
                            - len(without_explicit_contract)
                        )
                        / total
                    )
                    * 100,
                    2,
                )
                if total
                else 0.0
            ),
            "routes_without_explicit_contract_details": sorted(
                without_explicit_contract,
                key=lambda item: (
                    item["framework"],
                    item["path"],
                    item["method"],
                ),
            ),
        }

    @staticmethod
    def _discover_duplicate_contract_names(
        contracts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for contract in contracts:
            grouped[contract["name"]].append(contract)

        duplicates: list[dict[str, Any]] = []

        for name, items in sorted(grouped.items()):
            unique_sources = sorted(
                {
                    item["source"]
                    for item in items
                }
            )

            if len(unique_sources) < 2:
                continue

            duplicates.append(
                {
                    "name": name,
                    "declaration_count": len(items),
                    "source_count": len(unique_sources),
                    "sources": unique_sources,
                    "kinds": sorted(
                        {
                            item["contract_kind"]
                            for item in items
                        }
                    ),
                    "languages": sorted(
                        {
                            item["language"]
                            for item in items
                        }
                    ),
                }
            )

        return duplicates

    @staticmethod
    def _name_safety_signal(
        name: str,
        source: str,
        classification: str,
        language: str,
        signal_type: str,
        line: int | None,
    ) -> dict[str, Any] | None:
        lowered = name.lower()

        matched = sorted(
            marker
            for marker in SAFETY_NAME_MARKERS
            if marker in lowered
        )

        if not matched:
            return None

        return {
            "language": language,
            "source": source,
            "classification": classification,
            "name": name,
            "signal_type": signal_type,
            "matched_markers": matched,
            "line": line,
        }

    @staticmethod
    def _contract_name_signal(name: str) -> list[str]:
        lowered = name.lower()

        return sorted(
            marker
            for marker in CONTRACT_NAME_MARKERS
            if marker in lowered
        )

    @staticmethod
    def _build_alias_index(
        tree: ast.AST,
    ) -> dict[str, str]:
        aliases: dict[str, str] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    local = (
                        alias.asname
                        or alias.name.split(".")[0]
                    )
                    aliases[local] = alias.name

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    local = alias.asname or alias.name
                    aliases[local] = (
                        f"{module}.{alias.name}"
                        if module
                        else alias.name
                    )

        return aliases

    @staticmethod
    def _canonical_name(
        name: str,
        aliases: dict[str, str],
    ) -> str:
        if not name:
            return ""

        root, separator, remainder = name.partition(".")
        canonical_root = aliases.get(root, root)

        if separator:
            return f"{canonical_root}.{remainder}"

        return canonical_root

    @staticmethod
    def _expression_name(node: ast.AST | None) -> str:
        if node is None:
            return ""

        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            parent = ContractDiscovery._expression_name(
                node.value
            )

            return (
                f"{parent}.{node.attr}"
                if parent
                else node.attr
            )

        if isinstance(node, ast.Subscript):
            return ContractDiscovery._expression_name(
                node.value
            )

        if isinstance(node, ast.Call):
            return ContractDiscovery._expression_name(
                node.func
            )

        return ast.dump(
            node,
            include_attributes=False,
        )[:300]

    @staticmethod
    def _decorator_name(node: ast.AST) -> str:
        if isinstance(node, ast.Call):
            return ContractDiscovery._expression_name(
                node.func
            )

        return ContractDiscovery._expression_name(node)

    @staticmethod
    def _annotation(node: ast.AST | None) -> str | None:
        if node is None:
            return None

        try:
            return ast.unparse(node)
        except Exception:
            return ast.dump(
                node,
                include_attributes=False,
            )[:500]

    @staticmethod
    def _literal_value(node: ast.AST) -> Any:
        try:
            return ast.literal_eval(node)
        except Exception:
            return ContractDiscovery._expression_name(node)

    @staticmethod
    def _split_types(value: str | None) -> list[str]:
        if not value:
            return []

        return sorted(
            part.strip()
            for part in value.split(",")
            if part.strip()
        )

    @staticmethod
    def _next_route_path(path: Path) -> str:
        try:
            relative = path.relative_to("frontend/app")
        except ValueError:
            return "/"

        visible_parts = []

        for part in relative.parent.parts:
            if part.startswith("(") and part.endswith(")"):
                continue

            if part.startswith("@"):
                continue

            visible_parts.append(part)

        return (
            "/" + "/".join(visible_parts)
            if visible_parts
            else "/"
        )

    @staticmethod
    def _line_number(
        text: str,
        character_offset: int,
    ) -> int:
        return text.count(
            "\n",
            0,
            character_offset,
        ) + 1

    @staticmethod
    def _deduplicate(
        records: list[dict[str, Any]],
        keys: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        unique: dict[
            tuple[str, ...],
            dict[str, Any],
        ] = {}

        for record in records:
            key = tuple(
                repr(record.get(field))
                for field in keys
            )
            unique[key] = record

        return list(unique.values())

    @staticmethod
    def _classify_path(path_string: str) -> str:
        path = Path(path_string)
        parts = {
            part.lower()
            for part in path.parts
        }
        lowered = path.name.lower()

        if parts.intersection(ARCHIVE_MARKERS):
            return "archive_or_quarantine"

        if parts.intersection(GENERATED_MARKERS):
            return "generated_or_output"

        if parts.intersection(TOOLING_MARKERS):
            return "tooling"

        if (
            lowered.endswith(".bak")
            or ".backup" in lowered
            or ".phase" in lowered
            or ".generated." in lowered
        ):
            return "generated_or_backup"

        return "active"
