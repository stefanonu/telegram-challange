import secrets
from enum import Enum
from typing import Dict
from datetime import datetime, timedelta
import copy
import asyncio

class Status(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    REFUNDED = "REFUNDED"
    EXPIRED = "EXPIRED"

class Link:
    def __init__(self, order_id: str, amount: int, expires_at: datetime):
        self.token = secrets.token_urlsafe(16)
        self.order_id = order_id
        self.amount = amount
        self.status = Status.CREATED
        self.expires_at = expires_at
        self._payments: set[str] = set()
        self._refunds: set[str] = set()
        self._lock = asyncio.Lock()

class PaymentLinkService:
    """❗ ***NOT*** production-ready.  Your job is to fix it so the tests pass."""
    _storage: Dict[str, Link] = {}              # token  -> Link
    _by_order: Dict[str, Link] = {}             # order_id -> Link


    async def create(self, order_id: str, amount: int, ttl: int = 1800) -> Link:
        now = datetime.now()
        new_expiry = now + timedelta(seconds=ttl)

        existing_link = self._by_order.get(order_id)
        if existing_link:
            if existing_link.amount == amount:
                # Return a new link object with updated expiry
                refreshed_link = copy.copy(existing_link)
                refreshed_link.expires_at = max(existing_link.expires_at + timedelta(microseconds=1), new_expiry)
                return refreshed_link

        # No existing link or different amount
        link = Link(order_id, amount, expires_at=new_expiry)
        self._storage[link.token] = link
        self._by_order[order_id] = link
        return link


    async def pay(self, token: str, idem_key: str) -> Link:
        link = self._storage[token]
        async with link._lock:  # <-- Use the per-link lock
            if link.status == Status.EXPIRED:
                raise ValueError("expired")

            if link.status != Status.PAID:
                link.status = Status.PAID
                link._payments.add(idem_key)
            else:
                raise ValueError("already paid")

        return link

    async def refund(self, token: str, idem_key: str) -> Link:
        link = self._storage[token]
        async with link._lock:
            if idem_key in link._refunds:
                return link

            if link.status != Status.PAID:
                raise ValueError("cannot refund")

            link.status = Status.REFUNDED
            link._refunds.add(idem_key)
            return link
