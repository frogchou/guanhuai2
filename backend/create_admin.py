import asyncio
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.all_models import User
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        new_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin")
        )
        db.add(new_user)
        await db.commit()
        print("Admin user created successfully. Username: admin, Password: admin")

if __name__ == "__main__":
    asyncio.run(create_admin())
