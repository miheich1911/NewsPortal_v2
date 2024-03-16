from django import template


register = template.Library()


@register.filter()
def censor(value):
    swearing = ['европейские', 'кофе']
    if not isinstance(value, str):
        raise TypeError()
    for word in value.split():
        if word.lower() in swearing:
            value = value.replace(word, f"{word[0]}{'*' * (len(word) - 1)}")
    return value

