
import asyncio
import logging
from sqlalchemy import delete
from app.core.db import engine, AsyncSessionLocal
from app.models.all_models import User, Persona, Conversation, Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_database():
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting database cleanup...")
            
            # Delete in order of dependencies (child first)
            
            # 1. Messages (depends on Conversation)
            logger.info("Deleting Messages...")
            await db.execute(delete(Message))
            
            # 2. Conversations (depends on User, Persona)
            logger.info("Deleting Conversations...")
            await db.execute(delete(Conversation))
            
            # 3. Personas (depends on User)
            logger.info("Deleting Personas...")
            await db.execute(delete(Persona))
            
            # 4. Users
            logger.info("Deleting Users...")
            await db.execute(delete(User))
            
            await db.commit()
            logger.info("Database cleared successfully!")
            
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    # Ensure we can import app modules
    import sys
    import os
    sys.path.append(os.getcwd())
    
    asyncio.run(clear_database())
