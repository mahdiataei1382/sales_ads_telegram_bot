import logging
from uuid import uuid4
from telegram import Update , InlineQueryResultAudio
from telegram.ext import Application, CommandHandler, ContextTypes , MessageHandler , ConversationHandler , filters , InlineQueryHandler
import json
TOKEN = "7181380651:AAHuojuYyXPoZCcwIDb0Q6kpgZrj7rd883A"

logging.basicConfig(format="%(asctime)s - %(name)s - % (levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

admins = [408345002]
AUdio = 0
SONGER = 1
NAME = 2
file = open('music_data.json' , 'r')
musics = json.load(file)
file.close()

async def add_aduio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in admins:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="فایل اهنگ رو ارسال کن",
        )
        return AUdio

    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="شما دسترسی ندارید",
        )
        return add_music.END


async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.effective_message.audio.file_id
    context.user_data['file_id'] = file_id
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اسم خواننده رو بفرست",
    )
    return SONGER


async def send_songer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songer = update.effective_message.text
    context.user_data['songer'] = songer
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اسم اهنگ رو بفرست",
    )
    return NAME


async def send_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    music = {'file_id': context.user_data['file_id'], 'songer': context.user_data['songer'], 'name': name}
    musics.append(music)
    file = open('music_data.json','w')
    json.dump(musics , file)
    file.close()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='اهنگ اضافه شد',
    )
    return add_music.END


async def cancel_command_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = "اضافه کردن اهنگ کنسل شد"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )
    return add_music.END


async def serach_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text
    for music in musics:
        if music['name'] == name:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=music['file_id']
            )
            return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="not found"
    )


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=("""به بات اهنگهای بانو هایده خوش آمدید
دانلود موزیک ها /music
دانلود موزیک ویدیو /musicvideo
را کلیک کنید"""))


async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""لیست موزیک ها:
اهنگ شب عشق > /shabeshg
اهنگ اشاره > /eshare
اهنگ وای به حالش > /vaybehalesh
اهنگ ای زندگی سلام > /eyzendegisalam
اهنگ پریشون > /parishoon
اهنگ سال> /sal
اهنگ بهانه > /bahaneh
اهنگ عالم یکرنگی > /alamyekrangi
اهنگ راوی > /ravi
اهنگ گل سنگ > /golsang""")


async def musicvideo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""لیست موزیک ویدیو ها:
اهنگ شب عشق > /shabeshgv
اهنگ اشاره > /esharev
اهنگ وای به حالش > /vaybehaleshv
اهنگ ای زندگی سلام > /eyzendegisalamv
اهنگ پریشون > /parishonv
اهنگ سال> /salv
اهنگ شهر آشوب > /shahreashobv
اهنگ عالم یکرنگی > /alamyekrangiv
اهنگ راوی > /ravi
اهنگ گل سنگ > /golsangv""")

async def inline_query_handler( update : Update , context: ContextTypes.DEFAULT_TYPE) :
    query = update.inline_query.query
    results = []
    if not query:
        for music in musics:
            result = InlineQueryResultAudio(
                id=str(uuid4()),
                audio_url=music['file_id'],
                title=music['name']
            )
            results.append(result)

    else :
        for music in musics :
            if music['name'] == query :
                result = InlineQueryResultAudio(
                    id= str(uuid4()) ,
                    audio_url= music['file_id'] ,
                    title= music['name']
                )
                results.append(result)
    await update.inline_query.answer(results)

if __name__ == "__main__":
    bot = Application.builder().token(TOKEN).build()
    add_music = ConversationHandler(entry_points=[CommandHandler("add_audio", add_aduio_handler)], states={
        AUdio: [MessageHandler(filters.AUDIO, send_audio)],
        SONGER: [MessageHandler(filters.TEXT, send_songer)],
        NAME: [MessageHandler(filters.TEXT, send_name)], },
                                    fallbacks=[CommandHandler("cancel", cancel_command_handler), ], )
    bot.add_handler(add_music)
    bot.add_handler(InlineQueryHandler(inline_query_handler))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, serach_music))
    bot.add_handler(CommandHandler('start', start_handler))
    bot.add_handler(CommandHandler('music', music_handler))
    bot.add_handler(CommandHandler('musicvideo', musicvideo_handler))
    bot.run_polling()


