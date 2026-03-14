"""Quick script to reset all users (for development only).

WARNING: This will DELETE ALL USERS from the database!
Only use this in development when you need to start fresh.

Usage:
    python reset_users.py
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select, delete

sys.path.insert(0, 'backend')

from src.models.user import User
from src.config import settings


async def reset_users():
    """Delete all users from the database."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Count existing users
        result = await session.execute(select(User))
        users = result.scalars().all()
        user_count = len(users)

        if user_count == 0:
            print("No users found in database.")
            return

        print(f"Found {user_count} users in database:")
        for user in users:
            print(f"  - {user.email} (ID: {user.id})")
        print()

        # Confirm deletion
        confirm = input(f"⚠️  DELETE ALL {user_count} USERS? Type 'yes' to confirm: ").strip().lower()

        if confirm == 'yes':
            # Delete all users
            await session.execute(delete(User))
            await session.commit()
            print(f"✓ Deleted {user_count} users")
            print("✓ Database reset complete")
            print()
            print("Next steps:")
            print("1. Register a new user via POST /auth/register")
            print("2. Login with the new user via POST /auth/login")
        else:
            print("✗ Cancelled - no users deleted")


if __name__ == "__main__":
    print("=" * 60)
    print("User Reset Script (Development Only)")
    print("=" * 60)
    print()

    try:
        asyncio.run(reset_users())
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
