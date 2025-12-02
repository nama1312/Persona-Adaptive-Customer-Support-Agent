from simple_agent.agent import support_agent

if __name__ == '__main__':
    session = {}
    messages = [
        "Nothing is working. I get a 403 error when calling the API!",
        "What is our SLA and uptime? My execs asked for it.",
        "How do I set the API token in my container?"
        "I need to talk to a human right now!",                       
        "Nothing is working, this system is broken!",              
        "It's still not working! This is getting ridiculous!",     
        "The GPU kernel panic happens in tensor ops, advise me.",    


    ]
    for m in messages:
        out = support_agent(m, session)
        print('\n--- USER ---')
        print(m)
        print('\n--- ASSISTANT ---')
        print(out['assistant_message'])
        print('\nPersona:', out['persona'])
        print('KB used:', out['kb_used'])
        print('Should escalate:', out['should_escalate'])
        if out['handoff']:
            print('Handoff:', out['handoff'])
