def scan_email(subject, body, sender):
    """
    Scans the email for phishing indicators.
    Returns: (is_safe: bool, reason: str)
    """
    subject_lower = subject.lower()
    body_lower = body.lower()
    sender_lower = sender.lower()
    
    # List of suspicious keywords
    phishing_keywords = [
        "verify your account", "verify password", "urgent action required",
        "account suspended", "click here to unlock", "unauthorized access",
        "lottery winner", "congratulations you won", "bank account locked",
        "update your details", "immedate response"
    ]
    
    # Check for keywords
    for keyword in phishing_keywords:
        if keyword in body_lower or keyword in subject_lower:
            return False, f"Detected suspicious keyword: '{keyword}'"
            
    # Check for suspicious senders (basic check)
    if "no-reply" in sender_lower or "admin" in sender_lower:
        # If strict check is needed, but for now just flagging generic generic domains
        pass 
        
    return True, "Safe"
