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
    allowed_tags = ['img', '/img', 'strong', '/strong']

    # pattern = re.compile(r'<.*?>(.*?)<.*?>')
    pattern = re.compile(r'<(.*?)>(.*?)<(.*?)>')
    matches = pattern.finditer(text)

    text = text.replace('"', '&quot')
    text = text.replace("'", '&#39')
    text = text.replace('<', '&lt')
    text = text.replace('>', '&gt')

    for match in matches:
        open_tag = match[1]
        between_tags = match[2]
        close_tag = match[3]

        if (open_tag in allowed_tags) and (close_tag in allowed_tags):
            if open_tag == 'img' and close_tag == '/img':
                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<img src="{between_tags}" alt="img">')
            else:
                text = text.replace(f'&lt{open_tag}&gt{between_tags}&lt{close_tag}&gt', f'<{open_tag}>{between_tags}<{close_tag}>')

    return text



