
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
    # Extraction de l'ID de la vidéo à partir de différents formats d'URL
    video_id = None
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
    elif "youtube.com/watch" in url and "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtube.com/shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]
    
    if not video_id:
        print(f"Impossible d'extraire l'ID de la vidéo depuis l'URL: {url}")
        return None
    
    print(f"ID vidéo extrait: {video_id}")
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"URL normalisée: {clean_url}")
    
    output_filename = f"{uuid.uuid4()}.mp4"
    
    # Configuration de base pour yt-dlp
    ydl_opts = {
        # Format progressif pour éviter la nécessité de fusion audio/vidéo
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': output_filename,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'verbose': True,
        'no_warnings': False,
        'ignoreerrors': True,
        'geo_bypass': True,
        'socket_timeout': 30,
        'nocheckcertificate': True,  # Ignorer les erreurs de certificat
        'prefer_insecure': True,     # Préférer les connexions non-sécurisées si nécessaire
        'extractor_retries': 5,      # Nombre de tentatives pour l'extraction
        'fragment_retries': 10,      # Nombre de tentatives pour le téléchargement de fragments
        'skip_unavailable_fragments': True,  # Ignorer les fragments non disponibles
        # Tenter de forcer IPv4 pour éviter les restrictions
        'source_address': '0.0.0.0', 
    }
    
    for attempt in range(3):  # Faire 3 tentatives avec différentes configurations
        try:
            print(f"Tentative {attempt+1} de téléchargement depuis: {clean_url}")
            
            # Ajuster les options en fonction de la tentative
            if attempt == 1:
                # Deuxième tentative: essayer un format plus bas
                ydl_opts['format'] = 'best[height<=480]/best'
            elif attempt == 2:
                # Troisième tentative: essayer le format le plus simple
                ydl_opts['format'] = 'best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Téléchargement avec options: {ydl_opts['format']}")
                # Télécharger directement sans vérification préalable des infos
                ydl.download([clean_url])
                
                # Vérifier si le fichier existe
                if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                    print(f"Téléchargement réussi: {output_filename}")
                    return output_filename
                else:
                    print(f"Le fichier {output_filename} n'existe pas ou est vide après la tentative {attempt+1}")
        
        except Exception as e:
            print(f"Erreur lors de la tentative {attempt+1}: {e}")
            # Continuer avec la prochaine tentative
    
    # Une dernière tentative avec YouTube-DL directement si toutes les autres ont échoué
    try:
        print("Dernière tentative avec une configuration alternative...")
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_filename,
            'noplaylist': True,
            'quiet': False,
            'verbose': True,
            'no_warnings': False,
            'ignoreerrors': True,
            'geo_bypass': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                print(f"Téléchargement réussi avec la configuration alternative: {output_filename}")
                return output_filename
    except Exception as e:
        print(f"Échec de la dernière tentative: {e}")
    
    # Si on arrive ici, toutes les tentatives ont échoué
    print("Toutes les tentatives de téléchargement ont échoué.")
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
    if data == "admin_announce":
        await Announcement.waiting_for_text.set()
        await bot.send_message(callback_query.from_user.id, "Envoyez le texte de l'annonce à diffuser.")
    elif data == "admin_manage_admins":
            # Demander à l'admin s'il veut ajouter ou supprimer un admin
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton("Ajouter un admin", callback_data="admin_add"),
                types.InlineKeyboardButton("Supprimer un admin", callback_data="admin_remove")
            )
            await bot.send_message(callback_query.from_user.id, "Choisissez une action :", reply_markup=keyboard)
        elif data == "admin_ban_user":
            await BanUser.waiting_for_ban_id.set()
            await bot.send_message(callback_query.from_user.id, "Envoyez l'ID de l'utilisateur à bannir.")
        elif data == "admin_unban_user":
            await UnbanUser.waiting_for_unban_id.set()
            await bot.send_message(callback_query.from_user.id, "Envoyez l'ID de l'utilisateur à débannir.")
        elif data == "admin_stats":
            stats = (
                f"Nombre d'utilisateurs: {len(subscribers)}\n"
                f"Nombre d'admins: {len(admin_ids)}\n"
                f"Nombre de bannis: {len(banned_users)}"
            )
            await bot.send_message(callback_query.from_user.id, stats)
        elif data == "admin_manage_formats":
            await bot.send_message(callback_query.from_user.id, "Fonction 'Gérer formats' à implémenter.")
        elif data == "admin_manage_links":
            await bot.send_message(callback_query.from_user.id, "Fonction 'Gérer liens' à implémenter.")
        elif data == "admin_storage":
            files = os.listdir('.')
            await bot.send_message(callback_query.from_user.id, f"Fichiers présents: {files}")
        elif data == "admin_clear_storage":
            count = 0
            for f in os.listdir('.'):
                if f.endswith(".mp4"):
                    os.remove(f)
                    count += 1
            await bot.send_message(callback_query.from_user.id, f"{count} fichiers supprimés.")
        elif data == "admin_edit_start":
            await EditStartMessage.waiting_for_new_message.set()
            await bot.send_message(callback_query.from_user.id, "Envoyez le nouveau message de démarrage.")
        elif data == "admin_manage_sub":
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton("Ajouter une chaîne", callback_data="sub_add"),
                types.InlineKeyboardButton("Supprimer une chaîne", callback_data="sub_remove")
            )
            await bot.send_message(callback_query.from_user.id, "Choisissez une action :", reply_markup=keyboard)
        elif data == "admin_manage_telegraph":
            await TelegraphImage.waiting_for_image.set()
            await bot.send_message(callback_query.from_user.id, "Envoyez l'image à uploader sur Telegraph.")
        await bot.answer_callback_query(callback_query.id)

    # Gestion de l'ajout/suppression d'admins
    @dp.callback_query_handler(lambda c: c.data in ["admin_add", "admin_remove"])
    async def process_admin_manage(callback_query: types.CallbackQuery):
        action = callback_query.data  # "admin_add" ou "admin_remove"
        await ManageAdmins.waiting_for_admin_id.set()
        if action == "admin_add":
            await bot.send_message(callback_query.from_user.id, "Envoyez l'ID de l'utilisateur à ajouter comme admin.")
            await dp.current_state(user=callback_query.from_user.id).update_data(action="add")
        else:
            await bot.send_message(callback_query.from_user.id, "Envoyez l'ID de l'utilisateur à supprimer des admins.")
            await dp.current_state(user=callback_query.from_user.id).update_data(action="remove")
        await bot.answer_callback_query(callback_query.id)

    @dp.message_handler(state=ManageAdmins.waiting_for_admin_id, content_types=types.ContentTypes.TEXT)
    async def manage_admins_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        action = data.get("action")
        try:
            admin_id = int(message.text)
            if action == "add":
                admin_ids.add(admin_id)
                await message.reply(f"Utilisateur {admin_id} ajouté comme admin.")
            elif action == "remove":
                if admin_id in admin_ids:
                    admin_ids.remove(admin_id)
                    await message.reply(f"Utilisateur {admin_id} supprimé des admins.")
                else:
                    await message.reply(f"Utilisateur {admin_id} n'est pas admin.")
        except Exception as e:
            await message.reply("ID invalide.")
        await state.finish()

    # Bannir un utilisateur
    @dp.message_handler(state=BanUser.waiting_for_ban_id, content_types=types.ContentTypes.TEXT)
    async def ban_user_handler(message: types.Message, state: FSMContext):
        try:
            user_id = int(message.text)
            banned_users.add(user_id)
            if user_id in subscribers:
                subscribers.remove(user_id)
            await message.reply(f"Utilisateur {user_id} banni.")
        except Exception as e:
            await message.reply("ID invalide.")
        await state.finish()

    # Débannir un utilisateur
    @dp.message_handler(state=UnbanUser.waiting_for_unban_id, content_types=types.ContentTypes.TEXT)
    async def unban_user_handler(message: types.Message, state: FSMContext):
        try:
            user_id = int(message.text)
            if user_id in banned_users:
                banned_users.remove(user_id)
                await message.reply(f"Utilisateur {user_id} débanni.")
            else:
                await message.reply("Cet utilisateur n'est pas banni.")
        except Exception as e:
            await message.reply("ID invalide.")
        await state.finish()

    # Modifier le message de démarrage
    @dp.message_handler(state=EditStartMessage.waiting_for_new_message, content_types=types.ContentTypes.TEXT)
    async def edit_start_message_handler(message: types.Message, state: FSMContext):
        global welcome_message
        welcome_message = message.text
        await message.reply("Message de démarrage mis à jour.")
        await state.finish()

    # Gestion de l'abonnement forcé
    @dp.callback_query_handler(lambda c: c.data in ["sub_add", "sub_remove"])
    async def process_sub_manage(callback_query: types.CallbackQuery):
        action = callback_query.data  # "sub_add" ou "sub_remove"
        await ManageSubChannels.waiting_for_channel_name.set()
        if action == "sub_add":
            await bot.send_message(callback_query.from_user.id, "Envoyez le nom de la chaîne (ex: @channel) à ajouter.")
            await dp.current_state(user=callback_query.from_user.id).update_data(action="add")
        else:
            await bot.send_message(callback_query.from_user.id, "Envoyez le nom de la chaîne (ex: @channel) à supprimer.")
            await dp.current_state(user=callback_query.from_user.id).update_data(action="remove")
        await bot.answer_callback_query(callback_query.id)

    @dp.message_handler(state=ManageSubChannels.waiting_for_channel_name, content_types=types.ContentTypes.TEXT)
    async def manage_sub_channel_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        action = data.get("action")
        channel_name = message.text.strip()
        if action == "add":
            if channel_name not in FORCE_SUB_CHANNELS:
                FORCE_SUB_CHANNELS.append(channel_name)
                await message.reply(f"Chaîne {channel_name} ajoutée à l'abonnement forcé.")
            else:
                await message.reply("Cette chaîne est déjà dans la liste.")
        else:
            if channel_name in FORCE_SUB_CHANNELS:
                FORCE_SUB_CHANNELS.remove(channel_name)
                await message.reply(f"Chaîne {channel_name} supprimée de l'abonnement forcé.")
            else:
                await message.reply("Cette chaîne n'est pas dans la liste.")
        await state.finish()

    # Upload d'image sur Telegraph
    @dp.message_handler(state=TelegraphImage.waiting_for_image, content_types=types.ContentTypes.PHOTO)
    async def telegraph_image_handler(message: types.Message, state: FSMContext):
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        file = await bot.download_file(file_path)
        temp_filename = f"{uuid.uuid4()}.jpg"
        with open(temp_filename, "wb") as f:
            f.write(file.getvalue())
        url = upload_image_to_telegraph(temp_filename)
        os.remove(temp_filename)
        if url:
            await message.reply(f"Image uploadée sur Telegraph : {url}")
        else:
            await message.reply("Erreur lors de l'upload sur Telegraph.")
        await state.finish()

    # Diffusion d'annonce à tous les abonnés
    @dp.message_handler(state=Announcement.waiting_for_text, content_types=types.ContentTypes.TEXT)
    async def announcement_handler(message: types.Message, state: FSMContext):
        announcement_text = message.text
        failed = 0
        for user_id in subscribers.copy():
            try:
                await bot.send_message(user_id, f"📢 Annonce :\n\n{announcement_text}")
            except Exception as e:
                print(f"Erreur lors de l'envoi à {user_id} : {e}")
                failed += 1
        await message.reply(f"Annonce envoyée à {len(subscribers) - failed} utilisateurs. ({failed} échecs)")
        await state.finish()

    # ------------------------

# -------------------------------
# Lancement du bot
# -------------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
