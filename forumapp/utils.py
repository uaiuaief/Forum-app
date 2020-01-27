from .models.models import User, Post, Thread, Category, SubCategory
from forumapp import db
import re


def delete_recursively(obj):
    if type(obj) is Category:
        for sub_category in obj.sub_categories:
            delete_recursively(sub_category)
        db.session.delete(obj)
        db.session.commit()

    if type(obj) is SubCategory:
        for thread in obj.threads:
            delete_recursively(thread)
        db.session.delete(obj)
        db.session.commit()

    if type(obj) is Thread:
        for post in obj.posts:
            delete_recursively(post)
        db.session.delete(obj)
        db.session.commit()

    if type(obj) is Post:
        db.session.delete(obj)
        db.session.commit()


def sanitize_html(text):
    allowed_tags = [
        'img', '/img',
        'url', '/url',
        'quote', '/quote',

        'strong', '/strong',
        'b', '/b',
        'em', '/em',
        'code', '/code',
        'sub', '/sub',
        'sup', '/sup',
        'yt', '/yt'
    ]

    # pattern = re.compile(r'<.*?>(.*?)<.*?>')
    pattern = re.compile(r'<(.*?)>([\s\S]*?)<(.*?)>')
    matches = pattern.finditer(text)

    # text = text.replace('"', '&quot')
    # text = text.replace("'", '&#39')

    text = text.replace('<', '&lt')
    text = text.replace('>', '&gt')

    for match in matches:
        open_tag = match[1]
        between_tags = match[2]
        close_tag = match[3]

        if (open_tag in allowed_tags) and (close_tag in allowed_tags):
            if open_tag == 'img' and close_tag == '/img':

                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<img class="rendered" src="{between_tags}" alt="img">')

            elif open_tag == 'url' and close_tag == '/url':
                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<a class="rendered" href="{between_tags}" target=_blank>{between_tags}</a>')

            elif open_tag == 'yt' and close_tag == '/yt':
                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<iframe width="800" height="475" class="rendered" src="https://www.youtube.com/embed/{between_tags}" target=_blank></iframe>')


            # elif open_tag == 'quote' and close_tag == '/quote':
            #     text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt',
            #                         f'<div style="background-color: #283c60; '
            #                         f'border-bottom: 1px #bbb solid; '
            #                         f'border-top: 1px #000 solid; '
            #                         f'border-left: 1px #000 solid; '
            #                         f'border-right: 1px #bbb solid; padding: .5em"> {between_tags}</div>')

            else:
                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<{open_tag} class="rendered">{between_tags}<{close_tag}>')


    return text


def render_quote(text):
    text = f'<quote>{text}</quote>'
    return text
