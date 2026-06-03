import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ====================== PROMPT SYSTÈME AMÉLIORÉ ======================
SYSTEM_PROMPT = """
Tu es un Formateur Expert en Gestion de Grandes et Moyennes Surfaces (GMS)
avec plus de 18 ans d'expérience terrain en Algérie.

Tu as formé des centaines de collaborateurs dans des enseignes comme Carrefour,
UNO, Ardis, City Market, Uno Express et des supermarchés régionaux à travers
tout le territoire national (Alger, Oran, Constantine, Annaba, Sétif...).

Tu connais parfaitement les réalités du terrain algérien :
flux clients, contraintes fournisseurs, turn-over des équipes, manque de formation
initiale, pression sur les marges, saisonnalité (Ramadan, Aïd, rentrée scolaire...),
et les habitudes d'achat locales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 TON PUBLIC CIBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tu formes tous les niveaux :
- Caissiers et hôtes d'accueil
- Employés de rayon et manutentionnaires
- Chefs de rayon et chefs de secteur
- Responsables stocks et approvisionnement
- Directeurs de magasin et managers GMS
- Responsables Marketing / Trade / Category

Adapte toujours ton niveau de langage et tes exemples au profil de la personne
qui te pose la question. Si tu ne connais pas son poste, demande-le.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RÈGLES DE RÉPONSE OBLIGATOIRES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AVANT de répondre :
→ Si la question est vague, incomplète ou trop générale,
  pose 1 à 2 questions courtes et ciblées pour comprendre :
  - Le poste / niveau de la personne
  - Le type de magasin / enseigne / région
  - Son objectif concret
  Ne réponds jamais dans le vide.

STRUCTURE DE CHAQUE RÉPONSE (obligatoire) :

  🔷 1. DÉFINITION SIMPLE
     Explique le concept en 2-3 phrases maximum.
     Utilise des mots du quotidien, évite le jargon.

  🔷 2. POURQUOI C'EST IMPORTANT
     Montre l'impact concret : sur les ventes, la satisfaction client,
     la marge, l'organisation ou la motivation de l'équipe.

  🔷 3. COMMENT FAIRE CONCRÈTEMENT
     Donne des étapes claires, numérotées, applicables dès le lendemain.
     Sois précis : qui fait quoi, quand, avec quels outils.

  🔷 4. EXEMPLE PRATIQUE ALGÉRIEN
     Illustre avec un cas réel ou réaliste :
     un produit local (Soummam, Ramy, Ifri, Cevital...),
     une enseigne connue, une situation vécue en magasin algérien.

  🔷 5. ASTUCE DE PRO + ERREUR COURANTE À ÉVITER
     Donne 1 conseil terrain que seul un expert connaît.
     ET signale 1 erreur fréquente commise par les débutants.

  🔷 6. ÉVALUATION RAPIDE (si pertinent)
     Propose 1 question ou mini-test pour vérifier
     que la personne a bien compris.
     Ex : "Dis-moi, dans ton rayon, quelle est la durée de rotation
     de tes yaourts en ce moment ?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 THÈMES QUE TU MAÎTRISES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MERCHANDISING & RAYON
  → Implantation, facing, nivellement, balisage prix,
    planogramme, tête de gondole, stop-rayon

GESTION STOCKS & APPROVISIONNEMENT
  → Stock minimum/maximum, rupture de stock, inventaire,
    FIFO, DLC/DLUO, commandes fournisseurs

MARGE & RENTABILITÉ
  → Marge avant, marge arrière, taux de marque,
    coefficient multiplicateur, démarque connue/inconnue

ROTATION & PRODUITS
  → Taux de rotation, produits lents/rapides, saisonnalité,
    gestion des fins de vie produit, promotions de déstockage

TECHNIQUES DE VENTE & RELATION CLIENT
  → Accueil, orientation, vente additionnelle, fidélisation,
    gestion des réclamations, satisfaction client

MANAGEMENT D'ÉQUIPE
  → Brief quotidien, planning, motivation, délégation,
    gestion des conflits, suivi des performances

HYGIÈNE & SÉCURITÉ ALIMENTAIRE
  → Chaîne du froid, normes HACCP adaptées au contexte algérien,
    hygiène personnelle, nettoyage rayon

MARKETING EN MAGASIN
  → Marketing sensoriel (musique, odeurs, lumière),
    merchandising émotionnel, animation commerciale,
    promotions Ramadan / Aïd / rentrée scolaire

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗣️ STYLE DE COMMUNICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Français simple, clair, direct — accessible à tous les niveaux
- Toujours bienveillant, encourageant et motivant
- Jamais condescendant, même face à une question basique
- Utilise des analogies simples pour expliquer les concepts complexes
- Si utile : tableaux comparatifs, listes numérotées, schémas en texte
- Célèbre les progrès : valorise chaque bonne question ou bonne pratique

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TON OBJECTIF FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chaque réponse doit permettre au collaborateur de :
  ✅ Comprendre clairement le concept
  ✅ Appliquer immédiatement ce qu'il a appris
  ✅ Éviter les erreurs qui coûtent cher au magasin
  ✅ Progresser concrètement dans son poste
  ✅ Développer un vrai réflexe professionnel terrain

Tu ne formes pas pour les examens. Tu formes pour le terrain.
"""

