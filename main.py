
import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import yt_dlp
from telegraph import Telegraph
import asyncio

# -------------------------------
# Configuration
# -------------------------------
BOT_TOKEN = "7771993655:AAGfHswoXZXsZK3tnQg6-irxrWcjIYbjVwM"  # Remplace par ton token BotFather
ADMIN_IDS = [5116530698]  # Remplace par tes IDs admin
FORCE_SUB_CHANNELS = ["sineur_x_bot"]  # Remplace par le(s) nom(s) de ta(tes) chaîne(s)
WELCOME_IMAGE_URL = "https://graph.org/file/a832e964b6e04f82c1c75-7a8ca2206c069a333a.jpg"  # URL de ton image de bienvenue

# -------------------------------
# Initialisation du bot
# -------------------------------
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# -------------------------------
# Fonctions utilitaires
# -------------------------------
async def check_subscription(user_id: int) -> bool:
    """
    Vérifie si l'utilisateur est abonné aux chaînes obligatoires.
    """
    for channel in FORCE_SUB_CHANNELS:
        try:
            # Obtenir d'abord l'ID de la chaîne à partir du nom d'utilisateur
            chat = await bot.get_chat(f"@{channel}")
            member = await bot.get_chat_member(chat_id=chat.id, user_id=user_id)
            if member.status in ['left', 'kicked', 'banned']:
                # Créer un clavier avec un bouton pour rejoindre la chaîne
                keyboard = types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text="Rejoindre la chaîne", url=f"https://t.me/{channel}")]
                    ]
                )
                await bot.send_message(
                    user_id, 
                    f"Vous devez vous abonner à @{channel} pour utiliser ce bot.",
                    reply_markup=keyboard
                )
                return False
        except Exception as e:
            print("Erreur de vérification d'abonnement:", e)
            # Ne pas échouer silencieusement, indiquer l'erreur
            await bot.send_message(user_id, f"Erreur lors de la vérification d'abonnement: {e}")
            return False
    return True

def download_video(url: str) -> str:
    """
    Télécharge une vidéo YouTube et renvoie le chemin du fichier téléchargé.
    """
    # Nettoyage de l'URL (retrait des paramètres si/t qui peuvent poser problème)
    clean_url = url.split("?")[0] if "?" in url else url
    print(f"URL nettoyée: {clean_url}")
    
    output_filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        # Essayer différents formats en priorité décroissante
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,  # Ignorer les erreurs et continuer
        'verbose': True,
        # Ajouter des cookies pour les vidéos avec restrictions d'âge
        'cookiefile': None,
        # Contourner les géo-restrictions
        'geo_bypass': True,
        # Temps d'expiration des requêtes pour éviter les blocages
        'socket_timeout': 30,
    }
    
    try:
        print(f"Tentative de téléchargement depuis: {clean_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraire d'abord les informations pour vérifier si la vidéo est accessible
            info = ydl.extract_info(clean_url, download=False)
            if info:
                print(f"Vidéo trouvée: {info.get('title', 'Sans titre')}")
                # Télécharger la vidéo
                ydl.download([clean_url])
                
                # Vérifier si le fichier existe
                if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                    print(f"Téléchargement réussi: {output_filename}")
                    return output_filename
                else:
                    print(f"Le fichier {output_filename} n'existe pas ou est vide après téléchargement")
            else:
                print("Informations de la vidéo non disponibles")
        
        # Si on arrive ici, essayer avec une URL alternative (format court)
        if "youtu.be" in url or "youtube.com" in url:
            video_id = None
            if "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
            elif "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
            
            if video_id:
                alt_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Tentative avec URL alternative: {alt_url}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([alt_url])
                    if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                        print(f"Téléchargement réussi avec URL alternative: {output_filename}")
                        return output_filename
        
        return None
    except Exception as e:
        print(f"Erreur de téléchargement détaillée: {e}")
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
@dp.message(lambda message: message.text and message.text.startswith("/start"))
async def cmd_start(message: types.Message):
    # Vérifie l'abonnement forcé
    if not await check_subscription(message.from_user.id):
        await message.reply("Pour utiliser le bot, vous devez être abonné à notre chaîne.")
        return
    # Création du clavier inline
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Télécharger une vidéo", callback_data="download_video"),
                types.InlineKeyboardButton(text="Panneau Admin", callback_data="admin_panel")
            ]
        ]
    )
    # Envoi de l'image de bienvenue et du message
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=WELCOME_IMAGE_URL,
        caption=("Bienvenue sur notre bot de téléchargement de vidéos YouTube ! 📱\n\n"
                "Ce bot vous permet de télécharger facilement des vidéos depuis YouTube.\n\n"
                "✅ Téléchargement rapide\n"
                "✅ Haute qualité\n"
                "✅ Simple à utiliser\n\n"
                "Choisissez une option ci-dessous pour commencer :"),
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "download_video")
async def process_download_video(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "Envoie-moi le lien YouTube à télécharger.")

