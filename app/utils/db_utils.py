from motor.core import AgnosticCollection
from pyrogram.types.user_and_chats import User


def extract_user_data(user: User) -> dict:
    return dict(
        name=f"""{user.first_name or ""} {user.last_name or ""}""",
        username=user.username,
        mention=user.mention,
    )


async def add_data(collection: AgnosticCollection, id: str | int, data: dict) -> None:
    found = await collection.find_one({"_id": id})
    if not found:
        await collection.insert_one({"_id": id, **data})
    else:
        await collection.update_one({"_id": id}, {"$set": data})


async def delete_data(collection: AgnosticCollection, id: int) -> bool | None:
    found = await collection.find_one({"_id": id})
    if found:
        await collection.delete_one({"_id": id})
        return True
