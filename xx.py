
import asyncio, hashlib, sys, os, requests, re, time
from telethon import TelegramClient, events, errors
import asyncio
import re
from collections import deque
from telethon import events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from datetime import datetime
import socket
import time
import uuid
import platform

# --- 🎨 COLORS ---

G, Y, R, C, W, B = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[0m', '\033[1m'

# --- 🔐 CONFIGURATION (MAIN CONTROLLER WILL DYNAMICALLY REPLACE THIS) ---

# =====================================================================

# ======= CONTROLLER_REPLACE_START =======

# ======= CONFIGURATION =======
# নিচের ভ্যালুগুলো None করে দিন
API_ID = None 
API_HASH = None
NEW_BOT_TOKEN = '8748128265:AAGtC5JFJZQs5XS-3iUABDe63zQmzpMHQLo' 
USER_TG_ID = 5864155541
             


MAIN_SNIPER_BOT = 'XPrepaidsExchangeBot'  # যেটাতে ইউজারবোট ক্লিক করবে

STOCK_CHANNEL_ID = -1003280015883        # আপনার দেওয়া স্টক চ্যানেল আইডি

NEW_CONTROL_BOT = 'xsnipercontrollerbot'  # নতুন বটের ইউজারনেম



# --- 🛠 UI & LOGGING ---

def ui_header():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                      X-SNIPER v27.0                      ║")
    print("║             SECURED MULTI-TARGET SNIPER ENGINE           ║")
    print("║             Developed By: Yasir Arafat                   ║")
    print("╚══════════════════════════════════════════════════════════╝")




# 🛠️ নতুন নিখুঁত লাইন:

SESSION_NAME = f"cloned_bots/session_{USER_TG_ID}"

BOT_SESSION_NAME = f"cloned_bots/bot_ctrl_{USER_TG_ID}"



client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

bot_client = TelegramClient(BOT_SESSION_NAME, API_ID, API_HASH) # <─── একদম ক্লিন ও এররমুক্ত





# --- GLOBAL STATE ---

targets = [] 

min_bal = 1.0   

max_bal = 30.0

APPROVED_BINS = ["461126", "403446", "491277", "435880", "511332", "533985", "451129"]

click_lock = asyncio.Lock()

is_paused = False  # শুরুতে বোট রানিং থাকবে

TOTAL_HITS = 0

TOTAL_MISS = 0



# 🛠️ স্বয়ংক্রিয়ভাবে ওনার আইডি ট্র্যাক করার গ্লোবাল ভ্যারিয়েবল

MY_TELEGRAM_ID = None

# 🚀 [NEW METHOD]: সরাসরি আপনার কন্ট্রোলার বটের ইনবক্সে লাইভ লগ পুশ ফাংশন

# =====================================================================

def log(msg, type="info"):
    now = datetime.now().strftime("%H:%M:%S")
    
    if type == "success": 
        print(f"🟢 [{now}] [SUCCESS] {msg}")
        tg_msg = f"🟢 **[{now}] [SUCCESS]**\n└ `{msg}`"
    elif type == "error": 
        print(f"🔴 [{now}] [ERROR] {msg}")
        tg_msg = f"🔴 **[{now}] [ERROR]**\n└ `{msg}`"
    elif type == "target": 
        print(f"🎯 [{now}] [TARGET] {msg}")
        tg_msg = f"🎯 **[{now}] [TARGET LOCKED]**\n└ `{msg}`"
    elif type == "wait": 
        print(f"🟡 [{now}] [ALERT] {msg}")
        tg_msg = f"🟡 **[{now}] [ALERT]**\n└ `{msg}`"
    else: 
        print(f"ℹ️ [{now}] [INFO] {msg}")
        tg_msg = f"ℹ️ **[{now}] [INFO]**\n└ `{msg}`"

    if 'bot_client' in globals() and bot_client.is_connected() and MY_TELEGRAM_ID:
        try:
            asyncio.create_task(bot_client.send_message(MY_TELEGRAM_ID, tg_msg))
        except:
            pass

# --- ⚙️ API SETUP ---

def load_config():

    if os.path.exists("config.txt"):

        with open("config.txt", "r") as f:

            lines = [line.strip() for line in f.readlines() if line.strip()]

            if len(lines) >= 2:

                return int(lines[0]), lines[1]

    

    ui_header()

    log("Enter API details to continue:", "wait")

    api_id = input(f"{C}Enter API ID: {W}").strip()

    api_hash = input(f"{C}Enter API Hash: {W}").strip()

    with open("config.txt", "w") as f:

        f.write(f"{api_id}\n{api_hash}")

    return int(api_id), api_hash



# --- ⚡ PRECISE FLOODING ENGINE ---

async def send_flood_command(command, delay, target_ref):

    await asyncio.sleep(delay)

    if target_ref not in targets: return 

    try:

        await client.send_message(MAIN_SNIPER_BOT, command)

        target_ref["resp_a"] = datetime.now().strftime("%H:%M:%S")

    except: pass



# =====================================================================

# ⏱️ [BEST TIMING UPDATE]: সার্ভার ল্যাটেন্সি কভার করতে ১১৯.৩ ও ১১৯.৭ সেকেন্ডে ফ্লাড

# =====================================================================

async def start_sniper_timer(target_card):

    global TOTAL_MISS

    t_bin = str(target_card.get('bin', '')).strip()

    t_bal = str(target_card.get('bal', '')).replace('$', '').strip()

    range_command = f"/listing_range {t_bal} {t_bal}"

    

    target_card["status"] = "TRACKING"

    asyncio.create_task(send_flood_command(range_command, 118.4, target_card))
 
    asyncio.create_task(send_flood_command(range_command, 118.8, target_card))

    asyncio.create_task(send_flood_command(range_command, 119, target_card)) # ১ম ফ্লাড

    asyncio.create_task(send_flood_command(range_command, 119.4, target_card)) # ২য় ফ্লাড

    asyncio.create_task(send_flood_command(range_command, 119.8, target_card)) # ৩য় ফ্লাড

    asyncio.create_task(send_flood_command(range_command, 120, target_card)) # ৪র্থ ফ্লাড)



    countdown = 120.0

    while countdown > 0:

        if target_card not in targets: return 

        await asyncio.sleep(0.1)

        countdown -= 0.1

        

        target_card["countdown"] = countdown

        target_card["timer"] = f"{round(countdown, 1)}s"

        

        if round(countdown, 1) <= 0.7:

            target_card["status"] = "ATTACKING"

            

    target_card["timer"] = "0.0s"

    target_card["countdown"] = 0.0

    

    # মেইন বটের মেনু জেনারেট হতে টাইম লস হয়, তাই মেমরিতে এক্সট্রা ৫ সেকেন্ড হোল্ড করবে

    await asyncio.sleep(5.0) 

    if target_card in targets:

        targets.remove(target_card)

        TOTAL_MISS += 1

        log(f"Auto-Dropped (Menu not captured after floods): {t_bin} (${t_bal})", "error")



#---Matching Engine----

def find_target_btn(msg):
    if not msg or not msg.buttons or not msg.text:
        return None, None, None

    full_text = msg.text
    lines = full_text.splitlines()
    BAD_EMOJIS = ["🔄", "🅶", "🅿️", "♻️", "❌", "used", "relist"]

    for target in targets:
        t_bin = str(target.get('bin', '')).strip()
        t_bal = str(target.get('bal', '')).replace('$', '').strip()

        for line in lines:
            clean_line = line.strip()
            if not clean_serial_check(clean_line, t_bin, t_bal): continue
            
            is_dirty = False
            for emoji in BAD_EMOJIS:
                if emoji in clean_line:
                    is_dirty = True
                    break
            if is_dirty or not clean_line.endswith('%'): continue

        
            
            serial = clean_line.split('.')[0].strip() + "."
            for row in msg.buttons:
                if row and row[0].text.strip().startswith(serial):
                    for btn in row:
                        if 'purchase' in btn.text.lower(): 
                            return msg.id, btn.data, target
                    return msg.id, row[0].data, target

        for row in msg.buttons:
            if any(t_bin in btn.text and t_bal in btn.text for btn in row):
                for btn in row:
                    if 'purchase' in btn.text.lower():
                        
                        return msg.id, btn.data, target
                for btn in row:
                    if t_bin in btn.text and t_bal in btn.text:
                        return msg.id, btn.data, target

def clean_serial_check(line, bin_val, bal_val):
    low_line = line.lower().replace(' ', '')
    return bin_val in low_line and bal_val in low_line.replace('$', '')

# --- ⚡ ULTRA-FAST DIRECT EXECUTOR ---
async def attack(msg_id, chat_id, button_data, target_obj):
    global TOTAL_HITS
    t_bin = target_obj.get('bin', '')
    t_bal = target_obj.get('bal', '')
    
    async with click_lock:
        try:
            from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
            # সরাসরি ১ মিলিসেকেন্ড ল্যাটেন্সিতে কলব্যাক পুশ
            await client(GetBotCallbackAnswerRequest(
                peer=chat_id,
                msg_id=msg_id,
                data=button_data
            ))
            print(f"⚡ [DIRECT HIT SUCCESS] CallBack Sent for BIN: {t_bin}")
        except Exception as e: 
            pass
            
    TOTAL_HITS += 1



# --- AUTOMATED STOCK LISTENER ---

@client.on(events.NewMessage(chats=STOCK_CHANNEL_ID))

async def stock_listener(event):

    global targets

    if is_paused: return

    text = event.raw_text

    

    bin_match = re.search(r'Card BIN:\s*(\d{6})', text, re.IGNORECASE)

    bal_match = re.search(r'Balance:.*?\$(\d+\.\d+)', text, re.IGNORECASE)

    

    paypal_no = re.search(r'Used PayPal:\s*No', text, re.IGNORECASE)

    google_no = re.search(r'Used Google:\s*No', text, re.IGNORECASE)

    reg_false = re.search(r'Registered:\s*false', text, re.IGNORECASE)

    reg_true = re.search(r'Registered:\s*True', text, re.IGNORECASE)



    if bin_match and bal_match:

        t_bin = bin_match.group(1)

        t_bal = float(bal_match.group(1))



        if t_bin not in APPROVED_BINS: return

        if not (min_bal <= t_bal <= max_bal): return 



        should_add = False

        if t_bal > 30.0: return



        if google_no:

            if reg_false: should_add = True

            elif reg_true and paypal_no:

                if t_bal < 17.0: should_add = True



        if should_add:

            if not any(t['bin'] == t_bin and t['bal'] == str(t_bal) for t in targets):

                new_target = {

                    'bin': t_bin, 

                    'bal': str(t_bal), 

                    'timer': '120.0s',

                    'status': 'TRACKING',

                    'resp_a': '-',

                    'added_at': time.time() 

                }

                targets.append(new_target)

                serial_num = len(targets)

                log(f"Auto-Target Added [Serial: {serial_num}]: {t_bin} (${t_bal})", "target")

                

                asyncio.create_task(start_sniper_timer(new_target))



# --- CONTROL BOT COMMAND HANDLER ---

@bot_client.on(events.NewMessage)

async def command(event):

    global targets, min_bal, max_bal, is_paused, MY_TELEGRAM_ID

    

    # কঠোর নিরাপত্তা লক: কারেন্ট রানিং ওনার আইডি ছাড়া অন্য কারও কমান্ড গ্রাহ্য করবে না

    if MY_TELEGRAM_ID is None or event.sender_id != MY_TELEGRAM_ID:

        return



    txt = event.raw_text.strip()



    # ১. স্টক নোটিফিকেশন মেসেজ ফুল পেস্ট ট্র্যাকিং লজিক

    if "card bin" in txt.lower() and "balance" in txt.lower():

        if is_paused:

            await bot_client.send_message(event.chat_id, "⚠️ **Cannot Lock Target!** Sniper Engine is currently paused. Please type `resume` first.")

            return

            

        bin_match = re.search(r'Card BIN:\s*(\d{6})', txt, re.IGNORECASE)

        bal_match = re.search(r'Balance:.*?(?:\$|€|£)?\s*(\d+\.\d+)', txt, re.IGNORECASE)



        if bin_match and bal_match:

            t_bin = bin_match.group(1)

            t_bal = bal_match.group(1)

            

            if not any(t['bin'] == t_bin and t['bal'] == str(t_bal) for t in targets):

                new_target = {

                    'bin': t_bin, 

                    'bal': str(t_bal), 

                    'timer': '120.0s',

                    'status': 'TRACKING',

                    'resp_a': '-',

                    'added_at': time.time() 

                }

                targets.append(new_target)

                serial_num = len(targets)

                log(f"Manual Extract [Serial: {serial_num}]: {t_bin} (${t_bal})", "target")

                

                asyncio.create_task(start_sniper_timer(new_target))

                

                msg_text = f"🎯 **Target Locked!**\nBIN: `{t_bin}`\nBalance: `${t_bal}`\n\n🚀 Sniper is now **ACTIVE**."

                await bot_client.send_message(event.chat_id, msg_text)

            else:

                await bot_client.send_message(event.chat_id, "⚠️ Target already exists in memory!")

        else:

            await bot_client.send_message(event.chat_id, "❌ Failed to extract BIN or Balance. Please paste the exact stock message.")

    

    # ২. কন্ট্রোল কমান্ডসমূহ (রিপ্লাই যাবে সরাসরি বটের নিজস্ব প্রোফাইল থেকে)

    else:

        cmd = txt.lower()

        

        if cmd.startswith('/'): cmd = cmd[1:] 

        if cmd.startswith('set_range'): cmd = cmd.replace('set_range', 'set')

            

        if cmd in ["targets", "status", "clear", "stop", "resume"] or cmd.startswith("cancel") or cmd.startswith("set"):

            

            if cmd == "targets":

                if not targets:

                    await bot_client.send_message(event.chat_id, "❌ No targets in memory.\nℹ️ *To add a target, paste the raw stock message directly.*")

                else:

                    msg = "🎯 **Active Targets List:**\n"

                    for i, t in enumerate(targets, 1):

                        msg += f"{i}. BIN: `{t['bin']}` | Bal: `${t['bal']}`\n"

                    msg += "\nℹ️ *Use `cancel SERIAL` to remove any target.*"

                    await bot_client.send_message(event.chat_id, msg)



            elif cmd.startswith("cancel"):

                try:

                    parts = cmd.split()

                    index = int(parts[1]) - 1

                    if 0 <= index < len(targets):

                        targets.pop(index)

                        await bot_client.send_message(event.chat_id, f"✅ Target {index + 1} Removed successfully.")

                    else:

                        await bot_client.send_message(event.chat_id, "❌ Invalid serial number!\nℹ️ *Check active serials using `targets`*")

                except:

                    await bot_client.send_message(event.chat_id, "❌ **Format Error!**\n💡 Use: `cancel 1`")



            elif cmd == "status":

                state = "⏸️ PAUSED" if is_paused else ("🔥 ACTIVE" if targets else "💤 SLEEPING")

                status_msg = (

                    f"📊 **System Status:** {state}\n"

                    f"📦 **Active Targets:** {len(targets)}\n"

                    f"💰 **Allowed Range:** `${min_bal}` - `${max_bal}`\n\n"

                    f"📝 **Quick Guide (Click to Copy):**\n"

                    f"🔹 Check active targets: `targets`\n"

                    f"🔹 Change price range: `set_range 2 15`\n"

                    f"🔹 Delete specific target: `cancel 1`\n"

                    f"🔹 Pause entire engine: `stop`\n"

                    f"🔹 Resume engine: `resume`\n"

                    f"🔹 Wipe engine memory: `clear`"

                )

                await bot_client.send_message(event.chat_id, status_msg)

            

            elif cmd == "clear":

                targets.clear()

                await bot_client.send_message(event.chat_id, "🧹 **Memory Cleared!** All tracking targets removed.")



            elif cmd.startswith("set"):

                try:

                    parts = cmd.split()

                    if len(parts) < 3:

                        guide_msg = "ℹ️ **To set your balance range type:**\n\n`/set_range <min> <max>`\n\n**Example:** `/set_range 2 15`"

                        await bot_client.send_message(event.chat_id, guide_msg)

                        return



                    min_bal = float(parts[1])

                    max_bal = float(parts[2])

                    await bot_client.send_message(event.chat_id, f"✅ **Auto-Filter Updated!**\n💰 Range set to: `${min_bal}` - `${max_bal}`")

                except:

                    guide_msg = "❌ **Format Error!**\n\nℹ️ **To set your balance range type:**\n\n`/set_range <min> <max>`\n\n**Example:** `/set_range 2 15`"

                    await bot_client.send_message(event.chat_id, guide_msg)



            elif cmd == "stop":

                targets.clear()

                is_paused = True

                await bot_client.send_message(event.chat_id, "🛑 **Sniper Engine Paused.** System is now `SLEEPING`. All current targets wiped. Type `resume` to re-activate.")



            elif cmd == "resume":

                if is_paused:

                    is_paused = False

                    await bot_client.send_message(event.chat_id, "🔥 **Sniper Engine Re-Activated!** Monitoring is now `LIVE`.")

                else:

                    await bot_client.send_message(event.chat_id, "ℹ️ Sniper Engine is already **LIVE**.")



# 📦 ১. সাইজ ৩ এর আল্ট্রা-লাইট মেমোরি ক্যাশ (আপনার গাইডলাইন অনুযায়ী)
menu_cache = deque(maxlen=3)

def push_to_cache(msg):
    if not msg or not msg.text: 
        return
    # ডুপ্লিকেট আইডি থাকলে পুরোনোটা সরিয়ে ফ্রেশটা পুশ করা
    for old_msg in list(menu_cache):
        if old_msg.id == msg.id:
            menu_cache.remove(old_msg)
            break
    menu_cache.appendleft(msg)

# ⚡ ২. ১-মিলিসেকেন্ড র কলব্যাক এক্সিকিউটর এবং অল-পপ-আপ ডিটেক্টর
async def instant_callback_hit(chat_id, msg_id, button_data):
    try:
        # 🚀 ডিরেক্ট কলব্যাক পুশ এবং রেজাল্ট সেভ
        result = await client(GetBotCallbackAnswerRequest(
            peer=chat_id,
            msg_id=msg_id,
            data=button_data
        ))
        

        # 🛑 যেকোনো ধরনের পপ-আপ মেসেজ ডিটেকশন (Universal Catcher) 🛑
        if result and hasattr(result, 'message') and result.message:
            alert_text = result.message
            
            # মেসেজের টেক্সট যাই হোক না কেন, সেটাকে ক্যাটাগরি করে ইনবক্সে পাঠাবে
            text_lower = alert_text.lower()
            if "success" in text_lower or "✅" in text_lower:
                log(f"Bot Reply: {alert_text}", "success")
            elif "error" in text_lower or "❌" in text_lower or "fail" in text_lower or "already" in text_lower:
                log(f"Bot Alert: {alert_text}", "error")
            else:
                log(f"Bot Message: {alert_text}", "wait")

    except Exception as e:
        
        pass  


# ─── 📡 ৩. আপনার অপ্টিমাইজড মেইন হ্যান্ডলার (No Auto-Confirm) ───
@client.on(events.NewMessage(chats=MAIN_SNIPER_BOT))
@client.on(events.MessageEdited(chats=MAIN_SNIPER_BOT))
async def hybrid_fast_handler(event):
    if not targets: 
        return
        
    current_msg = event.message
    
    # 🎯 ধাপ ১: [EVENT FIRST] আসার সাথে সাথে ইনকামিং মেসেজ স্ক্যান
    if current_msg and current_msg.text:
        text_lower = current_msg.text.lower()
        
        # 🛑 এখানে কনফার্ম উইন্ডোর অটো-ক্লিক লজিকটি সম্পূর্ণ মুছে দেওয়া হয়েছে!
        
        # 🎯 শুধুমাত্র লিস্টিং মেনু চেক (Purchase Button)
        if "main listings v2" in text_lower and current_msg.buttons:
            match_result = find_target_btn(current_msg)
            if isinstance(match_result, tuple) and len(match_result) == 3:
                msg_id, btn_data, target_obj = match_result
                if btn_data and target_obj:
                    # 🛑 একবার পারচেজ বাটনে ক্লিক করার পরই মেমরি থেকে টার্গেট মুছে দেওয়া হবে, যেন ডাবল ক্লিক না পড়ে
                    if target_obj in targets:
                        targets.remove(target_obj)
                        log(f"Purchase Hit Success for BIN {target_obj.get('bin', '')}! ✅", "wait")
                    asyncio.create_task(instant_callback_hit(event.chat_id, msg_id, btn_data))
                    return

    # কারেন্ট মেসেজে সাথে সাথে ম্যাচ না মিললে এটিকে ক্যাশে পুশ করে লোকাল ক্যাশ স্ক্যান শুরু
    push_to_cache(current_msg)

    # 🎯 ধাপ ২: [CACHE SCAN] মেমোরি থেকে ১, ২, ৩ নম্বর মেনু ব্যাকআপ স্ক্যান
    try:
        for cached_msg in menu_cache:
            if cached_msg.id == current_msg.id: 
                continue  
                
            cached_text_lower = (cached_msg.text or "").lower()
            
            # 🎯 ক্যাশড মেসেজে শুধুমাত্র পারচেজ চেক
            if "main listings v2" in cached_text_lower and cached_msg.buttons:
                match_result = find_target_btn(cached_msg)
                if isinstance(match_result, tuple) and len(match_result) == 3:
                    msg_id, btn_data, target_obj = match_result
                    if btn_data and target_obj:
                        if target_obj in targets:
                            targets.remove(target_obj)
                            log(f"Purchase Hit Success for BIN {target_obj.get('bin', '')}! Waiting for your manual confirm...", "wait")
                        asyncio.create_task(instant_callback_hit(event.chat_id, msg_id, btn_data))
                        return
    except Exception:
        pass

# --- AUTO-CLEANUP ENGINE (SMART & SAFE CLEANER) ---

async def auto_cleanup():

    while True:

        try:

            now = time.time()

            for target in targets[:]: 

                if now - target.get('added_at', now) > 125:

                    targets.remove(target)

            

            # 🧹 মেইন বটের চ্যাট হিস্ট্রি ক্লিন করার ম্যাজিক (LUCKY MENU SAVER)

            try:

                messages = await client.get_messages(MAIN_SNIPER_BOT, limit=20)

                msgs_to_delete = []

                

                for i, msg in enumerate(messages):

                    if i == 0: continue 

                        

                    text = msg.text or ""

                    text_lower = text.lower()

                    

                    if msg.out and "/listing_range" in text_lower:

                        msgs_to_delete.append(msg.id)

                        continue

                        

                    if "main listings v2" in text_lower and "legend:" in text_lower:

                        msg_age = time.time() - msg.date.timestamp()

                        if msg_age < 10: continue 



                        is_lucky_menu = False

                        for j in range(i - 1, -1, -1):

                            newer_text = (messages[j].text or "").lower()

                            if "main listings v2" in newer_text and "legend:" in newer_text:

                                break 

                            if "confirm" in newer_text or "success" in newer_text:

                                is_lucky_menu = True

                                break

                                

                        # লজিকটি এখন ঠিকঠাক লুপের ভেতরে আছে

                        if not is_lucky_menu:

                            msgs_to_delete.append(msg.id)



                if msgs_to_delete:

                    await client.delete_messages(MAIN_SNIPER_BOT, msgs_to_delete)

            except Exception as e:

                pass



            await asyncio.sleep(10)

        except: 

            await asyncio.sleep(10)







# --- START ---
async def main():
    global MY_TELEGRAM_ID, client, bot_client # Global গুলো এখানে লিখুন
    
    # নতুন করে কনফিগারেশন লোড করা
    api_id, api_hash = load_config()
    
    # নতুন করে ক্লায়েন্ট তৈরি করা (যেহেতু এখন এপিআই আইডি পাওয়া গেছে)
    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    bot_client = TelegramClient(BOT_SESSION_NAME, api_id, api_hash)
    log("Connecting to Telegram Engine...", "wait")
    
    await client.start() 
    await bot_client.start(bot_token=NEW_BOT_TOKEN) 

    me = await client.get_me()
    MY_TELEGRAM_ID = me.id 
    
    asyncio.create_task(auto_cleanup())
    ui_header()
    log(f"Successfully Connected to Main Bot for User: {me.first_name}", "success")
    
    # 🚀 ডিরেক্ট স্টার্ট নোটিফিকেশন পুশ
    try:
        start_notification = f"🚀 **X-SNIPER v28.0 Is Live!**\n└ Owner: `{me.first_name}`\n└ Location: `Singapore Server` 🇸🇬"
        await bot_client.send_message(MY_TELEGRAM_ID, start_notification)
    except:
        pass
    
    # ব্যাকগ্রাউন্ডে স্নাইপিং লুপ সচল রাখা
    while True:
        await asyncio.sleep(1)

# --- AUTO RECOVERY & NETWORK CHECKER ---

def wait_for_internet():

    """Silently internet er jonno wait korbe, loop korbe na"""

    is_printed = False

    while True:

        try:

            # Google er DNS e ping kore check korbe net ache kina

            socket.create_connection(("1.1.1.1", 53), timeout=3)

            if is_printed:

                print("🌐 Network connection activated! Bot is resuming...")

            return

        except OSError:

            if not is_printed:

                print("⚠️ No internet connection. Waiting silently in background...")

                is_printed = True

            time.sleep(5)



if __name__ == "__main__":

    while True:

        try:

            wait_for_internet() # Prothome net check korbe

            client.loop.run_until_complete(main())

        except Exception as e:

            # Error hole purono stuck session gulo clear kore dibe jeno loop e na pore

            try:

                client.loop.run_until_complete(client.disconnect())

                client.loop.run_until_complete(bot_client.disconnect())

            except:

                pass

            time.sleep(3) # 3 second rest niye abar wait_for_internet() e chole jabe
