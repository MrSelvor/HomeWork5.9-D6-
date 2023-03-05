from django import template

register = template.Library()

@register.filter()

def censor(text):

    if type(text) == str:

        censors_words = ["article", "news"]

        for word in censors_words:
            text = text.replace(word, '*' * len(word))

        return text
    else:
        print("TypeError")