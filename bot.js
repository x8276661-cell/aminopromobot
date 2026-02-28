const fs = require("fs");
const readline = require("readline");

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question("اكتب اسم الملف مع الامتداد: ", function(filename) {
    rl.question("اكتب الكود/النص:\n", function(content) {
        fs.writeFile(filename, content, (err) => {
            if (err) console.log("❌ خطأ في الحفظ:", err);
            else console.log("✅ تم حفظ الملف بنجاح:", filename);
            rl.close();
        });
    });
});