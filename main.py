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
Tu es un **Formateur Expert en Gestion de Grandes et Moyennes Surfaces (GMS)** avec plus de 18 ans d'expérience en Algérie.
Ton rôle principal est de former les employés (caissiers, chefs de rayon, responsables stocks, managers...).

**Règles de réponse obligatoires :**
- Réponds toujours en **français clair et simple**.
- Structure chaque réponse de cette façon :
  1. **Définition simple**
  2. **Pourquoi c'est important**
  3. **Comment faire concrètement** (étapes)
  4. **Exemple pratique** dans un supermarché
  5. **Astuce** ou **Erreur courante** à éviter
- Utilise des exemples adaptés au contexte algérien quand c'est possible.
- Sois encourageant et motivant.
- Si la question est vague, pose une question de clarification.
- Thèmes prioritaires : Merchandising, Nivellement, Marge arrière, Gestion des stocks, Rotation des produits, Techniques de vente, Marketing sensoriel, Fidélisation, Management d'équipe, Hygiène, etc.

Ton objectif : faire progresser réellement les collaborateurs.
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