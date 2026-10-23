import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Bot Token from Environment Variable ─────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set.")

# ── Data: Facts and Quizzes ──────────────────────────────
FACTS = {
    "science": [
        "A teaspoon of neutron star material would weigh about 6 billion tons on Earth.",
        "Light from the Sun takes about 8 minutes and 20 seconds to reach Earth.",
        "Water expands by about 9% when it freezes, which is why ice floats.",
    ],
    "animals": [
        "A group of flamingos is called a 'flamboyance'.",
        "Octopuses have three hearts and blue blood.",
        "Cows have best friends and can become stressed when separated from them.",
    ],
    "geography": [
        "The Pacific Ocean is larger than all of Earth's land area combined.",
        "Africa is the only continent that spans all four hemispheres.",
        "Canada has more lakes than the rest of the world combined.",
    ],
    "history": [
        "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "The shortest war in history lasted about 38 minutes, between Britain and Zanzibar in 1896.",
        "Oxford University is older than the Aztec Empire.",
    ],
    "technology": [
        "The first computer bug was a real moth found in a Harvard Mark II computer in 1947.",
        "Email existed before the World Wide Web.",
        "The first 1GB hard drive, released in 1980, weighed over 500 pounds and cost $40,000.",
    ],
}

QUIZZES = {
    "science": [
        {
            "question": "What is the most abundant gas in Earth's atmosphere?",
            "options": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
            "answer": 1,
        },
        {
            "question": "How many bones are in the adult human body?",
            "options": ["206", "300", "150", "250"],
            "answer": 0,
        },
    ],
    "animals": [
        {
            "question": "Which animal is known as the 'ship of the desert'?",
            "options": ["Horse", "Camel", "Elephant", "Donkey"],
            "answer": 1,
        },
        {
            "question": "What is the fastest land animal?",
            "options": ["Lion", "Cheetah", "Horse", "Greyhound"],
            "answer": 1,
        },
    ],
    "geography": [
        {
            "question": "What is the largest desert in the world?",
            "options": ["Sahara", "Arabian", "Gobi", "Antarctic"],
            "answer": 3,
        },
        {
            "question": "Which country has the most time zones?",
            "options": ["Russia", "USA", "France", "China"],
            "answer": 2,
        },
    ],
    "history": [
        {
            "question": "In which year did the Berlin Wall fall?",
            "options": ["1987", "1989", "1991", "1993"],
            "answer": 1,
        },
        {
            "question": "Who was the first President of the United States?",
            "options": ["Thomas Jefferson", "George Washington", "John Adams", "Abraham Lincoln"],
            "answer": 1,
        },
    ],
    "technology": [
        {
            "question": "What does 'CPU' stand for?",
            "options": ["Central Process Unit", "Central Processing Unit", "Computer Personal Unit", "Central Processor Utility"],
            "answer": 1,
        },
        {
            "question": "Which company created the Android operating system?",
            "options": ["Apple", "Microsoft", "Google", "Samsung"],
            "answer": 2,
        },
    ],
}

CATEGORIES = ["science", "animals", "geography", "history", "technology"]
CATEGORY_LABELS = {
    "science": "🔬 Science",
    "animals": "🐾 Animals",
    "geography": "🌍 Geography",
    "history": "📜 History",
    "technology": "💻 Technology",
}

# ── In-memory user state ─────────────────────────────────
user_category = {}      # user_id -> category
user_quiz_state = {}    # user_id -> { category, index, score }

# ── Helpers ──────────────────────────────────────────────
def build_category_keyboard():
    buttons = []
    for cat in CATEGORIES:
        buttons.append(
            [InlineKeyboardButton(CATEGORY_LABELS[cat], callback_data=f"cat:{cat}")]
        )
    return InlineKeyboardMarkup(buttons)

