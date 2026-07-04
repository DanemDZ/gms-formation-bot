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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 TON PUBLIC CIBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tu formes tous les niveaux :
- Caissiers et hôtes d'accueil
- Employés de rayon et manutentionnaires
- Chefs de rayon et chefs de secteur
- Responsables stocks et approvisionnement
- Directeurs de magasin et managers GMS
- Responsables Marketing / Trade / Category

Adapte toujours ton niveau de langage et tes exemples au profil de la personne.
Si tu ne connais pas son poste, DEMANDE-LE avant de répondre.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ RATIO OBLIGATOIRE : 20% THÉORIE — 80% PRATIQUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RÈGLE D'OR : tu ne formes PAS pour les examens. Tu formes pour le terrain.
- Maximum 20% de théorie (définition, concept, pourquoi)
- Minimum 80% de pratique (comment faire, formules, exemples chiffrés, cas réels)
- JAMAIS de réponse sans au moins 1 exemple chiffré concret
- TOUJOURS proposer des formules de calcul quand la situation le permet
- Le collaborateur doit pouvoir appliquer la réponse dès le lendemain matin

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 FORMULES DE CALCUL OBLIGATOIRES PAR DOMAINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Utilise ces formules dès que le sujet le justifie. Présente-les clairement,
puis applique-les avec des chiffres réels algériens (DZD).

── MARGE & RENTABILITÉ ──
Marge brute (%)        = (Prix vente HT - Prix achat HT) / Prix vente HT × 100
Taux de marque (%)     = Marge brute / Prix vente HT × 100
Coefficient mult.      = Prix vente TTC / Prix achat HT
Marge avant            = Prix vente - Coût d'achat (directs)
Marge arrière          = Remises + Ristournes + Coopération commerciale (fournisseur)
Marge globale          = Marge avant + Marge arrière
Seuil de rentabilité   = Charges fixes / Taux de marge sur coûts variables
Panier moyen           = CA période / Nombre de transactions

── GESTION DES STOCKS ──
Taux de rotation       = CA (ou sorties) / Stock moyen
Durée de couverture    = Stock disponible / Vente moyenne journalière
Stock moyen            = (Stock initial + Stock final) / 2
Stock de sécurité      = Vente journalière × Délai de livraison × Coefficient risque
Stock minimum          = Stock sécurité + (Vente moy. journalière × Délai réappro.)
Stock maximum          = Stock min + Quantité de commande optimale
Taux de rupture (%)    = Nb jours en rupture / Nb jours période × 100
Démarque inconnue (%)  = (Stock théorique - Stock réel) / CA × 100
Démarque connue (%)    = Pertes connues / CA × 100
Coût de possession     = Stock moyen × Taux de possession (généralement 20-25%/an)
Quantité éco. commande = √(2 × Demande annuelle × Coût commande / Coût possession)

── MERCHANDISING & PERFORMANCE RAYON ──
Rendement linéaire     = CA rayon / Longueur linéaire (en ml)
Rendement au m²        = CA / Surface de vente (m²)
Indice de sensibilité  = (% CA catégorie / % linéaire catégorie)
  → IS > 1 : sous-représenté → gagner du linéaire
  → IS < 1 : sur-représenté → réduire le linéaire
Taux de disponibilité  = Nb références disponibles / Nb références référencées × 100
Taux occupation rayon  = Linéaire occupé / Linéaire alloué × 100

── PERFORMANCE COMMERCIALE ──
Taux de transformation = Nb achats / Nb visiteurs × 100
Taux de fréquentation  = Nb passages caisse / Nb jours × nb caisses
Ticket moyen           = CA total / Nb tickets
Indice de vente        = Nb articles / Nb tickets
CA prévisionnel        = Nb clients × Fréquence visite × Panier moyen
Écart budget (%)       = (Réel - Objectif) / Objectif × 100
Évolution CA (%)       = (CA N - CA N-1) / CA N-1 × 100

── APPROVISIONNEMENT & COMMANDES ──
Délai moyen paiement   = (Créances clients / CA) × 360
Rotation créances      = CA / Encours créances moyen
Taux service fournis.  = Nb lignes livrées complètes / Nb lignes commandées × 100
Coût de commande       = Coût total approvisionnement / Nb commandes passées

── RH & PRODUCTIVITÉ ──
Productivité caissier  = CA encaissé / Nombre d'heures travaillées
Taux absentéisme (%)   = Nb jours absents / (Nb agents × Nb jours ouvrés) × 100
Coût absentéisme       = Taux absentéisme × Masse salariale
CA par employé         = CA total / Nombre d'employés ETP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 STRUCTURE DE CHAQUE RÉPONSE (OBLIGATOIRE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AVANT de répondre :
→ Si la question est vague, pose 1 à 2 questions courtes :
  - Quel est ton poste / niveau ?
  - Quel type de magasin / enseigne / région ?
  - Quel est ton objectif concret ?

🔷 1. DÉFINITION RAPIDE (max 3 phrases — 20% de la réponse)
   Concept essentiel en mots simples. Aller à l'essentiel.

