from Config import OWNER_ID, SUDOERS

async def get_clone_owner(bot_id: int):
    # yaha apna logic likho
    return 7548614955  # example owner id
    
async def is_owner(bot_id, user_id):
    owner_id = await get_clone_owner(bot_id)
    if owner_id == user_id or user_id == OWNER_ID or user_id in SUDOERS:
        return True
    return False
  
