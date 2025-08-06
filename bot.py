import discord
from discord.ext import commands
import csv
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id != 1115026738238464080:
        return

    auteur = message.author.mention
    date_heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extraction des données du message
    lines = message.content.strip().split('\n')
    data = {}

    form_keys = {
        "Nom du soignant": "nom_soignant",
        "Date et Heure de l'Intervention": "date_heure",
        "Nom + Prénom de la Victime": "nom_victime",
        "SEXE de la Victime": "sexe",
        "Raison de l'Intervention": "raison",
        "Localisation des Blessures": "localisation",
        "Echelle de douleur": "douleur",
        "Détails des Blessures": "details",
        "Description de la Prise en Charge": "prise_en_charge",
        "Examens réalisés": "examens",
        "Opération Réalisée ?": "operation",
        "Si oui, de quoi s'agissait-il ?": "details_operation",
        "Suivi de la Victime": "suivi"
    }

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key in form_keys:
                data[form_keys[key]] = value

    # Chemin CSV
    csv_path = os.path.join(os.getcwd(), "interventions.csv")
    file_exists = os.path.isfile(csv_path)

    # Ecriture CSV
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(form_keys.values())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({key: data.get(key, '') for key in fieldnames})

    # Création dossier PDF si non existant
    pdf_dir = "pdf_bilans"
    os.makedirs(pdf_dir, exist_ok=True)

    # Génération du PDF
    victime = data.get("nom_victime", "victime")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"BILAN_{victime.replace(' ', '_')}_{timestamp}.pdf"
    file_path = os.path.join(pdf_dir, file_name)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>BILAN MÉDICAL D'INTERVENTION</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    for key in fieldnames:
        label = key.replace('_', ' ').capitalize()
        value = data.get(key, '-')
        elements.append(Paragraph(f"<b>{label}</b> : {value}", styles['Normal']))
        elements.append(Spacer(1, 6))

    doc.build(elements)

    # Envoi du message résumé dans le salon de log
    log_channel = bot.get_channel(1115027225071333518)
    date_formatted = datetime.now().strftime("%d/%m/%Y à %H:%M")
    if log_channel:
        print("✅ Salon de log trouvé")
        await log_channel.send(
            f"🗕️ Bilan médical de **{victime}** (envoyé par {auteur}) le **{date_formatted}**",
            file=discord.File(file_path)
        )
    else:
        print("❌ Salon de log introuvable")
        await bot.process_commands(message)

# Démarrez votre bot ici
bot.run("TOKEN")