from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import select

from app.infrastructure.database import SessionLocal
from app.models.approval import ApprovalGrant
from app.models.plan import Plan, PlanStep
from app.services.health_monitor import utc_now_iso
from app.services.planner import get_public_step_id


class ApprovalService:
    def __init__(self, health_monitor) -> None:
        self._health_monitor = health_monitor

    async def issue_grant(self, plan_id: str, approved_step_ids: list[str]) -> ApprovalGrant:
        if not approved_step_ids:
            raise ValueError("Chon it nhat mot buoc")

        with SessionLocal() as session:
            plan = session.get(Plan, plan_id)
            if plan is None:
                raise ValueError("plan not found")
            steps = session.scalars(
                select(PlanStep).where(
                    PlanStep.plan_id == plan_id,
                    PlanStep.plan_version == plan.version,
                )
            ).all()
            indexed = {get_public_step_id(step.step_id): step for step in steps}
            selected = [indexed[step_id] for step_id in approved_step_ids if step_id in indexed]
            if not selected:
                raise ValueError("Chon it nhat mot buoc")

            write_steps = [step for step in selected if step.read_or_write == "WRITE"]
            if write_steps and not self._health_monitor.is_write_allowed():
                raise PermissionError("Account not HEALTHY — write actions blocked")

            grant = ApprovalGrant(
                grant_id=f"grant-{uuid4().hex[:10]}",
                plan_id=plan_id,
                plan_version=plan.version,
                approved_step_ids=json.dumps([get_public_step_id(step.step_id) for step in selected]),
                approver_id="local_user",
                invalidated=False,
            )
            session.add(grant)
            session.commit()
            session.refresh(grant)
            session.expunge(grant)
            return grant

    async def invalidate_grants_for_plan(self, plan_id: str, reason: str) -> None:
        with SessionLocal() as session:
            grants = session.scalars(
                select(ApprovalGrant).where(
                    ApprovalGrant.plan_id == plan_id,
                    ApprovalGrant.invalidated.is_(False),
                )
            ).all()
            for grant in grants:
                grant.invalidated = True
                grant.invalidated_at = utc_now_iso()
                grant.invalidated_reason = reason
                session.add(grant)
            session.commit()
