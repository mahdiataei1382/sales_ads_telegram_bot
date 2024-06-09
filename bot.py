from typing import Final

from telegram import (
    Update,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    InlineQueryHandler,
)

from mongo_client import AdsMongoClient

BOT_TOKEN: Final = "6559276107:AAGYkl2Mqc6LC3uLVY4UQa4h6RVcImOvjxs"

CATEGORY, PHOTO, DESCRIPTION = range(3)
# db connection
db_client = AdsMongoClient("localhost", 27017)
# add your user ids here, you can use @userinfobot to get your user id
# DO NOT REMOVE EXISTING IDs
dev_ids = [92129627, 987654321 , 408345002]


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام، من ربات ثبت آگهی هستم. برای قبت آگهی جدید از دستور /add_advertising استفاده کنید.",
        reply_to_message_id=update.effective_message.id,
    )


async def add_category_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.effective_user.id in dev_ids :
        category = ""
        for word in context.args:
            category = category + word + " "
        category = category[:-1]
        db_client.add_category(category)
        text  = f"دسته بندی {category} با موفقیت اضافه شد."
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id
        )

    else :
        text = "شما اجازه دسترسی به این دستور را ندارید."
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id
        )


async def add_advertising_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    categories = db_client.get_categories()
    text = "لطفا از بین دسته بندی های زیر یکی را انتخاب کنید:\n" + "\n".join(categories)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )
    return CATEGORY


async def choice_category_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["category"] = update.effective_message.text
    text = "لطفا عکس آگهی خود را ارسال کنید."
    await context.bot.send_message(
        chat_id= update.effective_chat.id ,
        text = text ,
        reply_to_message_id= update.effective_message.id
    )
    return PHOTO


async def photo_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["photo_url"] = update.effective_message.photo[-1].file_id
    text = "لطفا توضیحات آگهی خود را وارد کنید. در توضیحات می توانید اطلاعاتی مانند قیمت، شماره تماس و ... را وارد کنید."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )
    return DESCRIPTION

async def description_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    description = update.effective_message.text
    user_id = int(update.effective_user.id)
    photo_url = str(context.user_data["photo_url"])
    category = str(context.user_data["category"])
    db_client.add_advertising(user_id=user_id , photo_url=str(photo_url) , category=category , description=description)
    text = "آگهی شما با موفقیت ثبت شد."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )
    return ConversationHandler.END


async def cancel_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    text = "عملیات ثبت آگهی لغو شد. برای ثبت آگهی جدید از دستور /add_category استفاده کنید."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )
    return ConversationHandler.END

async def my_ads_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ads = db_client.get_user_ads(update.effective_user.id)
    if ads==[]:
       text =  "شما هیچ آگهی ثبت نکرده‌اید."
       await context.bot.send_message(
           chat_id=update.effective_chat.id ,
           text = text ,
           reply_to_message_id=update.effective_message.id
       )
    else :
        for ad in ads :
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=ad["photo_url"],
                caption=ad["description"] + f"\n\n" + "برای حذف آگهی از دستور زیر استفاده کنید." + "\n\n" + f"/delete_ad {ad['id']}",
                reply_to_message_id=update.effective_message.id,
            )

async def delete_ad_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ad_id = context.args[0]
    db_client.delete_advertising(update.effective_user.id , ad_id)
    text = "آگهی با موفقیت حذف شد."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.effective_message.id
    )

async def search_ads_by_category_inline_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    category = update.inline_query.query
    ads = db_client.get_ads_by_category(category=category)
    results = []
    for ad in ads :
        result = InlineQueryResultPhoto(
            id = ad["id"] ,
            title=ad["description"] ,
            photo_url=ad["photo_url"] ,
            thumbnail_url=ad["photo_url"],
            caption=ad["description"],
        )
        results.append(result)

    await context.bot.answer_inline_query(update.inline_query.id , results)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("add_category", add_category_command_handler))
    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("add_advertising", add_advertising_command_handler)
            ],
            states={
                CATEGORY: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, choice_category_message_handler
                    )
                ],
                PHOTO: [
                    MessageHandler(filters.PHOTO, photo_message_handler),
                ],
                DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, description_message_handler
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )
    )
    app.add_handler(CommandHandler("delete_ad" , delete_ad_command_handler))
    app.add_handler(CommandHandler("my_ads", my_ads_command_handler))
    app.add_handler(InlineQueryHandler(search_ads_by_category_inline_query))
    app.run_polling()
