from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class ChatAnswerRoute(str, Enum):

    STRATEGY_LIBRARY_LIST = "strategy_library_list"
    STRATEGY_LIBRARY_COUNT = "strategy_library_count"
    STRATEGY_LIBRARY_IDENTITY = "strategy_library_identity"

    DEVELOPER_REPOSITORY = "developer_repository"

    GENERAL_FINANCE = "general_finance"
    PORTFOLIO_ACCOUNT = "portfolio_account"

    GENERAL_CHAT = "general_chat"


@dataclass(frozen=True)
class ChatRouteContract:

    route: ChatAnswerRoute

    retrieval_allowed: bool

    strategy_truth_allowed: bool

    repository_context_allowed: bool

    deterministic_answer: bool

    developer_model_preferred: bool

    finance_model_preferred: bool


_SSRN_PATTERN = re.compile(
    r"\bSSRN_3247865_\d{3}\b",
    re.IGNORECASE,
)


def classify_chat_route(
    query: str,
) -> ChatRouteContract:

    text = str(
        query or ""
    ).strip()

    lowered = text.lower()

    explicit_research_request = bool(
        re.search(
            r"\b(?:research|investigate|look up|"
            r"find (?:sources?|papers?|evidence)|"
            r"scientific papers?|academic papers?|"
            r"cite (?:the )?sources?|with citations?)\b",
            lowered,
        )
    )

    if not lowered:

        return ChatRouteContract(
            route=ChatAnswerRoute.GENERAL_CHAT,
            retrieval_allowed=False,
            strategy_truth_allowed=False,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=False,
            finance_model_preferred=False,
        )

    has_strategy = (
        "strateg"
        in lowered
    )

    has_lifecycle = (
        "lifecycle"
        in lowered
    )

    has_repeated = (
        "repeated"
        in lowered
        or "candidate-specific"
        in lowered
        or "small-set"
        in lowered
    )

    listing = any(
        token in lowered
        for token in (
            "list",
            "which",
            "what are",
            "show",
            "give me",
            "ids and names",
            "id and name",
        )
    )

    count_intent = any(
        token in lowered
        for token in (
            "how many",
            "count",
            "number of",
        )
    )

    explicit_ssrn = (
        _SSRN_PATTERN.search(
            text
        )
        is not None
    )

    developer_terms = (
        "jwt",
        "token refresh",
        "refresh token",
        "logout",
        "authentication",
        "authorization",
        "backend",
        "frontend",
        "fastapi",
        "typescript",
        "python",
        "repository",
        "repo",
        "route.ts",
        "endpoint",
        "api route",
        "database",
        "postgres",
        "session cookie",
        "csrf",
        "source code",
        "function",
        "class ",
        "stack trace",
        "exception",
    )

    portfolio_terms = (
        "my portfolio",
        "my positions",
        "my holdings",
        "account balance",
        "allocation",
        "snaptrade",
        "broker account",
    )

    neurovest_terms = (
        "neurovest",
        "authoritative strategy",
        "strategy library",
        "research library",
        "lifecycle evidence",
        "structured model lineage",
    )

    if (
        has_strategy
        and has_lifecycle
        and has_repeated
        and listing
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.STRATEGY_LIBRARY_LIST,
            retrieval_allowed=True,
            strategy_truth_allowed=True,
            repository_context_allowed=False,
            deterministic_answer=True,
            developer_model_preferred=False,
            finance_model_preferred=False,
        )

    if (
        has_strategy
        and has_lifecycle
        and has_repeated
        and count_intent
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.STRATEGY_LIBRARY_COUNT,
            retrieval_allowed=True,
            strategy_truth_allowed=True,
            repository_context_allowed=False,
            deterministic_answer=True,
            developer_model_preferred=False,
            finance_model_preferred=False,
        )

    # V36-R3R7 — preserve mixed-domain requests before the
    # strategy identity shortcut.

    mixed_request_markers = (
        " then ",
        " also ",
        " distinguish",
        " compare",
        " separate",
        " while ",
        "general finance",
        "general concept",
        "keeping the strategy",
        "keep the strategy",
    )

    padded_lowered = (
        " "
        + lowered
        + " "
    )

    mixed_request = any(
        marker in padded_lowered
        for marker in mixed_request_markers
    )

    mixed_developer_terms = (
        "python",
        "async",
        "await",
        "code",
        "coding",
        "typescript",
        "javascript",
        "fastapi",
    )

    mixed_finance_terms = (
        "mean reversion",
        "momentum",
        "diversification",
        "diversified",
        "expected return",
        "finance concept",
        "market concept",
    )

    if (
        explicit_ssrn
        and mixed_request
        and any(
            token in lowered
            for token in mixed_developer_terms
        )
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.DEVELOPER_REPOSITORY,
            retrieval_allowed=True,
            strategy_truth_allowed=True,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=True,
            finance_model_preferred=False,
        )

    if (
        explicit_ssrn
        and mixed_request
        and any(
            token in lowered
            for token in mixed_finance_terms
        )
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.GENERAL_FINANCE,
            retrieval_allowed=True,
            strategy_truth_allowed=True,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=False,
            finance_model_preferred=True,
        )

    if (
        explicit_ssrn
        or (
            has_strategy
            and any(
                token in lowered
                for token in neurovest_terms
            )
        )
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.STRATEGY_LIBRARY_IDENTITY,
            retrieval_allowed=True,
            strategy_truth_allowed=True,
            repository_context_allowed=False,
            deterministic_answer=True,
            developer_model_preferred=False,
            finance_model_preferred=False,
        )

    # NEUROVEST_GENERAL_CODING_ISOLATION_V1
    # General programming education does not request repository evidence.
    # Repository-specific requests retain their existing governed path.
    generic_code_education = (
        lowered.startswith((
            "explain ",
            "what is ",
            "what are ",
            "how does ",
            "how do ",
            "teach me ",
        ))
        and any(
            term in lowered
            for term in (
                "python",
                "javascript",
                "typescript",
                "sql",
                "async function",
                "programming",
            )
        )
        and not any(
            term in lowered
            for term in (
                "neurovest",
                "our repository",
                "my repository",
                "the repository",
                "our codebase",
                "my codebase",
                "the codebase",
                "our backend",
                "our frontend",
                "inspect the repo",
                "inspect the code",
                "source file",
                "source code in",
            )
        )
    )

    if generic_code_education:
        return ChatRouteContract(
            route=ChatAnswerRoute.GENERAL_CHAT,
            retrieval_allowed=False,
            strategy_truth_allowed=False,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=True,
            finance_model_preferred=False,
        )

    if any(
        token in lowered
        for token in developer_terms
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.DEVELOPER_REPOSITORY,
            retrieval_allowed=True,
            strategy_truth_allowed=False,
            repository_context_allowed=True,
            deterministic_answer=False,
            developer_model_preferred=True,
            finance_model_preferred=False,
        )

    if any(
        token in lowered
        for token in portfolio_terms
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.PORTFOLIO_ACCOUNT,
            retrieval_allowed=False,
            strategy_truth_allowed=False,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=False,
            finance_model_preferred=True,
        )

    research_grounded_finance_terms = (
        "fama-french",
        "fama french",
        "fama–french",
        "fama—french",
        "three-factor model",
        "three factor model",
        "factor investing",
        "diversification",
        "concentration risk",
        "value investing",
        "growth investing",
        "momentum investing",
        "systematic risk",
        "company-specific risk",
        "market-wide risk",
        "asset allocation",
        "backtesting",
        "strategy evaluation",
    )

    if any(
        token in lowered
        for token in research_grounded_finance_terms
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.GENERAL_FINANCE,
            retrieval_allowed=True,
            strategy_truth_allowed=False,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=False,
            finance_model_preferred=True,
        )

    general_finance_terms = (
        "momentum",
        "mean reversion",
        "arbitrage",
        "etf",
        "stock",
        "bond",
        "finance",
        "investing",
        "market",
        "risk parity",
        "portfolio theory",
        "diversification",
        "diversified",
        "expected return",
        "expected returns",
        "idiosyncratic risk",
        "concentration risk",
    )

    if any(
        token in lowered
        for token in general_finance_terms
    ):

        return ChatRouteContract(
            route=ChatAnswerRoute.GENERAL_FINANCE,
            retrieval_allowed=explicit_research_request,
            strategy_truth_allowed=False,
            repository_context_allowed=False,
            deterministic_answer=False,
            developer_model_preferred=False,
            finance_model_preferred=True,
        )

    return ChatRouteContract(
        route=ChatAnswerRoute.GENERAL_CHAT,
        retrieval_allowed=explicit_research_request,
        strategy_truth_allowed=False,
        repository_context_allowed=False,
        deterministic_answer=False,
        developer_model_preferred=False,
        finance_model_preferred=False,
    )


__all__ = [
    "ChatAnswerRoute",
    "ChatRouteContract",
    "classify_chat_route",
]
