import constants as keys
from telegram import Bot
from telegram.ext import *
from cs50 import SQL

print("Bot started!")

#define /start command
def start_command(update, context):
    update.message.reply_text("Hi there, I'm NBA Stat Bot!")

#define /help command
def help_command(update, context):
    update.message.reply_text("Start the comparison using /compare, and then input the names of the two players one by one!")

#define states for the conversation
FIRST_PLAYER, SECOND_PLAYER = range(2)
#start conversation
def start_compare(update, context):
    #extract the first player's name
    update.message.reply_text("Tell me the first player's name!")
    return FIRST_PLAYER

#define function to get the first name
def get_first_name(update, context):
    #save first name into user_data dict
    context.user_data['player1'] = update.message.text
    player1 = context.user_data['player1']
    #ask for second name
    update.message.reply_text(f"you entered {player1}, now tell me the second player's name!")
    return SECOND_PLAYER

#define function to get second name
def get_second_name(update, context):
    #save second name into user_data dict
    context.user_data['player2'] = update.message.text
    player1 = context.user_data['player1']
    player2 = context.user_data['player2']

    db = SQL("sqlite:///nba.db")

    try:
        #sql stuff
        player1_db = db.execute("SELECT * FROM stats WHERE Player LIKE ?", player1)[0]
        player2_db = db.execute("SELECT * FROM stats WHERE Player LIKE ?", player2)[0]

        #hm
        pts1 = player1_db['PTS']
        pts2 = player2_db['PTS']
        ast1 = player1_db['AST']
        ast2 = player2_db['AST']
        reb1 = player1_db['TRB']
        reb2 = player2_db['TRB']

        fg1 = round((player1_db['FG%']*100), 2)
        fg2 = round((player2_db['FG%']*100), 2)
        threept1 = round((player1_db['3P%']*100), 2)
        threept2 = round((player2_db['3P%']*100), 2)
        ft1 = round((player1_db['FT%']*100), 2)
        ft2 = round((player2_db['FT%']*100), 2)

        #draft message
        message = f"{player1_db['Player']} vs {player2_db['Player']}:\n"

        #compare and bold the stats
        if pts1 > pts2:
            message += f"Points per game: <b>{pts1}</b> vs {pts2}\n"
        else:
            message += f"Points per game: {pts1} vs <b>{pts2}</b>\n"

        if ast1 > ast2:
            message += f"Assists per game: <b>{ast1}</b> vs {ast2}\n"
        else:
            message += f"Assists per game: {ast1} vs <b>{ast2}</b>\n"

        if reb1 > reb2:
            message += f"Rebounds per game: <b>{reb1}</b> vs {reb2}\n"
        else:
            message += f"Rebounds per game: {reb1} vs <b>{reb2}</b>\n"

        if fg1 > fg2:
            message += f"Field goal percentage: <b>{fg1}%</b> vs {fg2}%\n"
        else:
            message += f"Field goal percentage: {fg1}% vs <b>{fg2}%</b>\n"

        if threept1 > threept2:
            message += f"Three-point percentage: <b>{threept1}%</b> vs {threept2}%\n"
        else:
            message += f"Three-point percentage: {threept1}% vs <b>{threept2}%</b>\n"

        if ft1 > ft2:
            message += f"Free throw percentage: <b>{ft1}%</b> vs {ft2}%\n"
        else:
            message += f"Free throw percentage: {ft1}% vs <b>{ft2}%</b>\n"


        update.message.reply_text(message, parse_mode='HTML')

        #end the convo
        return ConversationHandler.END

    except:
        update.message.reply_text("Players not found! Please try again using /compare. :(")
        return ConversationHandler.END

# Define the function to handle conversation cancellation
def cancel(update, context):
    update.message.reply_text("Okay, the comparison has been cancelled.")
    return ConversationHandler.END

def cancel_command(update, context):
    update.message.reply_text("Okay, the comparison has been cancelled.")
    return ConversationHandler.END

def error(update, context):
    print(f"Update {update} caused error {context.error}")

#define main function
def main():
    updater = Updater(keys.token, use_context=True)
    dp = updater.dispatcher

    #command handlers
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("cancel", cancel_command))

    #Create the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('compare', start_compare)],
        states={
            FIRST_PLAYER: [MessageHandler(Filters.text, get_first_name)],
            SECOND_PLAYER: [MessageHandler(Filters.text, get_second_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)



    updater.start_polling()
    updater.idle()

main()
