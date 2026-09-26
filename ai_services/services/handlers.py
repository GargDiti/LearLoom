from services.query_router import Source, Action

def handle_general_learn(query: str):
    # TODO: send query straight to Groq for an explanation
    pass

def handle_website_learn(query: str, url: str):
    # TODO: Firecrawl -> discover topics -> user picks one -> fetch relevant content -> Groq explains it
    pass

def handle_general_quiz(query: str):
    # TODO: Groq generates a quiz directly from the named topic
    pass

def handle_website_quiz(query: str, url: str):
    # TODO: Firecrawl scrapes relevant content -> Groq generates quiz from that content only
    pass

def dispatch(source: Source, action: Action, query: str, url: str | None):
    if source == Source.GENERAL and action == Action.LEARN:
        return handle_general_learn(query)
    if source == Source.WEBSITE and action == Action.LEARN:
        return handle_website_learn(query, url)
    if source == Source.GENERAL and action == Action.QUIZ:
        return handle_general_quiz(query)
    if source == Source.WEBSITE and action == Action.QUIZ:
        return handle_website_quiz(query, url)