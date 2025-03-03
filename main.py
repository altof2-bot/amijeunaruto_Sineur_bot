import logging
import os
import uuid
from aiogram import Bot, Dispatcher, executor, types
import yt_dlp
from telegraph import Telegraph

# -------------------------------
# Configuration
# -------------------------------
BOT_TOKEN = "7771993655:AAGfHswoXZXsZK3tnQg6-irxrWcjIYbjVwM"         # Remplace par ton token BotFather
ADMIN_IDS = [5116530698]                   # Remplace par tes IDs admin
FORCE_SUB_CHANNELS = ["sineur_x_bot"]     # Remplace par le(s) nom(s) de ta(tes) chaîne(s)
WELCOME_IMAGE_URL = "https://graph.org/file/a832e964b6e04f82c1c75-7a8ca2206c069a333a.jpg/welcome.jpg"  # URL de ton image de bienvenue

# -------------------------------
# Initialisation du bot
# -------------------------------
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# -------------------------------
# Fonctions utilitaires
# -------------------------------
async def check_subscription(message: types.Message) -> bool:
    """
    Vérifie si l'utilisateur est abonné aux chaînes obligatoires.
    """
    for channel in FORCE_SUB_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=message.from_user.id)
            if member.status == 'left':
                return False
        except Exception as e:
            print("Erreur de vérification d'abonnement:", e)
            return False
    return True

def download_video(url: str) -> str:
    """
    Télécharge une vidéo YouTube et renvoie le chemin du fichier téléchargé.
    """
    output_filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_filename,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_filename
    except Exception as e:
        print("Erreur de téléchargement:", e)
        return None

def upload_image_to_telegraph(file_path: str) -> str:
    """
    Upload une image sur Telegraph et renvoie l'URL.
    """
    telegraph = Telegraph()
    telegraph.create_account(short_name="bot")
    try:
        with open(file_path, 'rb') as f:
            response = telegraph.upload_file(f)
        if isinstance(response, list) and len(response) > 0:
            return "https://telegra.ph" + response[0]['src']
        else:
            return None
    except Exception as e:
        print("Erreur lors de l'upload sur Telegraph:", e)
        return None

def is_admin(user_id: int) -> bool:
    """
    Vérifie si l'utilisateur est dans la liste des admins.
    """
    return user_id in ADMIN_IDS

# -------------------------------
# Handlers du bot
# -------------------------------
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    # Vérifie l'abonnement forcé
    if not await check_subscription(message):
        await message.reply("Pour utiliser le bot, vous devez être abonné à notre chaîne.")
        return
    # Création du clavier inline
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Télécharger une vidéo", callback_data="download_video"),
        types.InlineKeyboardButton("Panneau Admin", callback_data="admin_panel")
    )
    # Envoi de l'image de bienvenue et du message
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=WELCOME_IMAGE_URL,
        caption="Bienvenue sur le bot ! Choisissez une option :",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "download_video")
async def process_download_video(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Envoie-moi le lien YouTube à télécharger.")

@dp.message_handler(lambda message: message.text and message.text.startswith("http"))
async def handle_video_link(message: types.Message):
    msg = await message.reply("Téléchargement en cours...")
    video_path = download_video(message.text)
    if video_path:
        await bot.send_video(message.chat.id, open(video_path, "rb"))
        os.remove(video_path)
    else:
        await message.reply("Erreur lors du téléchargement de la vidéo.")

@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Vous n'êtes pas autorisé à utiliser cette commande.")
        return
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Envoyer une annonce", callback_data="admin_announce"),
        types.InlineKeyboardButton("Gérer les admins", callback_data="admin_manage_admins"),
        types.InlineKeyboardButton("Bannir utilisateur", callback_data="admin_ban_user"),
        types.InlineKeyboardButton("Débannir utilisateur", callback_data="admin_unban_user"),
        types.InlineKeyboardButton("Voir statistiques", callback_data="admin_stats"),
        types.InlineKeyboardButton("Gérer formats", callback_data="admin_manage_formats"),
        types.InlineKeyboardButton("Gérer liens", callback_data="admin_manage_links"),
        types.InlineKeyboardButton("Voir stockage", callback_data="admin_storage"),
        types.InlineKeyboardButton("Vider stockage", callback_data="admin_clear_storage"),
        types.InlineKeyboardButton("Modifier message démarrage", callback_data="admin_edit_start"),
        types.InlineKeyboardButton("Gérer abonnement forcé", callback_data="admin_manage_sub"),
        types.InlineKeyboardButton("Gérer images Telegraph", callback_data="admin_manage_telegraph")
    )
    await message.answer("Panneau Admin :", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("admin_"))
async def process_admin_callbacks(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await bot.answer_callback_query(callback_query.id, text="Accès refusé.")
        return

    data = callback_query.data
    response_text = ""
    if data == "admin_announce":
        response_text = "Fonction 'Envoyer une annonce' à implémenter."
    elif data == "admin_manage_admins":
        response_text = "Fonction 'Gérer les admins' à implémenter."
    elif data == "admin_ban_user":
        response_text = "Fonction 'Bannir utilisateur' à implémenter."
    elif data == "admin_unban_user":
        response_text = "Fonction 'Débannir utilisateur' à implémenter."
    elif data == "admin_stats":
        response_text = "Fonction 'Voir statistiques' à implémenter."
    elif data == "admin_manage_formats":
        response_text = "Fonction 'Gérer formats' à implémenter."
    elif data == "admin_manage_links":
        response_text = "Fonction 'Gérer liens' à implémenter."
    elif data == "admin_storage":
        response_text = "Fonction 'Voir stockage' à implémenter."
    elif data == "admin_clear_storage":
        response_text = "Fonction 'Vider stockage' à implémenter."
    elif data == "admin_edit_start":
        response_text = "Fonction 'Modifier message démarrage' à implémenter."
    elif data == "admin_manage_sub":
        response_text = "Fonction 'Gérer abonnement forcé' à implémenter."
    elif data == "admin_manage_telegraph":
        response_text = "Fonction 'Gérer images Telegraph' à implémenter."
    else:
        response_text = "Action inconnue."
    await bot.send_message(callback_query.from_user.id, response_text)
    await bot.answer_callback_query(callback_query.id)

# -------------------------------
# Lancement du bot
# -------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)