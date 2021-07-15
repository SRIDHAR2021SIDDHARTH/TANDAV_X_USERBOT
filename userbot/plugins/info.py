
"""Get Telegram Profile Picture and other information
Syntax: .info @username"""

import html

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location

from tandavbot.utils import admin_cmd, sudo_cmd, edit_or_reply


@bot.on(admin_cmd(pattern="info ?(.*)", outgoing=True))
@bot.on(sudo_cmd(pattern="info ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await event.edit(str(error_i_a))
        return False
    replied_user_profile_photos = await borg(
        GetUserPhotosRequest(
            user_id=replied_user.user.id, offset=42, max_id=0, limit=80
        )
    )
    replied_user_profile_photos_count = "NaN"
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError:
        pass
    user_id = replied_user.user.id
    first_name = html.escape(replied_user.user.first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.user.last_name
    last_name = (
        last_name.replace("\u2060", "") if last_name else ("Last Name not found")
    )
    user_bio = replied_user.about
    if user_bio is not None:
        user_bio = html.escape(replied_user.about)
    common_chats = replied_user.common_chats_count
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception as e:
        dc_id = "`Need a Profile Picture to check **this**`"
        str(e)
    caption = """<b>𝖤𝚇𝚃𝚁𝙰𝙲𝚃𝙴𝙳 𝚄𝚂𝙴𝚁 𝙸𝙽𝙵𝙾 𝙱𝚈 𝙳𝙴𝙰𝙳𝙻𝚈 𝙱𝙾𝚃<b>
<b>┏━━━━━━━━━━━━━━━━━━━━━<b>   
<b>┣ 𝚄𝚂𝙴𝚁 𝙸𝙳</b>: <code>{}</code>
<b>┣ 𝙻𝙸𝙽𝙺 𝚃𝙾 𝙿𝚁𝙾𝙵𝙸𝙻𝙴</b>: <a href='tg://user?id={}'>Click Here🚪</a>
<b>┣ 𝙵𝙸𝚁𝚂𝚃 𝙽𝙰𝙼𝙴</b>: <code>{}</code> 
<b>┣ 𝙻𝙰𝚂𝚃 𝙽𝙰𝙼𝙴</b>: <code>{}</code>
<b>┣ 𝙱𝙸𝙾</b>: {}
<b>┣ 𝙳𝙲 𝙸𝙳</b>: {}
<b>┣ 𝙽𝙾. 𝙾𝙵 𝙿𝚂𝚂</b> : {}
<b>┣ 𝚁𝙴𝚂𝚃𝚁𝙸𝙲𝚃𝙴𝙳</b>: {}
<b>┣ 𝚅𝙴𝚁𝙸𝙵𝙸𝙴𝙳</b>: {}
<b>┣ 𝙱𝙾𝚃</b>: {}
<b>┣ 𝙶𝚁𝙾𝚄𝙿𝚂 𝙸𝙽 𝙲𝙾𝙼𝙼𝙾𝙽</b>: {}
<b>┗━━━━━━━━━━━━━━━━━━━━━<b>
<b>⚡<a href='https://t.me/deadly_userbot'>𝙵𝚁𝙾𝙼 𝙳𝙰𝚃𝙰𝙱𝙰𝚂𝙴 𝙾𝙵 𝙳𝙴𝙰𝙳𝙻𝚈𝙱𝙾𝚃</a>⚡ </b>
""".format(                 
        user_id,
        user_id,
        first_name,
        last_name,
        user_bio,
        dc_id,
        replied_user_profile_photos_count,
        replied_user.user.restricted,
        replied_user.user.verified,
        replied_user.user.bot,
        common_chats,
    )
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = event.message.id
    await borg.send_message(
        event.chat_id,
        caption,
        reply_to=message_id_to_reply,
        parse_mode="HTML",
        file=replied_user.profile_photo,
        force_document=False,
        silent=True,
    )
    await event.delete()


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.forward.sender_id
                    or previous_message.forward.channel_id
                )
            )
            return replied_user, None
        else:
            replied_user = await event.client(
                GetFullUserRequest(previous_message.sender_id)
            )
            return replied_user, None
    else:
        input_str = None
        try:
            input_str = event.pattern_match.group(1)
        except IndexError as e:
            return None, e
        if event.message.entities is not None:
            mention_entity = event.message.entities
            probable_user_mention_entity = mention_entity[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            else:
                try:
                    user_object = await event.client.get_entity(input_str)
                    user_id = user_object.id
                    replied_user = await event.client(GetFullUserRequest(user_id))
                    return replied_user, None
                except Exception as e:
                    return None, e
        elif event.is_private:
            try:
                user_id = event.chat_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        else:
            try:
                user_object = await event.client.get_entity(int(input_str))
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
