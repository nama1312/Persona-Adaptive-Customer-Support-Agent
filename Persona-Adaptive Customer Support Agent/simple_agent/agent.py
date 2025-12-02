import re
from simple_agent.llm import generate_llm_reply


# below is knowledge base (KB)

KB = [
    {"id": "kb1", "title": "Auth error 403", "content": "403 means permission denied. Check API key and scopes."},
    {"id": "kb2", "title": "Set API token", "content": "Create API key in Settings and set the env var MY_API_KEY."},
    {"id": "kb3", "title": "Rate limit", "content": "If you see 429, wait and retry with exponential backoff."},
]



def _norm(text):
    return re.sub(r"\W+", " ", text.lower()).strip()



def detect_persona(message):
    t = _norm(message)
    if any(w in t for w in ["angry","frustrat","not working","nothing"]):
        return "Frustrated User"
    if any(w in t for w in ["api","error","token","log","403","500"]):
        return "Technical Expert"
    if any(w in t for w in ["sla","roi","budget","exec","qbr"]):
        return "Business Executive"
    return "Frustrated User"  



def retrieve_kb(message, top_k=2):
    words = set(_norm(message).split())
    scored = []
    for doc in KB:
        doc_words = set(_norm(doc['title'] + ' ' + doc['content']).split())
        score = len(words & doc_words)
        if score > 0:
            scored.append((score, doc))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [d for s,d in scored[:top_k]]



def should_escalate(message, persona, kb_results, session):
    text = _norm(message)
    
    if any(p in text for p in ["human","agent","talk to","escalate"]):
        return True, "user asked for human"
    
    session.setdefault('frustration', 0)
    if persona == 'Frustrated User' and any(w in text for w in ['nothing','still','not working']):
        session['frustration'] += 1
        if session['frustration'] >= 2:
            return True, 'repeated frustration'

    if persona == 'Technical Expert' and not kb_results:
        return True, 'no KB match for technical question'
    return False, ''



def generate_reply(message, persona, kb_results):
    if not kb_results:
        kb_text = "I couldn't find a KB article that matches."
    else:
        kb_text = '\n'.join([f"{d['title']}: {d['content']}" for d in kb_results])

    if persona == 'Technical Expert':
        return kb_text + '\n\nNext: please share logs and exact error codes.'
    if persona == 'Frustrated User':
        return "Sorry you're facing this. " + kb_text + "\nSteps: 1) Check token 2) Restart client 3) Tell me if it still fails."
    if persona == 'Business Executive':
        return "Short summary: " + kb_text + "\nImpact: possible auth or rate-limit issue. Recommend escalating to engineering if needed."
    return kb_text



def support_agent(message, session=None):
    if session is None:
        session = {}
    persona = detect_persona(message)
    kb_results = retrieve_kb(message)
    escalate, reason = should_escalate(message, persona, kb_results, session)
    reply = generate_llm_reply(persona, message, kb_results)
    handoff = None
    if escalate:
        handoff = {
            'summary': message[:500],
            'persona': persona,
            'kb': [d['id'] for d in kb_results],
            'reason': reason,
            'owner': 'Tier 2' if persona == 'Technical Expert' else 'Account Manager'
        }
    return {
        'assistant_message': reply,
        'persona': persona,
        'kb_used': [d['id'] for d in kb_results],
        'should_escalate': escalate,
        'handoff': handoff,
        'session': session
    }
