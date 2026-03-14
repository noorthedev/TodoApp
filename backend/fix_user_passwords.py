"""Script to fix unhashed passwords in the database.

This script checks all users and rehashes any passwords that are not bcrypt hashes.
Run this if you have users created before the security implementation was complete.

Usage:
    python fix_user_passwords.py
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

# Add src to path
sys.path.insert(0, 'backend')

from src.models.user import User
from src.config import settings
from src.utils.security import hash_password


async def fix_passwords():
    """Check and fix unhashed passwords in the database."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Fetch all users
        result = await session.execute(select(User))
        users = result.scalars().all()

        print(f"Found {len(users)} users in database")
        print("-" * 60)

        fixed_count = 0
        already_hashed_count = 0

        for user in users:
            # Check if password is already a bcrypt hash
            is_bcrypt = user.hashed_password.startswith('$2b$') if user.hashed_password else False

            if is_bcrypt:
                print(f"✓ User {user.email} - Password already hashed (bcrypt)")
                already_hashed_count += 1
            else:
                print(f"✗ User {user.email} - Password NOT hashed")
                print(f"  Current value: {user.hashed_password[:30]}...")

                # Ask for confirmation before rehashing
                print(f"  ⚠️  WARNING: Cannot recover original password!")
                print(f"  Options:")
                print(f"    1. Delete this user (they must re-register)")
                print(f"    2. Set a new password for this user")
                print(f"    3. Skip this user")

                choice = input(f"  Choose option (1/2/3): ").strip()

                if choice == "1":
                    await session.delete(user)
                    print(f"  → User {user.email} deleted")
                    fixed_count += 1
                elif choice == "2":
                    new_password = input(f"  Enter new password for {user.email}: ").strip()
                    if new_password:
                        user.hashed_password = hash_password(new_password)
                        print(f"  → Password updated for {user.email}")
                        fixed_count += 1
                    else:
                        print(f"  → Skipped (empty password)")
                else:
                    print(f"  → Skipped")

                print()

        # Commit changes
        if fixed_count > 0:
            await session.commit()
            print("-" * 60)
            print(f"✓ Fixed {fixed_count} users")
            print(f"✓ {already_hashed_count} users already had hashed passwords")
        else:
            print("-" * 60)
            print(f"✓ All {already_hashed_count} users already have hashed passwords")
            print("No changes needed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Password Hash Fix Script")
    print("=" * 60)
    print()

    try:
        asyncio.run(fix_passwords())
        print()
        print("✓ Script completed successfully")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
