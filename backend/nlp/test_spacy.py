import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Test a command
doc = nlp("delete the latest task please")

# Show tokens
for token in doc:
    print(token.text, token.pos_, token.dep_)
