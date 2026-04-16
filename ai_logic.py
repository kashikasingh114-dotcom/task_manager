def analyze_task(title: str):
    title_lower = title.lower()

    # 🔥 Priority detection (smarter)
    if any(word in title_lower for word in ["urgent", "asap", "today"]):
        priority = "High"
        reason = "Contains urgency keywords"
    elif any(word in title_lower for word in ["tomorrow", "soon"]):
        priority = "Medium"
        reason = "Contains near-deadline keywords"
    elif any(word in title_lower for word in ["exam", "assignment"]):
        priority = "High"
        reason = "Important academic task"
    else:
        priority = "Low"
        reason = "No urgency detected"

    # 🧠 Category detection
    if any(word in title_lower for word in ["study", "exam", "assignment"]):
        category = "Study"
    elif any(word in title_lower for word in ["meeting", "project", "office"]):
        category = "Work"
    elif any(word in title_lower for word in ["gym", "run", "health"]):
        category = "Health"
    elif any(word in title_lower for word in ["buy", "shopping", "home"]):
        category = "Personal"
    else:
        category = "General"

    return {
        "priority": priority,
        "category": category,
        "reason": reason
    }