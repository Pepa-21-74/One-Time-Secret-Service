from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import SecretsOrm

class Secret_key_repository:
    @classmethod
    async def reveal_secret_record(
        cls,
        session: AsyncSession,
        secret_id: str,
    ) -> str | None:
        
        query = select(SecretsOrm).filter_by(
            secret_id=secret_id,
            is_viewed=False,
        ).with_for_update()

        result = await session.execute(query)
        record = result.scalar_one_or_none()

        if record is None:
            return None
        
        update_viewed_status_stmt = update(SecretsOrm).filter_by(
            secret_id=secret_id,
        ).values(is_viewed=True)
        await session.execute(update_viewed_status_stmt)

        await session.commit()
        return record.secret_data

    @classmethod
    async def add_secret_record(
        cls,
        session: AsyncSession,
        secret_data: str,
        hashed_password: str | None,
        secret_id: str
    ) -> str:

        record = SecretsOrm(
            secret_data=secret_data,
            hashed_password=hashed_password,
            is_viewed=False,
            secret_id=secret_id
        )
        session.add(record)
        await session.commit()
        return record.secret_id
    
    @classmethod
    async def get_secret_password(
            cls,
            session: AsyncSession,
            secret_id: str,
        ) -> SecretsOrm | None:
            
            query = select(SecretsOrm).filter_by(
                secret_id=secret_id,
                is_viewed=False,
            ).with_for_update()
    
            result = await session.execute(query)
            record = result.scalar_one_or_none()
    
            if record is None:
                return None
            
            return record
    