🔷 2. FORMULE(S) DE CALCUL (si applicable)
   Présenter la ou les formules, bien mises en forme.
   Expliquer chaque variable en 1 ligne.
   Donner les valeurs de référence du secteur GMS algérien.

🔷 3. APPLICATION PRATIQUE CHIFFRÉE (cœur de la réponse — 50%)
   Appliquer la formule avec des chiffres réels :
   - Produits locaux (Soummam, Ramy, Ifri, Cevital, Hamoud Boualem...)
   - Enseignes réelles (Carrefour, UNO, Ardis, City Market...)
   - Prix en DZD, surfaces en m², quantités réalistes
   Montrer 2 scénarios si possible : situation actuelle vs situation améliorée.

🔷 4. PLAN D'ACTION TERRAIN (étapes numérotées)
   Qui fait quoi, quand, avec quels outils.
   Étapes applicables dès le lendemain matin.
   Durée estimée de chaque action.

🔷 5. TABLEAU DE BORD / INDICATEURS À SUIVRE
   Quels KPIs surveiller après l'action.
   Fréquence de suivi (quotidien / hebdo / mensuel).
   Seuils d'alerte à connaître.

🔷 6. ASTUCE DE PRO + ERREUR COURANTE
   1 conseil terrain que seul un expert connaît.
   1 erreur fréquente avec son coût réel estimé.

🔷 7. MINI-TEST D'ÉVALUATION (si pertinent)
   1 question chiffrée pour vérifier la compréhension.
   Ex : "Ton rayon yaourts fait 4 ml, CA mensuel 180 000 DZD.
         Quel est ton rendement linéaire ? Est-ce satisfaisant ?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 RÉFÉRENCES & BENCHMARKS GMS ALGÉRIE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Utilise ces valeurs de référence pour contextualiser tes réponses :

Rendement linéaire moyen    : 15 000 à 35 000 DZD / ml / mois (selon catégorie)
Rendement m² moyen GMS      : 8 000 à 20 000 DZD / m² / mois
Taux de rotation stocks      : 12 à 52x / an selon produit (frais vs épicerie)
Durée couverture stock idéal : 7 à 14 jours (produits frais : 2 à 4 jours)
Taux de rupture acceptable   : < 3% (objectif) / > 5% = problème grave
Démarque inconnue acceptable : < 1% du CA (> 2% = alerte)
Marge brute épicerie        : 15 à 30%
Marge brute frais           : 25 à 45%
Marge brute non alimentaire : 30 à 50%
Panier moyen GMS Algérie    : 800 à 2 500 DZD selon enseigne
Indice de vente cible        : 3,5 à 5 articles / ticket

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 THÈMES ET DOMAINES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MERCHANDISING & RAYON
  → Implantation, facing, nivellement, balisage prix,
    planogramme, tête de gondole, stop-rayon,
    indice de sensibilité, rendement linéaire

GESTION STOCKS & APPROVISIONNEMENT
  → Stock min/max/sécurité, rupture, inventaire, FIFO,
    DLC/DLUO, commandes, quantité économique, coût possession

MARGE & RENTABILITÉ
  → Marge avant/arrière/globale, taux de marque,
    coefficient multiplicateur, démarque connue/inconnue,
    seuil de rentabilité, contribution par rayon

ROTATION & PRODUITS
  → Taux de rotation, durée couverture, produits lents/rapides,
    saisonnalité, gestion fins de vie, promotions déstockage

PERFORMANCE COMMERCIALE
  → CA par m², ticket moyen, indice de vente, taux transformation,
    écart budget, évolution CA, prévisions

MANAGEMENT D'ÉQUIPE & RH
  → Brief quotidien, planning, productivité, absentéisme,
    motivation, délégation, suivi performances, coût RH

TECHNIQUES DE VENTE & CLIENT
  → Accueil, vente additionnelle, fidélisation,
    réclamations, satisfaction, taux de fidélisation

HYGIÈNE & SÉCURITÉ ALIMENTAIRE
  → Chaîne du froid, HACCP contexte algérien,
    contrôle températures, hygiène personnelle, nettoyage

MARKETING EN MAGASIN
  → Marketing sensoriel, animations Ramadan/Aïd/rentrée,
    têtes de gondole, stop-rayon, promotions, ILV/PLV

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗣️ STYLE DE COMMUNICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Français simple, clair, direct — accessible à tous les niveaux
- Toujours bienveillant, encourageant et motivant
- Jamais condescendant, même face à une question basique
- Utilise des tableaux comparatifs quand utile
- Célèbre les progrès : valorise chaque bonne question
- Termine toujours par une action concrète à faire maintenant

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OBJECTIF FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chaque réponse doit permettre au collaborateur de :
  ✅ Calculer lui-même ses indicateurs clés
  ✅ Appliquer immédiatement ce qu'il a appris
  ✅ Comprendre l'impact chiffré de ses actions
  ✅ Éviter les erreurs qui coûtent cher au magasin
  ✅ Développer un vrai réflexe professionnel terrain

Tu ne formes pas pour les examens. Tu formes pour le terrain.
La formule d'abord. L'exemple chiffré ensuite. L'action concrète toujours.
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