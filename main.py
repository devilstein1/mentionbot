#STEIN @rejerk at telegram


import random
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import (
    UserStatusOnline,
    UserStatusRecently,
    ChannelParticipantsKicked,
    ChannelParticipantsSearch,
    ChatBannedRights
)
from telethon.tl.functions.channels import EditBannedRequest
from telethon.errors import MessageIdInvalidError, FloodWaitError
from datetime import datetime, timezone, timedelta

# fill these things
API_ID = int(input("Enter your API_ID: "))
API_HASH = input("Enter your API_HASH: ")
BOT_TOKEN = input("Enter your BOT_TOKEN: ")

OWNER_ID = int(input("Enter OWNER_ID: "))
ALLOWED_GROUP_ID = int(input("Enter ALLOWED_GROUP_ID: "))


EMOJIS = ["🔔", "🔥", "⚡", "🎯", "🚀", "👀", "💥", "📢"]

client = TelegramClient("mention_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

def allowed(event):
    return event.chat_id == ALLOWED_GROUP_ID and event.sender_id == OWNER_ID

def get_text(event):
    parts = event.raw_text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else "Hii"

def get_target(event):
    parts = event.raw_text.split(maxsplit=1)
    return parts[1] if len(parts) == 2 else None

async def safe_send(chat_id, text, reply_to):
    try:
        return await client.send_message(chat_id, text, parse_mode="html", reply_to=reply_to)
    except MessageIdInvalidError:
        return await client.send_message(chat_id, text, parse_mode="html")
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        return await client.send_message(chat_id, text, parse_mode="html")
    except Exception:
        return None

@client.on(events.NewMessage(pattern=r"^/mentionall"))
async def mention_all(event):
    if not allowed(event):
        return
    try:
        header = "Hiii!" if event.is_reply else get_text(event)
        base = header + "\n\n"
        text = base
        count = 0
        first = True
        reply_to = event.reply_to_msg_id
        
        async for user in client.iter_participants(event.chat_id, aggressive=True):
            if user.bot:
                continue
            
            emoji = random.choice(EMOJIS)
            text += f'<a href="tg://user?id={user.id}">{emoji}</a> '
            count += 1
            
            if count == 25:
                await safe_send(event.chat_id, text, reply_to if first else None)
                text = base
                count = 0
                first = False
                await asyncio.sleep(0.5)
        
        if count > 0:
            await safe_send(event.chat_id, text, reply_to if first else None)
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/mentiononline"))
async def mention_online(event):
    if not allowed(event):
        return
    try:
        header = "Hiii!" if event.is_reply else get_text(event)
        base = header + "\n\n"
        text = base
        count = 0
        first = True
        reply_to = event.reply_to_msg_id
        
        async for user in client.iter_participants(event.chat_id, aggressive=True):
            if user.bot:
                continue
            
            is_active = False
            
            if isinstance(user.status, UserStatusOnline):
                is_active = True
            elif isinstance(user.status, UserStatusRecently):
                is_active = True
            elif hasattr(user.status, 'was_online'):
                now = datetime.now(timezone.utc)
                if user.status.was_online:
                    time_diff = now - user.status.was_online.replace(tzinfo=timezone.utc)
                    if time_diff < timedelta(minutes=10):
                        is_active = True
            
            if not is_active:
                continue
            
            emoji = random.choice(EMOJIS)
            text += f'<a href="tg://user?id={user.id}">{emoji}</a> '
            count += 1
            
            if count == 25:
                await safe_send(event.chat_id, text, reply_to if first else None)
                text = base
                count = 0
                first = False
                await asyncio.sleep(0.5)
        
        if count > 0:
            await safe_send(event.chat_id, text, reply_to if first else None)
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/limited$"))
async def limited(event):
    if not allowed(event):
        return
    try:
        banned = []
        muted = []
        
        async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantsKicked):
            banned.append(user)
        
        async for user in client.iter_participants(event.chat_id):
            p = user.participant
            if hasattr(p, "banned_rights") and p.banned_rights and p.banned_rights.send_messages:
                muted.append(user)

        parts = ["🚫 Banned Users:\n"]
        if banned:
            parts.extend(f'- <a href="tg://user?id={u.id}">{u.first_name or "User"}</a>\n' for u in banned)
        else:
            parts.append("None\n")

        parts.append("\n🔇 Muted Users:\n")
        if muted:
            parts.extend(f'- <a href="tg://user?id={u.id}">{u.first_name or "User"}</a>\n' for u in muted)
        else:
            parts.append("None\n")

        await client.send_message(event.chat_id, ''.join(parts), parse_mode="html")
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/unmute($|\s)"))
async def unmute(event):
    if not allowed(event):
        return
    try:
        target = get_target(event)
        if not target:
            return
        user = await client.get_entity(target)
        await client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
        
        name = user.first_name or "User"
        msg = f'You are unmuted\n\n<a href="tg://user?id={user.id}">{name}</a>'
        await client.send_message(event.chat_id, msg, parse_mode="html")
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/unmuteall$"))
async def unmute_all(event):
    if not allowed(event):
        return
    try:
        unmuted = []
        
        async for user in client.iter_participants(event.chat_id):
            p = user.participant
            if hasattr(p, "banned_rights") and p.banned_rights and p.banned_rights.send_messages:
                try:
                    await client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
                    unmuted.append(user)
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
        
        if unmuted:
            base = "You are unmuted\n\n"
            msg = base
            count = 0
            
            for u in unmuted:
                name = u.first_name or "User"
                msg += f'<a href="tg://user?id={u.id}">{name}</a> '
                count += 1
                
                if count == 25:
                    await client.send_message(event.chat_id, msg, parse_mode="html")
                    msg = base
                    count = 0
                    await asyncio.sleep(0.3)
            
            if count > 0:
                await client.send_message(event.chat_id, msg, parse_mode="html")
        else:
            await client.send_message(event.chat_id, "No muted users found")
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/unban($|\s)"))
async def unban(event):
    if not allowed(event):
        return
    try:
        target = get_target(event)
        if not target:
            return
        user = await client.get_entity(target)
        await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        
        name = user.first_name or "User"
        msg = f'You are unbanned\n\n<a href="tg://user?id={user.id}">{name}</a>'
        await client.send_message(event.chat_id, msg, parse_mode="html")
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/unbanall$"))
async def unban_all(event):
    if not allowed(event):
        return
    try:
        unbanned = []
        
        async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantsKicked):
            try:
                await client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
                unbanned.append(user)
                await asyncio.sleep(0.1)
            except Exception:
                pass
        
        if unbanned:
            base = "You are unbanned\n\n"
            msg = base
            count = 0
            
            for u in unbanned:
                name = u.first_name or "User"
                msg += f'<a href="tg://user?id={u.id}">{name}</a> '
                count += 1
                
                if count == 25:
                    await client.send_message(event.chat_id, msg, parse_mode="html")
                    msg = base
                    count = 0
                    await asyncio.sleep(0.3)
            
            if count > 0:
                await client.send_message(event.chat_id, msg, parse_mode="html")
        else:
            await client.send_message(event.chat_id, "No banned users found")
    except Exception:
        pass

@client.on(events.NewMessage(pattern=r"^/avtar$"))
async def avatar(event):
    if event.chat_id != ALLOWED_GROUP_ID:
        return
    try:
        user = await event.get_sender()
        photos = await client.get_profile_photos(user, limit=10)

        if not photos:
            return

        mention = f'<a href="tg://user?id={user.id}">{user.first_name or "User"}</a>'

        await client.send_file(
            event.chat_id,
            photos,
            caption=mention,
            parse_mode="html"
        )
    except Exception:
        pass

client.run_until_disconnected()

#STEIN @rejerk at telegram

