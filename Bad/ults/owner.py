from Config import OWNER_ID, SUDOERS


    
async def is_owner(bot_id, user_id):
    owner_id = await get_clone_owner(bot_id)
    if owner_id == user_id or user_id == OWNER_ID or user_id in SUDOERS:
        return True
    return False
  