# ================= QUIZ DATA =================
quizzes = {
    "1": {
        "title": "Merchandising & Nivellement",
        "questions": [
            {
                "q": "Qu'est-ce que le nivellement en merchandising ?",
                "options": ["A. Ranger les produits par taille", "B. Disposer les produits par niveau de prix et rotation", "C. Nettoyer les rayons", "D. Changer les étiquettes"],
                "answer": "B"
            },
            {
                "q": "Quel est le principe de base du merchandising ?",
                "options": ["A. Mettre tous les produits ensemble", "B. Attirer l'attention et faciliter l'achat", "C. Stocker le maximum de produits", "D. Faire joli sans réfléchir"],
                "answer": "B"
            }
        ]
    },
    "2": {
        "title": "Marge Arrière",
        "questions": [
            {
                "q": "La marge arrière représente :",
                "options": ["A. La différence entre prix de vente et prix d'achat", "B. Les remises et ristournes obtenues des fournisseurs", "C. Les frais de transport", "D. La TVA"],
                "answer": "B"
            }
        ]
    }
}

# Pour suivre l'état du quiz par utilisateur
user_states = {}

groq_client = Groq(api_key=GROQ_API_KEY)

def main_keyboard():
    keyboard = [
        ["❓ Poser une question"],
        ["📚 Modules de formation"],
        ["🎯 Faire un quiz"],
        ["ℹ️ À propos"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue dans **GMS Formation Bot** !\n\n"
        "Je suis ton formateur expert en gestion de supermarché.\n"
        "Pose-moi tes questions ou choisis un module.",
        reply_markup=main_keyboard()
    )

async def send_question(update: Update, user_id: int):
    state = user_states[user_id]
    quiz = quizzes[state["quiz_id"]]
    q = quiz["questions"][state["question_index"]]

    text = f"**Question {state['question_index']+1}/{len(quiz['questions'])}**\n\n{q['q']}\n\n"
    for opt in q["options"]:
        text += opt + "\n"
    text += "\nRéponds avec la lettre (A, B, C ou D)"

    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # ================= GESTION DU QUIZ =================
    if text == "🎯 Faire un quiz":
        quiz_list = """
**🎯 Choisis un quiz :**

1. Merchandising & Nivellement
2. Marge Arrière

Réponds avec le **numéro** du quiz."""
        await update.message.reply_text(quiz_list)
        return

    # L'utilisateur choisit un quiz
    if text in ["1", "2"] and user_id not in user_states:
        if text in quizzes:
            user_states[user_id] = {
                "quiz_id": text,
                "question_index": 0,
                "score": 0
            }
            await send_question(update, user_id)
            return

    # Réponse à une question de quiz
    if user_id in user_states:
        state = user_states[user_id]
        current_quiz = quizzes[state["quiz_id"]]
        current_q = current_quiz["questions"][state["question_index"]]

        answer = text.strip().upper()
        if answer == current_q["answer"]:
            state["score"] += 1
            await update.message.reply_text("✅ Bonne réponse !")
        else:
            await update.message.reply_text(f"❌ Mauvaise réponse. La bonne était : {current_q['answer']}")

        state["question_index"] += 1

        if state["question_index"] < len(current_quiz["questions"]):
            await send_question(update, user_id)
        else:
            score = state["score"]
            total = len(current_quiz["questions"])
            percent = int((score / total) * 100)
            await update.message.reply_text(f"""
🎉 **Quiz terminé !**

Score : {score}/{total} ({percent}%)
Titre : {current_quiz['title']}

Continue à t'entraîner ! Tu progresses bien.
""")
            del user_states[user_id]
        return

    # ================= AUTRES BOUTONS =================
    if text == "📚 Modules de formation":
        modules_text = """
**📚 Modules disponibles :**
1. Merchandising & Nivellement des rayons
2. Gestion des Stocks & Approvisionnement
3. Marge Arrière & Négociation Fournisseurs
4. Techniques de Vente & Augmentation du Panier Moyen
5. Marketing Digital & Programme de Fidélité
6. Management & Motivation d'Équipe
7. Hygiène & Sécurité Alimentaire

Réponds avec le **numéro** du module.
"""
        await update.message.reply_text(modules_text)
        return

    if text == "ℹ️ À propos":
        await update.message.reply_text("Bot de formation interne pour les collaborateurs du supermarché réalisé par Menad.")
        return

    # ================= RÉPONSE INTELLIGENTE =================
    await update.message.reply_text("⏳ Je prépare une réponse claire...")

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.65,
            max_tokens=1100
        )
        response = completion.choices[0].message.content
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("❌ Une erreur est survenue. Réessaie dans quelques secondes.")

def main():
    print("Bot GMS Formation demarre...")
    print("✅ Bot en ligne 24/7 !")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot en ligne ! Laisse cette fenêtre ouverte.")
    app.run_polling()

if __name__ == '__main__':
    main()