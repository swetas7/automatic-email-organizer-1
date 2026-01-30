def generate_reply(category, sender, body):
    """Generates a template-based reply based on the email category."""
    
    # simplistic name extraction (assumes "Name <email>" format or just Name)
    name = sender.split("<")[0].strip().replace('"', '')
    if "@" in name: # if name is just an email
        name = "there"
    
    greeting = f"Hi {name},"
    signature = "\n\nBest regards,\n[Your Name]"
    
    templates = {
        "Classes & Lectures": f"{greeting}\n\nThank you for the update regarding the class. I have noted the details.\n{signature}",
        "Exams & Academics": f"{greeting}\n\nI have received the information about the exams. Thanks for letting me know.\n{signature}",
        "Assignments & Deadlines": f"{greeting}\n\nMessage received. I will ensure to submit the assignment on time.\n{signature}",
        "Placements & Internships": f"{greeting}\n\nThank you for this opportunity. I will review the details and apply accordingly.\n{signature}",
        "Club Activities": f"{greeting}\n\nSounds exciting! I'll check my calendar and try to be there.\n{signature}",
        "Events & Workshops": f"{greeting}\n\nThanks for the invitation. I look forward to the event.\n{signature}",
        "Competitions & Hackathons": f"{greeting}\n\nCount me in! I will check the rules and register.\n{signature}",
        "Administrative Notices": f"{greeting}\n\nNoted. Thank you for the information.\n{signature}",
        "Finance & Fees": f"{greeting}\n\nI have received the payment/fee notice. I will process it shortly.\n{signature}",
        "General Announcements": f"{greeting}\n\nThanks for the update.\n{signature}",
        "Spam / Promotions": "", # No reply for spam
    }
    
    return templates.get(category, f"{greeting}\n\nReceived with thanks.\n{signature}")
