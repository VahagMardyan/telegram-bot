from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

async def start_bot(update,context):
    dialog.mode = "main"
    text_message = load_message("main_en")
    await send_photo(update,context,name="main")
    await send_text(update,context,text_message)
    await send_text_buttons(update,context,"Would you like to start ?",{
        "start":"Start Bot",
        "stop":"Stop Bot",
    })
    await show_main_menu(update,context,{
        "start":"Main bot menu.",
        "profile":"generation of Tinder profile 😎",
        "opener":"message for acquaintance 🥰",
        "message":"correspondence on your behalf 😈",
        "date":"correspondence with stars 🔥",
        "gpt":"Communication with AI (ChatGPT)",
    })

async def gpt_bot(update,context):
    dialog.mode = "gpt"
    text = load_message("gpt_en")
    await send_photo(update,context,"gpt")
    await send_text(update=update,context=context,text=text)

async def gpt_dialog(update,context):
    text = update.message.text
    prompt = load_prompt("gpt_en")
    answer = await chatgpt.send_question(prompt,text)
    await send_text(update,context,answer)

async def date(update,context):
    dialog.mode = "date"
    text = load_message("date_en")
    await send_photo(update,context,"date")
    await send_text_buttons(update,context,text,{
        "date_grande":"Ariana Grande",
        "date_robbie":"Margot Robbie",
        "date_zendaya":"Zendaya",
        "date_gosling":"Ryan Gosling",
        "date_hardy":"Tom Hardy",
    })

async def date_dialog(update,context):
    text = update.message.text
    my_message = await send_text(update,context,"He/She is typing...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date_button(update,context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update,context,query)
    await send_text(update,context,f"Good choice!")

    prompt = load_prompt(f"{query}_en")
    chatgpt.set_prompt(prompt)

async def message(update,context):
    dialog.mode = "message"
    text = load_message("message_en")
    await send_photo(update,context,"message")
    await send_text_buttons(update,context,text,{
        "message_next":"Next message",
        "message_date":"Invite on a date",
    })
    dialog.list.clear()

async def message_button(update,context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(f"{query}_en")
    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(update,context,"ChatGPT is thinking...")
    
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def message_dialog(update,context):
    text = update.message.text
    dialog.list.append(text)

async def profile(update,context):
    dialog.mode = "profile"
    text = load_message("profile_en")
    await send_photo(update,context,"profile")
    await send_text(update,context,text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update,context,"How old are you?")

async def profile_dialog(update,context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update,context,"What kind of work do you do?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update,context,"Do you have any hobbies?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update,context,"What do you NOT like about people?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update,context,"What is your purpose in dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile_en")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update,context,"ChatGPT is generating profile for you...")

        answer = await chatgpt.send_question(prompt,user_info)
        await my_message.edit_text(answer)
    
async def opener(update,context):
    dialog.mode = "opener"
    text = load_message("opener_en")
    await send_photo(update,context,"opener")
    await send_text(update,context,text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update,context,"What is her name?")

async def opener_dialog(update,context):
    text = update.message.text
    dialog.count += 1
    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update,context,"How old is she?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update,context,"Rate her appearance: 1-10 points")
    elif dialog.count == 3:
        dialog.user["beauty"] = text
        await send_text(update,context,"Who does she work for?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update,context,"What is purpose in dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("opener_en")
        user_info = dialog_user_info_to_str(dialog.user)
        
        my_message = await send_text(update,context,"ChatGPT is thinking...")

        answer = await chatgpt.send_question(prompt,user_info)
        await my_message.edit_text(answer)

async def bot_messages(update,context):
    if dialog.mode == "gpt":
        await gpt_dialog(update,context)
    elif dialog.mode == "date":
        await date_dialog(update,context)
    elif dialog.mode == "message":
        await message_dialog(update,context)
    elif dialog.mode == "profile":
        await profile_dialog(update,context)
    elif dialog.mode == "opener":
        await opener_dialog(update,context)
    else:
        await send_text(update,context,f"You have written: {update.message.text}")

async def bot_buttons(update,context):
    query = update.callback_query.data
    if query == "start":
        await send_text(update,context,"Bot started.")
    else:
        await send_text(update,context,"OK, I won't start the process:)")

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

chatgpt = ChatGptService(token="YOUR-CHATGPT-TOKEN")

app = ApplicationBuilder().token("YOUR-TELEGRAM-BOT-TOKEN").build()
app.add_handler(CommandHandler("start",start_bot))
app.add_handler(CommandHandler("gpt",gpt_bot))
app.add_handler(CommandHandler("date",date))
app.add_handler(CommandHandler("message",message))
app.add_handler(CommandHandler("profile",profile))
app.add_handler(CommandHandler("opener",opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,bot_messages))
app.add_handler(CallbackQueryHandler(date_button,pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button,pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(bot_buttons))

app.run_polling()