import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, Application, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from datetime import datetime
# Remplace par ton vrai token
TOKEN =7593371180:AAHDOrLB5GebjIxFGiI0JZNv84-jc5kSVzA
# Nom du fichier pour sauvegarder les données
DATA_FILE = "data.json"

# Charger les données depuis le fichier JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Erreur lors du chargement des données. Fichier JSON corrompu.")
                return {}
    return {}

# Sauvegarder les données dans le fichier JSON
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
CREATOR_ID = 1687928453 5116530698  # ID du créateur
players = {}
# Variables des joueurs et autres données
players = {"referrals", "money", "exp"}
teams = {}  # Dictionnaire pour stocker les équipes
# Joueurs préenregistrés (exemples)
# Joueurs préenregistrés (exemples)
players = {
    123456: {"name": "Joueur1", "health": 100, "attack": 20, "level": 1, "exp": 1000, "money": 50, "referrals": [], "is_example": True},
    654321: {"name": "Joueur2", "health": 100, "attack": 20, "level": 1, "exp": 100, "money": 50, "referrals": [], "is_example": True},
}

# Dictionnaire pour stocker les participants du tournoi
tournoi_participants = []  # Liste pour suivre les participants au tournoi

# Demandes en attente
pending_requests = {}

villages = ['Konoha', 'Suna', 'Kiri', 'Iwa', 'Kumo']
clans = ['Uchiha', 'Hyuga', 'Senju', 'Nara', 'Akimichi', 'Yamanaka', 'Aburame', 'Inuzuka', 'Uzumaki']

jutsus = {
    'Uchiha': ['Sharingan', 'Kaléidoscoptique du sharigan', 'Susanoo', 'Rinngan'],
    'Hyuga': ['Byakugan', 'Gentle Fist', 'Eight Trigrams Palms'],
    'Senju': ['Mokuton'],
    'Nara': ['Kage Mane no Jutsu'],
    'Akimichi': ['Baika no Jutsu', 'Multi-Size Technique'],
    'Yamanaka': ['Shintenshin no Jutsu'],
    'Aburame': ['Kikaichū no Jutsu'],
    'Inuzuka': ['Ninjutsu de l\'Inuzuka'],
    'Uzumaki': ['Fūinjutsu', 'Rasengan', 'Rasen Shuriken']
}

missions = [
    {"name": "Mission de reconnaissance", "exp": 100, "money": 50, "difficulty": 1},
    {"name": "Assassinat d'un ennemi", "exp": 200, "money": 100, "difficulty": 2},
    {"name": "Protéger le village", "exp": 300, "money": 150, "difficulty": 3},
    {"name": "Infiltration d'un camp ennemi", "exp": 400, "money": 200, "difficulty": 4},
    {"name": "Combat contre un ninja légendaire", "exp": 500, "money": 500, "difficulty": 5}
]