def build_action_keyboard(category):
    buttons = [
        [
            InlineKeyboardButton("📖 Get a Fact", callback_data=f"fact:{category}"),
            InlineKeyboardButton("❓ Take a Quiz", callback_data=f"quiz:{category}"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# ── Command Handlers ─────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_category.pop(user.id, None)
    user_quiz_state.pop(user.id, None)

    await update.message.reply_text(
        "👋 Welcome to SB24GZ Daily Facts Bot!\n\n"
        "I send interesting facts and short quizzes in five categories:\n\n"
        "🔬 Science\n🐾 Animals\n🌍 Geography\n📜 History\n💻 Technology\n\n"
        "Use the buttons below to pick a category, then choose a fact or a quiz.\n\n"
        "Commands:\n"
        "/fact – Get a fact from your chosen category\n"
        "/quiz – Take a quick quiz\n"
        "/category – Change your category\n"
        "/help – Show this message again",
        reply_markup=build_category_keyboard(),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here’s how to use the bot:\n\n"
        "1. Tap /start to choose a category.\n"
        "2. Use /fact to get a fact from your category.\n"
        "3. Use /quiz to take a quiz in your category.\n"
        "4. Use /category to switch categories.\n\n"
        "Everything happens right here in the chat — no external links."
    )

async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose a category:", reply_markup=build_category_keyboard()
    )

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    category = user_category.get(user_id)
    if not category:
        await update.message.reply_text(
            "Please choose a category first:", reply_markup=build_category_keyboard()
        )
        return
    fact = random.choice(FACTS[category])
    await update.message.reply_text(
        f"{CATEGORY_LABELS[category]} — Fact:\n\n{fact}",
        reply_markup=build_action_keyboard(category),
    )

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    category = user_category.get(user_id)
    if not category:
        await update.message.reply_text(
            "Please choose a category first:", reply_markup=build_category_keyboard()
        )
        return
    await send_quiz(update, user_id, category, 0, 0)

async def send_quiz(update, user_id, category, index, score):
    quizzes = QUIZZES[category]
    if index >= len(quizzes):
        await update.effective_message.reply_text(
            f"🎉 Quiz complete!\n\nYour score: {score}/{len(quizzes)}\n\n"
            "Use the buttons below to keep learning.",
            reply_markup=build_action_keyboard(category),
        )
        user_quiz_state.pop(user_id, None)
        return

    q = quizzes[index]
    user_quiz_state[user_id] = {"category": category, "index": index, "score": score}

    buttons = []
    for i, option in enumerate(q["options"]):
        buttons.append(
            [InlineKeyboardButton(option, callback_data=f"ans:{category}:{index}:{i}")]
        )
    await update.effective_message.reply_text(
        f"{CATEGORY_LABELS[category]} — Quiz {index + 1}/{len(quizzes)}\n\n{q['question']}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

# ── Callback Handlers ────────────────────────────────────
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("cat:"):
        category = data.split(":", 1)[1]
        if category not in CATEGORIES:
            return
        user_category[user_id] = category
        await query.edit_message_text(
            f"You chose {CATEGORY_LABELS[category]}.\n\nWhat would you like to do?",
            reply_markup=build_action_keyboard(category),
        )

    elif data.startswith("fact:"):
        category = data.split(":", 1)[1]
        if category not in CATEGORIES:
            return
        user_category[user_id] = category
        fact = random.choice(FACTS[category])
        await query.edit_message_text(
            f"{CATEGORY_LABELS[category]} — Fact:\n\n{fact}",
            reply_markup=build_action_keyboard(category),
        )

    elif data.startswith("quiz:"):
        category = data.split(":", 1)[1]
        if category not in CATEGORIES:
            return
        user_category[user_id] = category
        await send_quiz(update, user_id, category, 0, 0)

    elif data.startswith("ans:"):
        parts = data.split(":")
        if len(parts) != 4:
            return
        _, category, index_str, answer_str = parts
        index = int(index_str)
        chosen = int(answer_str)
        state = user_quiz_state.get(user_id)
        if not state or state["category"] != category or state["index"] != index:
            await query.edit_message_text(
                "This quiz has expired. Use /quiz to start a new one."
            )
            return

        quizzes = QUIZZES[category]
        correct = quizzes[index]["answer"]
        score = state["score"] + (1 if chosen == correct else 0)
        feedback = "✅ Correct!" if chosen == correct else f"❌ Wrong. The correct answer was: {quizzes[index]['options'][correct]}"

        await query.edit_message_text(
            f"{feedback}\n\n{quizzes[index]['question']}\n\n"
            f"Your current score: {score}/{len(quizzes)}"
        )
        await send_quiz(update, user_id, category, index + 1, score)

# ── Application ──────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("category", category_command))
    app.add_handler(CommandHandler("fact", fact_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("✅ Bot handlers registered. Starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
