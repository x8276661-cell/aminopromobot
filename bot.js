const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const fs = require('fs');
const schedule = require('node-schedule');

// 🔑 التوكن الخاص بك
const token = "8118999111:AAGRKUMxreudNBbq_QDt1UszwG27cqhuSTY";
const bot = new TelegramBot(token, { polling: true });

let userTasks = {};

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, `
📦 *بوت حقيبة المستخدم*

اختر القسم:
/media - تحميل من الميديا
/ai - ذكاء اصطناعي
/files - إدارة الملفات
/tasks - التذكير والمهام
/services - خدمات سريعة
`, { parse_mode: "Markdown" });
});


// =========================
// 📥 قسم تحميل الميديا
// =========================

bot.onText(/\/media (.+)/, async (msg, match) => {
    const url = match[1];
    bot.sendMessage(msg.chat.id, "⏳ جاري التحميل...");

    try {
        // مثال API (ضع API حقيقي)
        const response = await axios.get(`https://api.example.com/download?url=${url}`);
        bot.sendMessage(msg.chat.id, `✅ رابط التحميل:\n${response.data.download}`);
    } catch (err) {
        bot.sendMessage(msg.chat.id, "❌ فشل التحميل");
    }
});


// =========================
// 🤖 قسم الذكاء الاصطناعي
// =========================

bot.onText(/\/ai (.+)/, async (msg, match) => {
    const prompt = match[1];

    try {
        // ضع API ذكاء اصطناعي حقيقي
        const response = await axios.post("https://api.example.com/ai", {
            prompt: prompt
        });

        bot.sendMessage(msg.chat.id, `🤖 الرد:\n${response.data.reply}`);
    } catch (err) {
        bot.sendMessage(msg.chat.id, "❌ خطأ في الذكاء الاصطناعي");
    }
});


// =========================
// 📂 قسم الملفات
// =========================

bot.onText(/\/files/, (msg) => {
    bot.sendMessage(msg.chat.id, "📂 أرسل أي ملف لحفظه في السيرفر");
});

bot.on("document", async (msg) => {
    const fileId = msg.document.file_id;
    const file = await bot.getFile(fileId);
    const fileUrl = `https://api.telegram.org/file/bot${token}/${file.file_path}`;

    const response = await axios({
        method: "GET",
        url: fileUrl,
        responseType: "stream"
    });

    response.data.pipe(fs.createWriteStream(`./${msg.document.file_name}`));
    bot.sendMessage(msg.chat.id, "✅ تم حفظ الملف");
});


// =========================
// ⏰ قسم التذكير والمهام
// =========================

bot.onText(/\/tasks/, (msg) => {
    bot.sendMessage(msg.chat.id, "اكتب:\n/addtask المهمة | بعد كم دقيقة");
});

bot.onText(/\/addtask (.+)/, (msg, match) => {
    const parts = match[1].split("|");
    const task = parts[0].trim();
    const minutes = parseInt(parts[1]);

    const time = new Date(Date.now() + minutes * 60000);

    schedule.scheduleJob(time, function(){
        bot.sendMessage(msg.chat.id, `⏰ تذكير:\n${task}`);
    });

    bot.sendMessage(msg.chat.id, "✅ تم إضافة التذكير");
});


// =========================
// ⚡ قسم الخدمات السريعة
// =========================

bot.onText(/\/services/, (msg) => {
    bot.sendMessage(msg.chat.id, `
⚡ خدمات سريعة:
/time - الوقت الحالي
/id - معرفة ID
`);
});

bot.onText(/\/time/, (msg) => {
    bot.sendMessage(msg.chat.id, `🕒 الوقت الآن:\n${new Date().toLocaleString()}`);
});

bot.onText(/\/id/, (msg) => {
    bot.sendMessage(msg.chat.id, `🆔 ID الخاص بك:\n${msg.from.id}`);
});