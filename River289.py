from asyncio import gather, run
from typing import Any, List
from aminodorksfix.asyncfix import Client, SubClient
from telegram import Bot

# ===== شعار عند بدء التشغيل (raw string لتجنب التحذيرات) =====
print(r"""
____             _           _       _
 |  _ \  ___  _ __| | _____   / \   __| |_   __
 | | |/ _ \| '__| |/ / __| / _ \ / /` \ \ / /
 | |_| | (_) | |  |   <\__ \/ ___ \ (_| |\ V /
 |____/ \___/|_|  |_|\_\___/_/   \_\__,_| \_/

Telegram: pxiz3
""")

# ===== تسجيل الدخول =====
async def login(client: Client) -> None:
    try:
        await client.login(input("[*] Email: "), input("[*] Password: "))
    except Exception as e:
        print(f"[LoginException]: {e}")
        await login(client)

# ===== اختيار المجتمع =====
async def choose_community(client: Client) -> str:
    communities = await client.sub_clients()
    print("\nالمجتمعات التي أنت عضو فيها:")
    for index, name in enumerate(communities.name, 1):
        print(f"{index}.{name}")
    return communities.comId[int(input("[*]Enter the community number: ")) - 1]

# ===== استثناء القادة والمنسقين =====
async def get_excluded_users(sub_client: SubClient) -> List[Any]:
    excluded_users = []
    excluded_names = []

    leaders_response, curators_response, blocked_response = await gather(
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

# ===== جلب الأعضاء =====
async def get_users(sub_client: SubClient, member_count: int) -> List[List[Any]]:
    excluded_users, _ = await get_excluded_users(sub_client)

    online_page = await sub_client.get_online_users()
    len_users_in_online = online_page.json.get("userProfileCount", 0)

    tasks = [
        sub_client.get_online_users(start=start, size=start + 100)
        for start in range(0, len_users_in_online, 100)
    ]
    online_results = await gather(*tasks)

    online_users = set()
    for response in online_results:
        for user in response.json.get("userProfileList", []):
            uid = user["uid"]
            if uid not in excluded_users:
                online_users.add(uid)

    tasks = [
        sub_client.get_all_users(type="recent", start=start, size=start + 100)
        for start in range(0, 400, 100)
    ]
    recent_results = await gather(*tasks)

    recent_users = set()
    for response in recent_results:
        for user in response.json.get("userProfileList", []):
            uid = user["uid"]
            if uid not in excluded_users and uid not in recent_users and uid not in online_users:
                recent_users.add(uid)

    all_users = list(online_users | recent_users)[:member_count]
    groups = [all_users[i: i + 99] for i in range(0, len(all_users), 99)]

    return groups

# ===== الترويج الجماعي =====
async def mass_chat_send(
        sub_client: SubClient,
        groups: List[List[Any]],
        message: str,
        title: str,
        content: str,
        bot: Bot,
        telegram_chat_id: int,
        excluded_names: List[str]
) -> None:
    sent_uids = set()

    for group in groups:
        blocked_now = await sub_client.get_blocker_users()
        filtered_group = [uid for uid in group if uid not in blocked_now["blockerUidList"]]

        if not filtered_group:
            continue

        try:
            chat = await sub_client.start_chat(
                userId=filtered_group,
                message=message
            )
            if len(filtered_group) > 1:
                await sub_client.edit_chat(
                    title=title,
                    content=content,
                    chatId=chat.chatId,
                    viewOnly=True
                )
            sent_uids.update(filtered_group)
            print(f"[+] Chat with {len(filtered_group)} users created.")

        except Exception as e:
            print(f"[❌] Failed: {e}")
            continue

    # إشعار التليجرام بعد الانتهاء
    excluded_text = "\n".join(excluded_names) if excluded_names else "لا يوجد"
    await bot.send_message(
        chat_id=telegram_chat_id,
        text=f"✅ انتهى الترويج!\nتم ارسال الرسائل لـ {len(sent_uids)} أعضاء.\n"
             f"عدد القادة والمنسقين المستثنين: {len(excluded_names)}\n"
             f"أسماؤهم:\n{excluded_text}"
    )

# ===== الدالة الرئيسية =====
async def main() -> None:
    client = Client(api_key=input("[*] API key: "), socket_enabled=False)
    await login(client)

    sub_client = SubClient(
        comId=(await choose_community(client)),
        profile=client.profile,
    )

    member_count = int(input("[*] عدد الأعضاء للترويج: "))
    promo_message = input("[*] رسالة الترويج: ")
    chat_title = input("[*] عنوان الدردشة: ")
    chat_content = input("[*] وصف الدردشة: ")

    # توكن البوت جاهز داخل السكربت
    TELEGRAM_TOKEN = "8447283214:AAGEpvMOK1yyyLHieYHM2SOveskgQpe62Aw"
    TELEGRAM_CHAT_ID = -1003123800306  # ضع هنا معرف الدردشة إذا تريد ثابتا
    bot = Bot(token=TELEGRAM_TOKEN)

    _, excluded_names = await get_excluded_users(sub_client)

    await mass_chat_send(
        sub_client=sub_client,
        groups=await get_users(sub_client, member_count),
        message=promo_message,
        title=chat_title,
        content=chat_content,
        bot=bot,
        telegram_chat_id=TELEGRAM_CHAT_ID,
        excluded_names=excluded_names
    )

if __name__ == "__main__":
    run(main())