# Commande /start avec photo et boutons
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    # Ajouter le joueur dans la base de données (si non existant)
    if user_id not in players:
        players[user_id] = {
            'name': user.first_name,
            'username': f"@{user.username}" if user.username else "Inconnu",
            'level': 1,
            'exp': 0,
            'money': 100,
            'village': None,
            'clan': None,
            'health': 100,
            'attack': 20,
            'team': None,
            'inventory': [],
            'referrals': [],
            'parrainage_done': False  # Ajout d'une clé pour savoir si le parrainage a déjà été effectué
        }

    # Vérification du parrainage
    inviter_id = None
    if len(update.message.text.split(' ')) > 1:
        inviter_id = int(update.message.text.split(' ')[1])

    # Message de bienvenue
    message = (
        f"Bienvenue {user.first_name} dans l'univers de Naruto ! 🌸\n"
        "Choisis ton village pour commencer ton aventure.\n"
        "Utilise /village <nom du village> pour choisir un village."
    )
    
    # Vérifier si un parrain est fourni et si ce parrain existe dans la base de données
    if inviter_id and inviter_id in players:
        # Vérifier si l'utilisateur a déjà été parrainé par ce parrain
        if user_id not in players[inviter_id]['referrals']:
            # Si le parrain n'a pas encore reçu la récompense pour ce joueur
            if not players[user_id].get('parrainage_done', False):
                # Ajouter le nouvel utilisateur à la liste des parrainages du parrain
                players[inviter_id]['referrals'].append(user_id)

                # Récompenses pour le parrain
                players[inviter_id]['money'] += 500
                players[inviter_id]['exp'] += 500

                # Marquer que le parrainage a été effectué pour cet utilisateur
                players[user_id]['parrainage_done'] = True

                # Notification au parrain
                inviter_message = (
                    f"🎉 {user.first_name} (@{user.username if user.username else 'Inconnu'}) "
                    "a rejoint grâce à ton lien !\n"
                    "💰 Tu gagnes 500¥ et 🌟 500 EXP !"
                )
                await context.bot.send_message(chat_id=inviter_id, text=inviter_message)
        else:
            # Si l'utilisateur a déjà été parrainé par ce parrain
            await update.message.reply_text(f"Tu as déjà été parrainé par {players[inviter_id]['name']} ! 🎉")

    # Configuration du clavier
    keyboard = [
        [
            InlineKeyboardButton("📑 SUPPORT 📑", callback_data="support_info"),
            InlineKeyboardButton("🤖 MISE À JOUR 🤖", callback_data="update_info"),
        ],
        [
            InlineKeyboardButton("🧑‍💻 DÉVELOPPEUR 🧑‍💻", callback_data="developer_info"),
            InlineKeyboardButton("🕵 CRÉATEUR 🕵", callback_data="creator_info"),
        ],
        [
            InlineKeyboardButton("📜 MES COMMANDES 📜", callback_data="user_commands"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
async def send_welcome_photo(update, context, message, reply_markup):
    # Envoyer la photo avec le message de bienvenue
    photo_message = await update.message.reply_photo(
        photo="https://graph.org/file/d8b62cc81e674cd0f6139-e598b58f88bfa8f1a8.jpg",  # URL directe de l'image
        caption=message,
        reply_markup=reply_markup
    )

    # Assigner l'ID du message de bienvenue
    context.chat_data["welcome_message_id"] = photo_message.message_id

# Fonction pour gérer les interactions des boutons
async def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Contenu à afficher en fonction du bouton cliqué
    if query.data == "support_info":
        caption = "📑 **SUPPORT** 📑\n\nVoici le lien vers notre support : Clique ici(https://t.me/GameFrenchSupport)"
    elif query.data == "update_info":
        caption = "🤖 **MISE À JOUR** 🤖\n\nConsultez les dernières mises à jour ici : Clique ici(https://t.me/GameFrench)"
    elif query.data == "developer_info":
        caption = (
            "🧑‍💻 **DÉVELOPPEUR** 🧑‍💻\n\n"
            "- Nom : 𝐍𝐄𝐓𝐅𝐋𝐀𝐒𝐇 𝐃𝐈𝐄𝐔 𝐌𝐀𝐔𝐑𝐈𝐂𝐄\n"
            "- Contact : @mauridieu\n"
            "- ID : 1687928453\n\n"
            "- HEBERGER SUR @REQUETE_ANIME_30sbot Merci d'utiliser ce bot ! 🚀"
        )
    elif query.data == "creator_info":
        caption = "🕵 **CRÉATEUR** 🕵\n\nDécouvrez le créateur ici : Clique ici(https://t.me/GameFrench)"
    elif query.data == "user_commands":
        caption = (
            "📜 **MES COMMANDES** 📜\n\n"
            "/start - Commencer l'aventure\n"
            "/village - Choisir un village\n"
            "/clan - Choisir un clan\n"
            "/mission - Démarrer une mission\n"
            "/inventory - Voir votre inventaire\n"
            "/profile - Voir votre profil\n"
            "/jutsu - Utiliser un jutsu\n"
            "/shop - Accéder à la boutique\n"
            "/buy - Acheter un objet\n"
            "/utiliser - Utiliser un objet\n"
            "/pvp - Combattre un autre joueur\n"
            "/top_player - Voir les meilleurs joueurs\n"
            "/equipe - Gérer votre équipe\n"
            "/donner - Donner un objet\n"
            "/bonus - Recevoir un bonus\n"
            "/entrainement - S'entraîner pour améliorer vos compétences\n"
            "/inviter - Inviter un ami\n"
            "/mission_du_ninja_legendaire - Mission légendaire\n"
            "/tournoi - Participer à un tournoi\n"
            "/quitter_tournoi - Quitter un tournoi\n\n"
            "🔹 Explorez ces commandes et amusez-vous bien ! 🎮"
        )
    elif query.data == "back_to_welcome":
        caption = (
            "Bienvenue à nouveau dans l'univers de Naruto ! 🌸\n"
            "Choisis ton village pour commencer ton aventure.\n"
            "Utilise /village <nom du village> pour choisir un village."
        )
    else:
        caption = "Option non reconnue. Veuillez réessayer."

    # Ajouter un bouton "Retour" sauf pour l'écran d'accueil
    if query.data != "back_to_welcome":
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="back_to_welcome")]]
    else:
        keyboard = [
            [
                InlineKeyboardButton("📑 SUPPORT 📑", callback_data="support_info"),
                InlineKeyboardButton("🤖 MISE À JOUR 🤖", callback_data="update_info"),
            ],
            [
                InlineKeyboardButton("🧑‍💻 DÉVELOPPEUR 🧑‍💻", callback_data="developer_info"),
                InlineKeyboardButton("🕵 CRÉATEUR 🕵", callback_data="creator_info"),
            ],
            [
                InlineKeyboardButton("📜 MES COMMANDES 📜", callback_data="user_commands"),
            ],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Modifier la légende du message de bienvenue
    message_id = context.chat_data.get("welcome_message_id")
    if message_id:
        await query.message.edit_caption(caption=caption, reply_markup=reply_markup)

# Choisir le village
async def choose_village(update: Update, context) -> None:
    user = update.message.from_user
    village = ' '.join(context.args)

    if village not in villages:
        await update.message.reply_text(f"Village invalide. Choisis un village parmi : {', '.join(villages)} essaye de commencer par la lettre majuscule 🚫")
        return

    players[user.id]['village'] = village

    message = f"Tu as choisi le village {village} 🌟.\nMaintenant, choisis ton clan ! Utilise /clan <nom du clan> pour choisir."
    
    await update.message.reply_text(message)

# Choisir la classe
async def choose_clan(update: Update, context) -> None:
    user = update.message.from_user
    cls = ' '.join(context.args)

    if cls not in clans:
        await update.message.reply_text(f"Clan invalide. Choisis un clan parmi : {', '.join(clans)} essaye de commencer par la lettre majuscule 🚫")
        return

    players[user.id]['clan'] = cls
    players[user.id]['health'] = 100  # Réinitialisation de la santé

    message = f"Tu as choisi le clan {cls} 🥷.\nTu es prêt à commencer ta première mission ! Utilise /mission pour commencer ta mission."
    
    await update.message.reply_text(message)

async def start_mission(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifier si le joueur est enregistré
    if user_id not in players:
        await update.message.reply_text("Tu n'es pas encore enregistré. Utilise la commande /start pour commencer.")
        return

    # Vérifier si le joueur est en mode Dieu
    if players[user_id].get('is_god_mode', False):
        # Mode Dieu : succès automatique avec récompenses maximales
        mission = random.choice(missions)
        exp_gain = mission["exp"] * 2  # Récompenses doublées
        money_gain = mission["money"] * 2

        players[user_id]['exp'] += exp_gain
        players[user_id]['money'] += money_gain
        players[user_id]['health'] = 999999999  # Santé infinie (par sécurité)

        message = (
            f"Mission réussie (Mode Dieu) ! 🎉\n"
            f"Tu as gagné {exp_gain} EXP et {money_gain} ¥.\n"
            "Santé et ressources infinies garanties. 😇"
        )

        # Ajouter un objet spécial dans l'inventaire (optionnel)
        special_item = "Artefact divin"
        if special_item not in players[user_id]['inventory']:
            players[user_id]['inventory'].append(special_item)
            message += f"\nObjet bonus : {special_item} 🛡️."

        await update.message.reply_text(message)

        # Mettre à jour le niveau
        level_message = level_up(user_id)
        if level_message:
            await update.message.reply_text(level_message)
        return

    # Mode normal
    # Vérifier si le joueur a assez de santé
    if players[user_id]['health'] <= 0:
        await update.message.reply_text("Tu es trop faible pour commencer une mission. Va récupérer de la santé. 🛌")
        return

    # Sélectionner une mission aléatoire
    mission = random.choice(missions)

    # Vérifier si le joueur a un boost de jutsu
    boost = players[user_id].get('mission_boost', 0)
    success_chance = 50 + boost  # Chance de base de 50% augmentée par le boost

    # Déterminer le résultat de la mission
    mission_result = "succès" if random.randint(1, 100) <= success_chance else "échec"

    # Réinitialiser le boost après la mission
    players[user_id]['mission_boost'] = 0

    if mission_result == "succès":
        # Récompenses pour une mission réussie
        players[user_id]['exp'] += mission["exp"]
        players[user_id]['money'] += mission["money"]

        message = f"Mission réussie ! 🎉\nTu as gagné {mission['exp']} EXP et {mission['money']} ¥."

        # Chance d'obtenir un objet en bonus
        if random.choice([True, False]):
            item = random.choice(["Shuriken", "Kunai", "Ramen", "Onigiri", "Bandage de soin", "Vêtement de ninja"])
            players[user_id]['inventory'].append(item)
            message += f"\nTu as trouvé un objet : {item} 🛒."
    else:
        # Pénalité pour une mission échouée
        players[user_id]['health'] -= 0
        if players[user_id]['health'] <= 0:
            players[user_id]['health'] = 0
            message = "Mission échouée et tu es tombé au combat ! 🛌 Tu as besoin de soins."
        else:
            message = "Mission échouée ! Tente ta chance prochainement 😓."

    await update.message.reply_text(message)

    # Mise à jour du niveau du joueur
    level_message = level_up(user_id)
    if level_message:
        await update.message.reply_text(level_message)

    # Offre une nouvelle mission
    await update.message.reply_text(message)

# Fonction pour gérer les niveaux et augmenter les points de vie
def level_up(user_id):
    player = players[user_id]
    if player['exp'] >= player['level'] * 500:  # Exemple : 500 EXP pour passer au niveau suivant
        player['level'] += 1
        player['exp'] = 0  # Reset EXP après niveau up
        player['health'] = 100 + (player['level'] * 20)  # Augmenter la santé de 20 points à chaque niveau
        message = f"Félicitations ! Tu as atteint le niveau {player['level']} ! 🎉 Tu as maintenant {player['health']} points de vie."
        return message
    return ""

# Fonction pour afficher le profil
async def profile(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    player = players[user_id]
    message = f"Profil de {player['name']} (ID: {user_id}) :\n\n" \
              f"🎮 Nom: {player['name']}\n" \
              f"🎯 Niveau: {player['level']}\n" \
              f"💎 EXP: {player['exp']}\n" \
              f"💰 Argent: {player['money']} ¥\n" \
              f"❤️ Santé: {player['health']}\n" \
              f"🌍 Village: {player['village']}\n" \
              f"🥷 Clan: {player['clan']}\n\n" \
              "Rappelle-toi, même les ninjas ont besoin de se reposer parfois ! 🛌"
    
    await update.message.reply_text(message)

# Fonction pour afficher l'inventaire
async def inventory(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    if not players[user_id]['inventory']:
        await update.message.reply_text("Ton inventaire est vide. Peut-être que tu devrais faire plus de missions ou en acheter des objets. 😅")
        return

    items = "\n".join(players[user_id]['inventory'])
    await update.message.reply_text(f"Ton inventaire :\n{items} 🎁")

# Fonction pour utiliser un jutsu
async def use_jutsu(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifier si le joueur a choisi une classe
    if players[user_id]['clan'] is None:
        await update.message.reply_text("Tu dois d'abord choisir ton clan avant d'utiliser un jutsu. 😅")
        return

    # Liste des jutsus par classe (exemple)
    jutsu_list = jutsus[players[user_id]['clan']]
    jutsu = random.choice(jutsu_list)  # Sélection aléatoire d'un jutsu

    # Appliquer un effet temporaire d'amélioration
    players[user_id]['mission_boost'] = 20  # Boost temporaire de réussite (+20% de chance)
    players[user_id]['jutsu_used'] = jutsu  # Sauvegarder le jutsu utilisé

    # Réduction de santé en contrepartie
    players[user_id]['health'] -= 10  # Coût en santé pour utiliser un jutsu

    # Vérifier si le joueur meurt après l'utilisation du jutsu
    if players[user_id]['health'] <= 0:
        players[user_id]['health'] = 0
        message = f"Tu as utilisé le jutsu : {jutsu} ! Mais tu es tombé au combat... Va récupérer de la santé. 🛌"
    else:
        message = f"Tu as utilisé le jutsu : {jutsu} ! Tes chances de réussir ta prochaine mission sont augmentées. 🔥"

    await update.message.reply_text(message)

# Fonction pour afficher la boutique
async def shop(update: Update, context) -> None:
    message = "Bienvenue dans la boutique ! 🛍️\nVoici les objets disponibles à l'achat :\n" \
              "- Shuriken (50 ¥) 🌀\n" \
              "- Kunai (30 ¥) 🔪\n" \
              "- Vêtement de ninja (150 ¥) 👕\n" \
              "- Bandage de soin (200 ¥) 🩹\n" \
              "- Medicament de kiri (1500 ¥) 💊\n"\
              "- Senbei (100 ¥) 🍘\n" \
              "- Narutomaki (150 ¥) 🍥\n" \
              "- Riz cuit (100 ¥) 🍚\n" \
              "- Bento (200 ¥) 🍱\n" \
              "- Ramen (950 ¥) 🍜\n" \
              "- Curry japonais (300 ¥) 🍛\n" \
              "- Hamburger (500 ¥) 🍔\n" \
              "- Onigiri (120 ¥) 🍙"

    await update.message.reply_text(message)

# Fonction pour acheter des objets
async def buy_item(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id
    item = ' '.join(context.args)
    prices = {
        "Shuriken": 50, "Kunai": 30, "Vêtement de ninja": 150, "Bandage de soin": 200, "Medicament de kiri": 1500,
        "Senbei": 100, "Narutomaki": 150, "Riz cuit": 100, "Bento": 200, 
        "Ramen": 250, "Curry japonais": 300, "Hamburger": 500, "Onigiri": 120
    }

    if item not in prices:
        await update.message.reply_text("Objet invalide. Choisis un objet valide à acheter. 💸")
        return

    price = prices[item]
    if players[user_id]['money'] < price:
        await update.message.reply_text(f"Tu n'as pas assez d'argent pour acheter {item}. 😭")
        return

    players[user_id]['money'] -= price
    players[user_id]['inventory'].append(item)
    await update.message.reply_text(f"Tu as acheté {item} pour {price} ¥ ! 🎉")
# Commande pour utiliser un objet
async def utiliser(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifier si un objet a été spécifié
    if len(context.args) == 0:
        await update.message.reply_text("Veuillez spécifier un objet à utiliser. Exemple : /utiliser Narutomaki")
        return

    # Récupérer le nom exact de l'objet tel que spécifié par l'utilisateur
    objet = ' '.join(context.args)

    # Liste des objets avec leurs effets
    objets_effets = {
        "Shuriken": {"pv": 0, "exp": 500},
        "Kunai": {"pv": 0, "exp": 250},
        "Vêtement de ninja": {"pv": 50, "exp": 300},
        "Bandage de soin": {"pv": 100, "exp": 0},
        "Medicament de kiri": {"pv": 1000, "exp": 0},
        "Senbei": {"pv": 10, "exp": 50},
        "Narutomaki": {"pv": 20, "exp": 50},
        "Riz cuit": {"pv": 30, "exp": 60},
        "Bento": {"pv": 40, "exp": 70},
        "Ramen": {"pv": 200, "exp": 800},
        "Curry japonais": {"pv": 80, "exp": 80},
        "Hamburger": {"pv": 40, "exp": 25},
        "Onigiri": {"pv": 60, "exp": 10},
    }

    # Vérifier si l'utilisateur possède cet objet dans son inventaire
    if objet not in players[user_id]['inventory']:
        await update.message.reply_text(f"Tu ne possèdes pas {objet} dans ton inventaire.")
        return

    # Vérifier si l'objet est valide
    if objet not in objets_effets:
        await update.message.reply_text(f"L'objet '{objet}' n'existe pas ou ne peut pas être utilisé.")
        return

    # Récupérer les effets de l'objet
    effet = objets_effets[objet]
    gain_pv = effet["pv"]
    gain_exp = effet["exp"]

    # Appliquer les effets au joueur
    players[user_id]['health'] += gain_pv
    players[user_id]['exp'] += gain_exp

    # Retirer l'objet de l'inventaire
    players[user_id]['inventory'].remove(objet)

    # Message de confirmation
    message = f"Vous avez utilisé {objet} !\n"
    if gain_pv > 0:
        message += f"❤️ Points de vie récupérés : {gain_pv}\n"
    if gain_exp > 0:
        message += f"🌟 Points d'expérience gagnés : {gain_exp}"

    await update.message.reply_text(message)
# Commande /pvp
async def pvp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    # Si l'utilisateur a une demande en attente
    if user_id in pending_requests:
        # Vérifier si une réponse est fournie
        if len(context.args) == 0:
            await update.message.reply_text(
                "Tu as une demande de combat en attente ! Réponds avec /pvp accepte ou /pvp refuse."
            )
            return

        # Récupérer l'initiateur du combat
        challenger_id = pending_requests[user_id]
        response = context.args[0].lower()

        if response == "accepte":
            # Commencer le combat
            await update.message.reply_text("Tu as accepté le combat ! Que le duel commence.")
            await context.bot.send_message(
                challenger_id,
                f"{players[user_id]['name']} a accepté le combat ! Le duel commence.",
            )
            await simulate_pvp(challenger_id, user_id, context)
        elif response == "refuse":
            # Refuser le combat
            await update.message.reply_text("Tu as refusé le combat.")
            await context.bot.send_message(
                challenger_id, f"{players[user_id]['name']} a refusé le combat."
            )
        else:
            await update.message.reply_text(
                "Réponse invalide. Utilise /pvp accepte ou /pvp refuse."
            )

        # Supprimer la demande en attente
        del pending_requests[user_id]
        return

    # Si l'utilisateur initie une nouvelle demande de PvP
    if len(context.args) == 0:
        await update.message.reply_text("Utilise la commande comme ceci : /pvp <ID de l'utilisateur cible>.")
        return

    # Récupérer l'ID de l'adversaire
    try:
        enemy_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("L'ID doit être un nombre valide.")
        return

    # Vérifier si l'utilisateur ciblé existe
    if enemy_id not in players:
        await update.message.reply_text("Le joueur spécifié n'existe pas parce que il n'a pas démarré le bot.")
        return

    # Empêcher un joueur de se battre contre lui-même
    if user_id == enemy_id:
        await update.message.reply_text("Tu ne peux pas te battre contre toi-même !")
        return

    # Vérifier si une demande est déjà en attente
    if enemy_id in pending_requests:
        await update.message.reply_text("Ce joueur a déjà une demande de combat en attente.")
        return

    # Enregistrer la demande de combat
    pending_requests[enemy_id] = user_id

    # Informer l'utilisateur ciblé
    await context.bot.send_message(
        chat_id=enemy_id,
        text=f"{players[user_id]['name']} te défie en duel !\nRéponds avec /pvp accepte ou /pvp refuse.",
    )
    await update.message.reply_text("Demande de combat envoyée !")

# Fonction pour simuler un combat PvP
async def simulate_pvp(challenger_id: int, defender_id: int, context: ContextTypes.DEFAULT_TYPE):
    challenger = players[challenger_id]
    defender = players[defender_id]

    # Vérifier que toutes les clés nécessaires existent
    required_keys = ["health", "attack", "name"]
    for player, player_id in [(challenger, challenger_id), (defender, defender_id)]:
        for key in required_keys:
            if key not in player:
                await context.bot.send_message(
                    chat_id=player_id,
                    text=f"Erreur : La clé '{key}' est manquante pour le joueur {player['name']}."
                )
                return

    # Calculer les dégâts infligés
    challenger_damage = random.randint(10, challenger["attack"])
    defender_damage = random.randint(10, defender["attack"])

    # Réduire les points de vie
    challenger["health"] -= defender_damage
    defender["health"] -= challenger_damage

    # Déterminer le résultat du combat
    if challenger["health"] <= 0 and defender["health"] <= 0:
        result = "Le combat est nul ! Les deux joueurs sont à terre. 💀"
        challenger["health"], defender["health"] = 0, 0
    elif challenger["health"] <= 0:
        result = f"{defender['name']} a gagné le combat contre {challenger['name']} ! 🎉"
        defender["exp"] += 100
        defender["money"] += 50
        challenger["health"] = 0
    elif defender["health"] <= 0:
        result = f"{challenger['name']} a gagné le combat contre {defender['name']} ! 🎉"
        challenger["exp"] += 100
        challenger["money"] += 50
        defender["health"] = 0
    else:
        result = (
            f"⚔️ Résultat du combat :\n"
            f"{challenger['name']} a infligé {challenger_damage} dégâts.\n"
            f"{defender['name']} a infligé {defender_damage} dégâts.\n\n"
            f"Statistiques restantes :\n"
            f"{challenger['name']} - Santé : {challenger['health']} ❤️\n"
            f"{defender['name']} - Santé : {defender['health']} ❤️"
        )

    # Envoyer le résultat aux deux joueurs
    await context.bot.send_message(challenger_id, result)
    await context.bot.send_message(defender_id, result)
# Commande /top_player pour afficher uniquement les vrais joueurs
async def top_player(update: Update, context: CallbackContext) -> None:
    # Filtrer pour exclure les joueurs d'exemple
    vrais_joueurs = {
        user_id: data for user_id, data in players.items() if not data.get("is_example", False)
    }

    if not vrais_joueurs:
        await update.message.reply_text("Aucun joueur enregistré pour le moment. 🫤")
        return

    # Trier les joueurs par niveau et expérience
    classement = sorted(
        vrais_joueurs.items(),
        key=lambda x: (x[1]['level'], x[1]['exp']),
        reverse=True
    )

    # Construire le message du classement
    message = "🏆 Classement des meilleurs joueurs 🏆\n"
    for rank, (user_id, data) in enumerate(classement, start=1):
        username = data.get("username", "Inconnu")
        name = data.get("name", "Anonyme")
        message += (
            f"{rank}. {username} ({name})\n"
            f"   Niveau : {data['level']}, EXP : {data['exp']}, ¥ : {data['money']}\n"
        )

    await update.message.reply_text(message)
async def equipe(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Si aucune commande spécifique n'est donnée, afficher les informations de l'équipe
    if len(context.args) == 0:
        for sensei_id, team in teams.items():
            if user_id == sensei_id or user_id in team['members']:
                members = [f"👨‍🏫 Sensei: @{team['sensei']} (ID: {team['sensei_id']})"]
                members += [f"- 🥷 @{players[member]['username'] or 'Inconnu'} (ID: {member})" for member in team['members']]
                await update.message.reply_text(
                    f"🔱 Informations de l'équipe :\n"
                    f"🏷️ Nom de l'équipe : {team['name']}\n"
                    f"👥 Membres :\n" + "\n".join(members)
                )
                return

        await update.message.reply_text("❌ Tu ne fais partie d'aucune équipe. Utilise /equipe create <nom de l'équipe> pour en créer. ⚔️")
        return

    command = context.args[0]

    if command == "create":
        # Créer une équipe
        if players[user_id]['level'] < 1000:
            await update.message.reply_text("⚠️ Tu dois être au niveau 1000 pour créer une équipe.")
            return

        if user_id in teams:
            await update.message.reply_text("⚠️ Tu as déjà créé une équipe.")
            return

        team_name = " ".join(context.args[1:]) if len(context.args) > 1 else f"Équipe de {user.first_name}"
        teams[user_id] = {
            "sensei": user.username or "Inconnu",
            "sensei_id": user_id,
            "name": team_name,
            "members": []
        }
        await update.message.reply_text(f"✅ Équipe '{team_name}' créée avec succès ! 🎉")
        return

    elif command.isdigit():
        # Ajouter un membre à l'équipe
        target_id = int(command)
        if user_id not in teams:
            await update.message.reply_text("⚠️ Tu n'as pas encore créé d'équipe.")
            return

        team = teams[user_id]
        if len(team['members']) >= 4:  # Limite des membres (3 max)
            await update.message.reply_text("⚠️ Ton équipe est déjà complète (4 membres max).")
            return

        if target_id in team['members']:
            await update.message.reply_text("⚠️ Ce joueur est déjà dans ton équipe.")
            return

        if target_id == user_id:
            await update.message.reply_text("⚠️ Tu ne peux pas t'ajouter toi-même à ton équipe.")
            return

        if target_id not in players:
            await update.message.reply_text("⚠️ Ce joueur n'est pas enregistré dans le jeu.")
            return

        # Ajouter le joueur à l'équipe
        team['members'].append(target_id)
        await update.message.reply_text(f"✅ Le joueur @{players[target_id]['username'] or 'Inconnu'} a été ajouté à l'équipe.")

        # Envoyer un message au joueur ajouté
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"👋 Tu as été ajouté à l'équipe '{team['name']}' par @{user.username or 'Inconnu'}.\n"
                     f"Utilise /equipe pour consulter les informations de l'équipe. 🔱"
            )
        except Exception:
            await update.message.reply_text("⚠️ Impossible de notifier ce joueur. Peut-être qu'il n'a pas démarré le bot.")
        return

    elif command == "quit":
        # Quitter l'équipe
        for sensei_id, team in teams.items():
            if user_id in team['members']:
                team['members'].remove(user_id)
                await update.message.reply_text("🚶 Tu as quitté l'équipe.")
                return

        await update.message.reply_text("⚠️ Tu ne peut toi même quitter ton équipe.")
        return

    else:
        await update.message.reply_text(
            "❌ Commande invalide. Voici ce que tu peux faire :\n"
            "- /equipe create <nom> : Créer une équipe.\n"
            "- /equipe <ID utilisateur> : Ajouter un joueur à ton équipe.\n"
            "- /equipe quit : Quitter l'équipe."
        )
async def donner(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifier les arguments
    if len(context.args) < 3:
        await update.message.reply_text("Usage : /donner <argent|objet> <montant/objet> <ID joueur>")
        return

    type_don = context.args[0].lower()
    cible_id = context.args[2]

    # Vérifier si l'ID cible est un entier valide
    try:
        cible_id = int(cible_id)
    except ValueError:
        await update.message.reply_text("L'ID du joueur doit être un nombre valide.")
        return

    # Vérifier si la cible existe
    if cible_id not in players:
        await update.message.reply_text("Le joueur spécifié n'existe pas. 🚫")
        return

    # Empêcher de se donner à soi-même
    if user_id == cible_id:
        await update.message.reply_text("Tu ne peux pas te donner quelque chose à toi-même. 🚫")
        return

    if type_don == "argent":
        try:
            montant = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Le montant doit être un nombre valide.")
            return

        # Vérifier si l'utilisateur a assez d'argent
        if players[user_id]['money'] < montant:
            await update.message.reply_text("Tu n'as pas assez d'argent pour effectuer ce don. 💸")
            return

        # Effectuer le transfert
        players[user_id]['money'] -= montant
        players[cible_id]['money'] += montant

        # Informer les deux joueurs
        await update.message.reply_text(f"✅ Tu as donné {montant} ¥ à {players[cible_id]['username']} ! 💰")
        await context.bot.send_message(
            chat_id=cible_id,
            text=f"🎉 {players[user_id]['username']} t'a donné {montant} ¥ ! 💰"
        )

    elif type_don == "objet":
        objet = context.args[1]

        # Vérifier si l'utilisateur possède l'objet
        if objet not in players[user_id]['inventory']:
            await update.message.reply_text("Tu ne possèdes pas cet objet. 🎒")
            return

        # Effectuer le transfert
        players[user_id]['inventory'].remove(objet)
        players[cible_id]['inventory'].append(objet)

        # Informer les deux joueurs
        await update.message.reply_text(f"✅ Tu as donné {objet} à {players[cible_id]['username']} ! 🎁")
        await context.bot.send_message(
            chat_id=cible_id,
            text=f"🎉 {players[user_id]['username']} t'a donné un objet : {objet} ! 🎁"
        )

    else:
        await update.message.reply_text("Type de don invalide. Utilise 'argent' ou 'objet'.")
        # Commande pour réclamer un bonus quotidien
# Commande pour récupérer un bonus quotidien
async def bonus(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifier si l'utilisateur est enregistré
    if user_id not in players:
        await update.message.reply_text(
            "Tu n'es pas encore enregistré ! Utilise la commande /start pour commencer ton aventure. 🌟"
        )
        return

    # Vérifier si l'utilisateur a déjà reçu son bonus
    last_bonus = players[user_id].get('last_bonus', None)
    current_time = datetime.now()

    if last_bonus:
        time_diff = current_time - last_bonus
        if time_diff.total_seconds() < 86400:  # 24 heures = 86400 secondes
            remaining_time = 86400 - time_diff.total_seconds()
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            await update.message.reply_text(
                f"Tu as déjà récupéré ton bonus aujourd'hui ! ⏳ Reviens dans {hours}h {minutes}min pour un nouveau bonus. 💎"
            )
            return

    # Accorder le bonus et mettre à jour le temps
    bonus_money = 500
    bonus_exp = 100
    players[user_id]['money'] += bonus_money
    players[user_id]['exp'] += bonus_exp
    players[user_id]['last_bonus'] = current_time

    await update.message.reply_text(
        f"🎁 Bonus quotidien récupéré !\n"
        f"💰 Argent : +{bonus_money}¥\n"
        f"🌟 EXP : +{bonus_exp}\n"
        f"Reviens demain pour un nouveau bonus ! 🎉"
    )
    # Commande d'entraînement
async def entrainement(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    if players[user_id]['money'] < 10:
        await update.message.reply_text("Tu n'as pas assez d'argent pour t'entraîner. Il te faut 10 ¥. 🏋️")
        return

    players[user_id]['money'] -= 50
    players[user_id]['exp'] += 100
    await update.message.reply_text("🏋️ Tu t'es entraîné avec 10¥ et tu as gagné 100 EXP ! Continue à progresser.")
    # Commande pour inviter des amis
async def inviter(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    lien_invitation = f"https://t.me/MondeDeNinjasBot?start={user_id}"
    message = f"🎉 Invite tes amis et gagne 500 ¥ et 500 EXP par personne invitée !\nVoici ton lien d'invitation :\n{lien_invitation}"
    await update.message.reply_text(message)
# Commande pour effectuer une mission ninja légendaire
async def mission_ninja_legendaire(update: Update, context) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérification du niveau minimal requis
    if players[user_id]['level'] < 1000:
        await update.message.reply_text("Tu dois être au moins niveau 1000 pour effectuer une mission ninja légendaire. 💪")
        return

    # Vérification de la santé minimale
    if players[user_id]['health'] <= 0:
        await update.message.reply_text("Tu es trop faible pour accomplir cette mission. Va récupérer de la santé. 🛌")
        return

    # Réussite ou échec de la mission (probabilité de succès plus élevée)
    mission_result = random.choices(["succès", "échec"], weights=[70, 30], k=1)[0]

    if mission_result == "succès":
        # Récompenses de la mission
        exp_gagne = 5000
        argent_gagne = 10000
        players[user_id]['exp'] += exp_gagne
        players[user_id]['money'] += argent_gagne

        # Calcul total des niveaux gagnés et santé
        niveaux_gagnes = players[user_id]['exp'] // 500
        players[user_id]['level'] += niveaux_gagnes
        players[user_id]['exp'] %= 500  # Garder l'EXP restante après montée de niveau
        sante_totale_gagnee = 20 * niveaux_gagnes
        players[user_id]['health'] += sante_totale_gagnee

        # Message de succès
        message = (
            f"Bravo ! 🌟 Tu as réussi une mission ninja légendaire.\n"
            f"🎁 Récompenses totales : 5000 EXP et 10000 ¥.\n"
        )

        if niveaux_gagnes > 0:
            message += (
                f"🎉 Félicitations ! Tu as gagné {niveaux_gagnes} niveau(x) supplémentaire(s), "
                f"atteignant le niveau {players[user_id]['level']}.\n"
                f"❤️ Ta santé a augmenté de {sante_totale_gagnee} points."
            )

        await update.message.reply_text(message)

    else:
        # Message en cas d'échec
        await update.message.reply_text(
            "La mission a échoué... 😓 Tu devras encore t'entraîner avant d'affronter de tels défis."
        )
        # Fonction pour calculer la montée de niveau
def update_level_and_health(player):
    while player['exp'] >= 500:
        player['exp'] -= 500  # Retirer 500 EXP pour chaque niveau gagné
        player['level'] += 1  # Augmenter le niveau
        player['health'] += 20  # Ajouter 20 points de santé

async def tournoi(update: Update, context) -> None:
    global tournoi_participants  # Utilisation de la variable globale
    user = update.message.from_user
    user_id = user.id

    # Vérifie si le joueur est déjà inscrit
    if user_id in tournoi_participants:
        await update.message.reply_text("Vous êtes déjà inscrit au tournoi ! ⏳")
        return

    # Ajoute le joueur à la liste des participants
    tournoi_participants.append(user_id)
    await update.message.reply_text("Vous êtes inscrit au tournoi ! 🏆")

    # Vérifie si le tournoi peut démarrer
    if len(tournoi_participants) == 4:  # Limite fixée à 4 joueurs
        await update.message.reply_text("Le tournoi commence maintenant ! 🎉")

        # Exécute le combat (simulé) et détermine un gagnant
        combats = []
        for i in range(3):  # Il y aura 3 combats pour simuler un mini tournoi
            combattant1, combattant2 = random.sample(tournoi_participants, 2)
            vainqueur = random.choice([combattant1, combattant2])
            perdant = combattant1 if vainqueur == combattant2 else combattant2
            combats.append((vainqueur, perdant))

            # Retire les perdants pour avancer dans le tournoi
            tournoi_participants.remove(perdant)

            # Informe tous les participants des résultats intermédiaires
            for participant in tournoi_participants + [perdant]:
                await context.bot.send_message(
                    chat_id=participant,
                    text=f"Combat {i+1} terminé :\n{context.bot_data[combattant1]} 🆚 {context.bot_data[combattant2]}\n"
                         f"🏆 Vainqueur : {context.bot_data[vainqueur]}\n❌ Perdant : {context.bot_data[perdant]}"
                )

        # Il reste un seul vainqueur à la fin
        gagnant = tournoi_participants[0]
        tournoi_participants.clear()  # Réinitialise la liste pour le prochain tournoi

        # Récompense le gagnant
        players[gagnant]['exp'] += 1000
        players[gagnant]['money'] += 5000

        # Gère l'augmentation de niveau et de santé
        while players[gagnant]['exp'] >= 500:
            players[gagnant]['level'] += 1
            players[gagnant]['exp'] -= 500
            players[gagnant]['health'] += 20

        # Message final pour tous les participants
        for participant in context.bot_data.keys():
            await context.bot.send_message(
                chat_id=participant,
                text=f"Le tournoi est terminé ! 🎉\n🏆 Vainqueur : {context.bot_data[gagnant]}\n"
                     f"+1000 EXP et +5000 ¥ pour le gagnant !"
            )
    else:
        await update.message.reply_text(f"Le tournoi démarre lorsque 4 joueurs sont inscrits. ({len(tournoi_participants)}/4)")
async def quitter_tournoi(update: Update, context) -> None:
    global tournoi_participants  # Utilisation de la variable globale
    user = update.message.from_user
    user_id = user.id

    # Vérifie si le joueur est inscrit
    if user_id not in tournoi_participants:
        await update.message.reply_text("Vous n'êtes pas inscrit au tournoi ! ❌")
        return

    # Retire le joueur de la liste des participants
    tournoi_participants.remove(user_id)
    await update.message.reply_text("Vous avez quitté le tournoi. 😔")
    
    # Informe les autres participants du départ
    for participant in tournoi_participants:
        await context.bot.send_message(
            chat_id=participant,
            text=f"{user.first_name} (@{user.username}) a quitté le tournoi. 😔"
        )
        # Vérifie si l'utilisateur est le créateur
def is_creator(user_id):
    return user_id == CREATOR_ID

# Commande pour bannir un utilisateur
async def ban(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /ban <ID utilisateur>")
        return

    target_id = int(context.args[0])
    if target_id not in players:
        await update.message.reply_text("Cet utilisateur n'existe pas ou n'est pas enregistré.")
        return

    players[target_id]['banned'] = True
    await update.message.reply_text(f"L'utilisateur avec l'ID {target_id} a été banni.")

# Commande pour débannir un utilisateur
async def unban(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /unban <ID utilisateur>")
        return

    target_id = int(context.args[0])
    if target_id not in players:
        await update.message.reply_text("Cet utilisateur n'existe pas ou n'est pas enregistré.")
        return

    players[target_id]['banned'] = False
    await update.message.reply_text(f"L'utilisateur avec l'ID {target_id} a été débanni.")

# Commande pour envoyer un message global
async def broadcast(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /broadcast <message>")
        return

    message = " ".join(context.args)
    for player_id in players.keys():
        try:
            await context.bot.send_message(chat_id=player_id, text=f"Message du créateur :\n{message}")
        except Exception as e:
            print(f"Impossible d'envoyer un message à {player_id}: {e}")

    await update.message.reply_text("Message diffusé à tous les utilisateurs.")

async def stats(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    # Vérifie si c'est le créateur
    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    # Vérifie s'il y a des joueurs enregistrés
    if not players:
        await update.message.reply_text("Aucun utilisateur enregistré pour l'instant.")
        return

    # Construire le message de statistiques
    stats_message = "📊 **Statistiques des utilisateurs :**\n\n"
    total_users = 0

    for uid, player in players.items():
        username = player.get('username', f"ID_{uid}")
        name = player.get('name', "Inconnu")
        level = player.get('level', 0)
        exp = player.get('exp', 0)
        money = player.get('money', 0)
        health = player.get('health', 0)
        village = player.get('village', "Non défini")
        clan = player.get('clan', "Non défini")

        stats_message += (
            f"👤 **Nom d'utilisateur :** {username}\n"
            f"🆔 **ID :** {uid}\n"
            f"🏅 **Niveau :** {level}\n"
            f"🌟 **EXP :** {exp}\n"
            f"💰 **Argent :** {money} ¥\n"
            f"❤️ **Santé :** {health}\n"
            f"🏘️ **Village :** {village}\n"
            f"👪 **Clan :** {clan}\n"
            "--------------------------------------\n"
        )
        total_users += 1

    # Ajouter le total d'utilisateurs à la fin
    stats_message += f"\n📈 **Nombre total d'utilisateurs :** {total_users}"

    # Envoyer le message
    await update.message.reply_text(stats_message)

# Commande pour envoyer une annonce
async def annonce(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation : /annonce <message>")
        return

    message = " ".join(context.args)
    for player_id in players.keys():
        try:
            await context.bot.send_message(chat_id=player_id, text=f"📢 Annonce :\n{message}")
        except Exception as e:
            print(f"Impossible d'envoyer une annonce à {player_id}: {e}")

    await update.message.reply_text("Annonce envoyée à tous les utilisateurs.")

async def dieu(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id

    if not is_creator(user_id):
        await update.message.reply_text("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return

    players[user_id] = {
        'name': user.first_name or "Créateur",
        'username': f"@{user.username}" if user.username else f"ID_{user_id}",
        'level': 100000000,  # Niveau très élevé
        'exp': 100000000,  # EXP illimité
        'money': 100000000,  # Argent illimité
        'village': "Divin",
        'clan': "Divin",
        'health': 100000000,  # Santé infinie
        'team': None,
        'inventory': ["∞"] * 100000000,  # Objets illimités
        'is_god_mode': True,  # Flag pour indiquer le mode dieu
    }

    await update.message.reply_text("Mode dieu activé ! 😇 Toutes les activités sont maintenant gagnées automatiquement.")
    # Commande /none pour désactiver le mode dieu (uniquement pour le créateur)
async def none(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifie si l'utilisateur est le créateur
    if user_id != CREATOR_ID:
        await update.message.reply_text("Tu n'as pas la permission d'utiliser cette commande.")
        return

    # Vérifie si l'utilisateur existe
    if user_id not in players:
        await update.message.reply_text("Tu n'es pas encore enregistré. Utilise /start pour commencer.")
        return

    # Vérifie si le mode dieu est activé pour ce joueur
    if players[user_id].get("god_mode", False):
        # Désactive le mode dieu
        players[user_id]["god_mode"] = False

        # Réinitialiser les stats à des valeurs normales de joueur
        players[user_id]["health"] = 100  # Exemple : Santé normale
        players[user_id]["attack"] = 20   # Exemple : Attaque normale
        players[user_id]["level"] = 1     # Exemple : Niveau normal
        players[user_id]["exp"] = 0       # Exemple : Expérience normale
        players[user_id]["money"] = 100   # Exemple : Argent normal

        # Optionnel : Réinitialiser l'inventaire ou d'autres attributs
        players[user_id]["inventory"] = []

        # Message de confirmation
        await update.message.reply_text("Le mode dieu a été désactivé et tes statistiques ont été réinitialisées.")
    else:
        await update.message.reply_text("Le mode dieu est déjà désactivé.")
        # Commande /restart pour réinitialiser les données du joueur
async def restart(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    # Vérifie si l'utilisateur existe dans les données
    if user_id not in players:
        await update.message.reply_text("Tu n'es pas encore enregistré. Utilise /start pour commencer.")
        return

    # Réinitialiser les données du joueur à zéro
    players[user_id] = {
        'name': user.first_name,
        'username': f"@{user.username}" if user.username else "Inconnu",
        'level': 1,
        'exp': 0,
        'money': 100,
        'village': None,
        'clan': None,
        'health': 100,
        'attack': 20,
        'team': None,
        'inventory': [],
        'referrals': [],
        'parrainage_done': False  # Réinitialiser le statut du parrainage
    }

    # Message pour l'utilisateur
    await update.message.reply_text(f"Tes données ont été réinitialisées avec succès, {user.first_name}! Recommence ton aventure ! 🌸")
    # Fonction pour gérer le mode automatique de sauvegarde
async def auto_save(update: Update, context: CallbackContext) -> None:
    save_data(players)  # Sauvegarder les données des joueurs à chaque message

# Créer l'application
application = Application.builder().token("7593371180:AAHDOrLB5GebjIxFGiI0JZNv84-jc5kSVzA").build()

# Charger les données des joueurs au démarrage
players = load_data()

# Ajouter un handler pour les commandes
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_callback))
application.add_handler(CommandHandler("village", choose_village))
application.add_handler(CommandHandler("clan", choose_clan))
application.add_handler(CommandHandler("mission", start_mission))
application.add_handler(CommandHandler("inventory", inventory))
application.add_handler(CommandHandler("profile", profile))
application.add_handler(CommandHandler("jutsu", use_jutsu))
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CommandHandler("buy", buy_item))
application.add_handler(CommandHandler("utiliser", utiliser))
application.add_handler(CommandHandler("pvp", pvp))
application.add_handler(CommandHandler("top_player", top_player))
application.add_handler(CommandHandler("equipe", equipe))
application.add_handler(CommandHandler("donner", donner))
application.add_handler(CommandHandler("bonus", bonus))
application.add_handler(CommandHandler("entrainement", entrainement))
application.add_handler(CommandHandler("inviter", inviter))
application.add_handler(CommandHandler("mission_du_ninja_legendaire", mission_ninja_legendaire))
application.add_handler(CommandHandler("tournoi", tournoi))
application.add_handler(CommandHandler("quitter_tournoi", quitter_tournoi))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("unban", unban))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("stats", stats))
application.add_handler(CommandHandler("annonce", annonce))
application.add_handler(CommandHandler("dieu", dieu))
application.add_handler(CommandHandler("none", none))
application.add_handler(CommandHandler("restart", restart))

# Domaine de ton app Koyeb
APP_URL = "https://only-oneida.amijeunaruto-sineur-bot.koyeb.app"

async def start(update, context):
    await update.message.reply_text("Bot en ligne via webhook !")

def main():
    print("EN COURS DE DÉMARRAGE, PATIENTEZ...")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        webhook_url=f"{APP_URL}/{TOKEN}"  # URL complète de webhook
    )

if __name__ == '__main__':
    main()