import asyncio
from aminodorksfix.asyncfix import Client, SubClient
from telegram import Bot
import time

# ===== شعار عند بدء التشغيل =====
print(r"""
____             _           _       _
 |  _ \  ___  _ __| | _____   / \   __| |_   __
 | | |/ _ \| '__| |/ / __| / _ \ / /` \ \ / /
 | |_| | (_) | |  |   <\__ \/ ___ \ (_| |\ V /
 |____/ \___/|_|  |_|\_\___/_/   \_\__,_| \_/

Telegram: pxiz3
""")

# ===== رسالة الترويج =====
PROMO_MESSAGE ="[C]𐏐̶      .   🇺🇸 ENGLISH ⠀  ⎯⎯⠀ ⠀៲𝐈𝐈̶ 𝐈𝐈̶៲    ⠀ۭ  ⠀  ⿻̷࣫    ⠀                                 When you  come  ,  the  girls   fade                                         like   shadows  They melt around  u    vanish   above        and  below                                                                                            aminoapps.com/c/Randamino                                                                 𐏐̶     .   🇮🇶 العربيـة ⠀  ⎯⎯⠀ ⠀៲𝐈𝐈̶ 𝐈𝐈̶៲          ⠀ۭ  ⠀  ⿻̷࣫   ⠀                                                             عِندَ  مَجِيئِكَ  ،  تَتَبَدَّدُ  الفَتَيَاتُ   كَأَطْيَافٍ   زَائِلَةٍ                                        فَتَذُوبُ حَوْلَكَ، وَتَتَلاشَى فَوقَكَ، وَتَنفَصِمُ تَحتَكَ                                                                         aminoapps.com/c/Randamino                                                                             𐏐̶      .   🇪🇸 Español ⠀  ⎯⎯⠀ ⠀៲𝐈𝐈̶ 𝐈𝐈̶៲    ⠀ۭ  ⠀ ⿻̷࣫                                                             Al   venir   tú  ,  las   chicas    se    desvanecen      como sombras Se derriten a tu desaparecen          aminoapps.com/c/Randamino"
CHAT_TITLE = "حاول تتكلم"
CHAT_CONTENT = PROMO_MESSAGE

# ===== تسجيل الدخول =====
async def login(client: Client):
    while True:
        try:
            email = input("[*] ايميل: ")
            password = input("[*] باسورد: ")
            await client.login(email, password)
            print("تم التسجيل بنجاح ✅")
            break
        except Exception as e:
            print(f"[LoginException]: {e}, حاول مرة ثانية.")

# ===== اختيار أعلى 5 مجتمعات =====
async def choose_top_communities(client: Client):
    communities = await client.sub_clients()
    selected = [(communities.comId[i], communities.name[i]) for i in range(min(5, len(communities.name)))]
    return selected

# ===== استثناء القادة والمنسقين =====
async def get_excluded_users(sub_client: SubClient):
    excluded_users = []
    excluded_names = []

    leaders_response, curators_response, blocked_response = await asyncio.gather(
        sub_client.get_all_users(type="leaders"),
        sub_client.get_all_users(type="curators"),
        sub_client.get_blocked_users(),
    )

    for user in leaders_response.json.get("userProfileList", []):
        excluded_users.append(user["uid"])
        excluded_names.append(user["nickname"])
    for user in curators_response.json.get("userProfileList", []):
        excluded_users.append(user["uid"])
        excluded_names.append(user["nickname"])
    for user in blocked_response.json:
        excluded_users.append(user["uid"])

    return excluded_users, excluded_names

# ===== جلب الأعضاء الأونلاين فقط =====
async def get_users(sub_client: SubClient):
    excluded_users, _ = await get_excluded_users(sub_client)
    online_page = await sub_client.get_online_users()
    len_users_in_online = online_page.json.get("userProfileCount", 0)

    tasks = [sub_client.get_online_users(start=start, size=start+100) for start in range(0, len_users_in_online, 100)]
    online_results = await asyncio.gather(*tasks)

    online_users = set()
    for response in online_results:
        for user in response.json.get("userProfileList", []):
            uid = user["uid"]
            if uid not in excluded_users:
                online_users.add(uid)

    all_users = list(online_users)
    groups = [all_users[i:i+99] for i in range(0, len(all_users), 99)]
    return groups

# ===== الترويج الجماعي =====
async def mass_chat_send_online(sub_client: SubClient, groups, bot: Bot, telegram_chat_id, excluded_names, community_name, total_counter):
    sent_uids = set()

    for group in groups:  # يشتغل على كل المجموعات
        try:
            blocked_now = await sub_client.get_blocker_users()
            filtered_group = [uid for uid in group if uid not in blocked_now["blockerUidList"]]

            if not filtered_group:
                continue

            chat = await sub_client.start_chat(userId=filtered_group, message=PROMO_MESSAGE)
            await sub_client.edit_chat(chatId=chat.chatId, title=CHAT_TITLE, content=CHAT_CONTENT, viewOnly=True)

            sent_uids.update(filtered_group)
            total_counter["count"] += len(filtered_group)
            print(f"⚙️ تم إنشاء دردشة في '{community_name}' 🪪 عدد الأعضاء في الدردشة: {len(filtered_group)}")

            await asyncio.sleep(5)

        except Exception as e:
            print(f"[❌] خطأ في {community_name}: {e}")
            continue  # يكمل على باقي المجموعات

    # إرسال إشعار للتليجرام بعد كل مجتمع
    if sent_uids:
        msg = f"📌 مجتمع: {community_name}\n👥 عدد الأعضاء الذين روج لهم: {len(sent_uids)}\n🚫 القادة والمنسقين المستبعدين: {', '.join(excluded_names)}"
        try:
            await bot.send_message(chat_id=telegram_chat_id, text=msg)
            await asyncio.sleep(10)
        except Exception as e:
            print(f"[❌] خطأ في إرسال إشعار التليجرام: {e}")

    return sent_uids

# ===== الدالة الرئيسية =====
async def main():
    API_KEY = "b7de71a758ae81ad40bda2cd464e2d58"
    client = Client(api_key=API_KEY, socket_enabled=False)
    await login(client)

    selected_communities = await choose_top_communities(client)
    TELEGRAM_TOKEN = input("[*] ادخل توكن بوت التليجرام: ")
    TELEGRAM_CHAT_ID = -1003123800306
    bot = Bot(token=TELEGRAM_TOKEN)

    total_counter = {"count": 0}
    for comId, comName in selected_communities:
        sub_client = SubClient(comId=comId, profile=client.profile)
        _, excluded_names = await get_excluded_users(sub_client)
        groups = await get_users(sub_client)
        await mass_chat_send_online(sub_client, groups, bot, TELEGRAM_CHAT_ID, excluded_names, comName, total_counter)

    # الإشعار النهائي
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"✅ تم انتهاء الترويج بنجاح\n📊 العدد الكلي للأعضاء الذين تم الترويج لهم: {total_counter['count']}")
    except Exception as e:
        print(f"[❌] خطأ في إرسال الإشعار النهائي: {e}")

    print(f"تم انتهاء الترويج بنجاح ✅\n📊 العدد الكلي: {total_counter['count']}")

if __name__ == "__main__":
    asyncio.run(main())