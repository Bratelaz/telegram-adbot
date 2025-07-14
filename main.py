
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes
from db import init_db, save_ad, get_ads_by_user, delete_ad

BOT_TOKEN = "JŪSŲ_BOT_TOKEN_CIA"
ADMIN_ID = 123456789  # <- Pakeisk į savo Telegram ID

TITLE, DESCRIPTION, PRICE, CITY, CONTACT, PHOTO, CONFIRM = range(7)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Dėti skelbimą", callback_data="add_ad")],
        [InlineKeyboardButton("🗂 Mano skelbimai", callback_data="my_ads")]
    ]
    await update.message.reply_text("👋 Sveiki! Ką norėtumėte daryti?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_ad":
        await query.message.reply_text("📝 Įveskite skelbimo pavadinimą:")
        return TITLE
    elif query.data == "my_ads":
        ads = get_ads_by_user(query.from_user.id)
        if not ads:
            await query.edit_message_text("❌ Jūs dar neturite skelbimų.")
            return
        buttons = []
        for ad in ads:
            buttons.append([
                InlineKeyboardButton(f"{ad[1]} – {ad[2]}€", callback_data=f"view_{ad[0]}"),
                InlineKeyboardButton("❌ Ištrinti", callback_data=f"del_{ad[0]}")
            ])
        await query.edit_message_text("🗂 Jūsų skelbimai:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("del_"):
        ad_id = int(query.data.split("_")[1])
        delete_ad(ad_id, query.from_user.id)
        await query.edit_message_text("🗑️ Skelbimas ištrintas.")

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"title": update.message.text}
    await update.message.reply_text("📝 Įveskite skelbimo aprašymą:")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id]["description"] = update.message.text
    await update.message.reply_text("💶 Įveskite <b>kainą</b>:", parse_mode="HTML")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id]["price"] = update.message.text
    await update.message.reply_text("🏙️ Įveskite <b>miestą</b>:", parse_mode="HTML")
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id]["city"] = update.message.text
    await update.message.reply_text("📞 Įveskite <b>kontaktą</b>:", parse_mode="HTML")
    return CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id]["contact"] = update.message.text
    await update.message.reply_text("📸 Įkelkite <b>nuotrauką</b>:", parse_mode="HTML")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    data = user_data[update.effective_user.id]
    data["photo_id"] = photo_id

    preview = f"<b>{data['title']}</b>\n\n<b>Aprašymas:</b> {data['description']}\n<b>Kaina:</b> {data['price']} €\n<b>Miestas:</b> {data['city']}\n<b>Kontaktas:</b> {data['contact']}"
    keyboard = [[
        InlineKeyboardButton("✅ Patvirtinti", callback_data="confirm_ad"),
        InlineKeyboardButton("❌ Atmesti", callback_data="cancel_ad")
    ]]

    await update.message.reply_photo(photo=photo_id, caption=preview, parse_mode="HTML")
    await context.bot.send_message(chat_id=ADMIN_ID, text="📬 Naujas skelbimas gautas:

" + preview,
                                   reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_ad":
        data = list(user_data.values())[-1]
        save_ad(ADMIN_ID, data['title'], data['description'], data['price'],
                data['city'], data['contact'], data['photo_id'])
        await query.edit_message_text("✅ Skelbimas patvirtintas ir išsaugotas.")
    elif query.data == "cancel_ad":
        await query.edit_message_text("❌ Skelbimas atmestas.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Veiksmas nutrauktas.")
    return ConversationHandler.END

if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="add_ad")],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler, pattern="my_ads|del_\d+|view_\d+"))
    app.add_handler(CallbackQueryHandler(confirm_handler, pattern="confirm_ad|cancel_ad"))
    app.run_polling()
