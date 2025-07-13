from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from config import BOT_TOKEN, CHANNEL_ID

TITLE, DESCRIPTION, PRICE, CITY, CONTACT, PHOTO, CONFIRM = range(7)
ads_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Įveskite skelbimo pavadinimą:")
    return TITLE

async def title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ads_data[update.effective_user.id] = {"title": update.message.text}
    await update.message.reply_text("✏️ Įveskite skelbimo aprašymą:")
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ads_data[update.effective_user.id]["description"] = update.message.text
    await update.message.reply_text("💶 Įveskite kainą (pvz. 10):")
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.replace('.', '', 1).isdigit():
        await update.message.reply_text("❌ Klaida! Įveskite kainą skaičiais.")
        return PRICE
    ads_data[update.effective_user.id]["price"] = update.message.text
    await update.message.reply_text("🏙️ Įrašykite miestą:")
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ads_data[update.effective_user.id]["city"] = update.message.text
    await update.message.reply_text("📞 Įrašykite kontaktą (tel. nr arba @username):")
    return CONTACT

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ads_data[update.effective_user.id]["contact"] = update.message.text
    await update.message.reply_text("📸 Atsiųskite nuotrauką:")
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file_id = update.message.photo[-1].file_id
    ads_data[update.effective_user.id]["photo"] = photo_file_id

    data = ads_data[update.effective_user.id]
    text = f"<b>{data['title']}</b>\n\n{data['description']}\n\n💶 Kaina: {data['price']} €\n🏙️ Miestas: {data['city']}\n📞 Kontaktai: {data['contact']}"

    keyboard = [
        [InlineKeyboardButton("✅ Skelbti", callback_data="post"),
         InlineKeyboardButton("❌ Atšaukti", callback_data="cancel")]
    ]

    await update.message.reply_photo(photo=photo_file_id, caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "post":
        data = ads_data[user_id]
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=data["photo"],
            caption=f"<b>{data['title']}</b>\n\n{data['description']}\n\n💶 Kaina: {data['price']} €\n🏙️ Miestas: {data['city']}\n📞 Kontaktai: {data['contact']}",
            parse_mode="HTML"
        )
        await query.edit_message_caption(caption="✅ Skelbimas išsiųstas!", parse_mode="HTML")
    else:
        await query.edit_message_caption(caption="❌ Skelbimas atšauktas.", parse_mode="HTML")
    return ConversationHandler.END

async def cancel_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔ Veiksmas nutrauktas.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            CONFIRM: [CallbackQueryHandler(confirm)]
        },
        fallbacks=[CommandHandler("cancel", cancel_all)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
