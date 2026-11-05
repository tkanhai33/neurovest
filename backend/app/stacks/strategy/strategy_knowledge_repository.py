from __future__ import annotations
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast
from uuid import UUID
from sqlalchemy import select
from backend.app.stacks.db_model.strategy_knowledge import StrategyKnowledge
from sqlalchemy.ext.asyncio import AsyncSession

class StrategyKnowledgeRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, record_id: UUID) -> StrategyKnowledge | None:
        return await self._session.get(StrategyKnowledge, record_id)

    async def get_by_strategy_id_version(self, *, strategy_id: str, strategy_version: int) -> StrategyKnowledge | None:
        statement = select(StrategyKnowledge).where(StrategyKnowledge.strategy_id == strategy_id, StrategyKnowledge.strategy_version == strategy_version)
        return (await self._session.execute(statement)).scalar_one_or_none()

    async def get_by_fingerprint(self, fingerprint: str) -> StrategyKnowledge | None:
        statement = select(StrategyKnowledge).where(StrategyKnowledge.strategy_fingerprint == fingerprint)
        return (await self._session.execute(statement)).scalar_one_or_none()

    async def get_latest_version(self, strategy_id: str) -> StrategyKnowledge | None:
        statement = select(StrategyKnowledge).where(StrategyKnowledge.strategy_id == strategy_id).order_by(StrategyKnowledge.strategy_version.desc()).limit(1)
        return (await self._session.execute(statement)).scalar_one_or_none()

    async def list_versions(self, strategy_id: str) -> list[StrategyKnowledge]:
        statement = select(StrategyKnowledge).where(StrategyKnowledge.strategy_id == strategy_id).order_by(StrategyKnowledge.strategy_version.asc())
        return list((await self._session.execute(statement)).scalars())

    async def list_by_symbol(self, symbol: str) -> list[StrategyKnowledge]:
        statement = select(StrategyKnowledge).where(cast(StrategyKnowledge.symbols, JSONB).contains([symbol]))
        return list((await self._session.execute(statement)).scalars())

    async def insert_candidate(self, record: StrategyKnowledge) -> StrategyKnowledge:
        duplicate = await self.get_by_fingerprint(record.strategy_fingerprint)
        if duplicate is not None:
            return duplicate
        self._session.add(record)
        await self._session.flush()
        return record

    async def record_validation(self, *, record: StrategyKnowledge, validation_status: str, scorecard: dict, backtest_metrics: dict, forward_metrics: dict, risk_metrics: dict, acceptance_thresholds: dict, rejection_reasons: list) -> StrategyKnowledge:
        record.validation_status = validation_status
        record.scorecard = dict(scorecard)
        record.backtest_metrics = dict(backtest_metrics)
        record.forward_metrics = dict(forward_metrics)
        record.risk_metrics = dict(risk_metrics)
        record.acceptance_thresholds = dict(acceptance_thresholds)
        record.rejection_reasons = list(rejection_reasons)
        await self._session.flush()
        return record

    async def admit_strategy(self, *, record: StrategyKnowledge, admission_reason: str) -> StrategyKnowledge:
        if record.validation_status not in {'passed', 'qualified', 'accepted'}:
            raise ValueError('Strategy validation must pass before admission.')
        duplicate = await self.get_by_fingerprint(record.strategy_fingerprint)
        if duplicate is not None and duplicate.id != record.id:
            raise ValueError('Duplicate strategy fingerprint.')
        record.lifecycle_state = 'accepted'
        record.admission_decision = 'admit'
        record.admission_reason = admission_reason
        await self._session.flush()
        return record

    async def reject_strategy(self, *, record: StrategyKnowledge, reason: str) -> StrategyKnowledge:
        if not reason.strip():
            raise ValueError('Rejection reason is required.')
        record.lifecycle_state = 'rejected'
        record.admission_decision = 'reject'
        record.admission_reason = reason
        await self._session.flush()
        return record

    async def promote_challenger(self, record: StrategyKnowledge) -> StrategyKnowledge:
        if record.lifecycle_state not in {'accepted', 'challenger', 'champion'}:
            raise ValueError('Only admitted strategies can be promoted.')
        record.lifecycle_state = 'champion'
        record.promotion_status = 'promoted'
        await self._session.flush()
        return record

    async def retire_strategy(self, record: StrategyKnowledge) -> StrategyKnowledge:
        record.lifecycle_state = 'retired'
        record.promotion_status = 'retired'
        await self._session.flush()
        return record
