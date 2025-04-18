predefined_category_icons = {
    "Tech": "💻",
    "Science": "🔬",
    "Health": "🏥",
    "Business": "💼",
    "Politics": "🗳️",
    "Entertainment": "🎭",
    "Sports": "🏅",
    "Education": "🎓",
    "Travel": "✈️",
    "Food": "🍜",
    "Lifestyle": "🧘",
    "Fashion": "👗",
    "Music": "🎵",
    "Movies": "🎬",
    "Gaming": "🎮",
    "News": "📰",
    "Environment": "🌍",
    "Social Media": "📱",
    "Finance": "💰",
    "Art": "🎨",
    "Misc": "🧩"
}

def get_thumbnail(category: str):
    return predefined_category_icons.get(category, "🧩") 