@dp.message(lambda message: message.text and (message.text.startswith("http") or "youtu" in message.text))
async def handle_video_link(message: types.Message):
    msg = await message.reply("Téléchargement en cours... Cela peut prendre quelques instants.")
    
    # Extraire l'URL YouTube
    url = message.text.strip()
    
    try:
        # Essayer de télécharger la vidéo
        await message.reply("Récupération des informations de la vidéo...")
        video_path = download_video(url)
        
        if video_path and os.path.exists(video_path):
            # Vérifier la taille du fichier
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # Taille en MB
            
            if file_size > 49:  # Telegram limite à 50MB
                await message.reply(f"⚠️ La vidéo est trop grande ({file_size:.1f}MB). Telegram limite les fichiers à 50MB.")
                os.remove(video_path)
            else:
                await message.reply(f"Envoi en cours... Taille: {file_size:.1f}MB")
                await bot.send_video(
                    message.chat.id, 
                    video=types.FSInputFile(video_path),
                    caption="Voici votre vidéo! 🎬"
                )
                await msg.delete()  # Supprimer le message "Téléchargement en cours"
                os.remove(video_path)
        else:
            await message.reply("⚠️ Impossible de télécharger cette vidéo. Vérifiez que l'URL est valide et que la vidéo est disponible.")
    except Exception as e:
        await message.reply(f"❌ Erreur: {str(e)[:200]}")
        print(f"Exception complète: {e}")

@dp.message(lambda message: message.text and message.text.startswith("/admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Vous n'êtes pas autorisé à utiliser cette commande.")
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Envoyer une annonce", callback_data="admin_announce")],
            [types.InlineKeyboardButton(text="Gérer les admins", callback_data="admin_manage_admins")],
            [types.InlineKeyboardButton(text="Bannir utilisateur", callback_data="admin_ban_user")],
            [types.InlineKeyboardButton(text="Débannir utilisateur", callback_data="admin_unban_user")],
            [types.InlineKeyboardButton(text="Voir statistiques", callback_data="admin_stats")],
            [types.InlineKeyboardButton(text="Gérer formats", callback_data="admin_manage_formats")],
            [types.InlineKeyboardButton(text="Gérer liens", callback_data="admin_manage_links")],
            [types.InlineKeyboardButton(text="Voir stockage", callback_data="admin_storage")],
            [types.InlineKeyboardButton(text="Vider stockage", callback_data="admin_clear_storage")],
            [types.InlineKeyboardButton(text="Modifier message démarrage", callback_data="admin_edit_start")],
            [types.InlineKeyboardButton(text="Gérer abonnement forcé", callback_data="admin_manage_sub")],
            [types.InlineKeyboardButton(text="Gérer images Telegraph", callback_data="admin_manage_telegraph")]
        ]
    )
    await message.answer("Panneau Admin :", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data and c.data.startswith("admin_"))
async def process_admin_callbacks(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer(text="Accès refusé.")
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
    await callback_query.answer()

# -------------------------------
# Lancement du bot
# -------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
