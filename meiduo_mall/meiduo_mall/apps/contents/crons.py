from collections import OrderedDict
from django.template import loader
import os
from django.conf import settings
import io

from contents.utils import get_categories
from contents.models import ContentCategory


def generate_static_index_html():

    categories = get_categories()

    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents
    }

    template = loader.get_template('index.html')
    html_text = template.render(context)

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

