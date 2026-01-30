def is_newsletter(sender, subject, body):
    """
    Determines if an email is a newsletter.
    Returns: bool
    """
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # Keywords often found in newsletters
    keywords = [
        "unsubscribe", "view in browser", "update your preferences",
        "privacy policy", "terms of use", "opt out", "newsletter",
        "weekly digest", "daily digest"
    ]
    
    # Check body for keywords
    for keyword in keywords:
        if keyword in body_lower:
            return True
            
    # Check sender for common newsletter patterns
    if "newsletter" in sender_lower or "noreply" in sender_lower or "digest" in sender_lower:
        return True
        
    return False
