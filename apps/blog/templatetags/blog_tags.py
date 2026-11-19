"""Blog şablon etiketleri — yazı gövdesi + yazı içi CTA.

{% blog_body p.content %}  → Markdown'ı HTML'e çevirir ve "bizi tanıyın" CTA kutusunu (blog/_cta_about.html) gövdeye
yerleştirir: yazar gövdede tek satır olarak `{{cta:about}}` yazdıysa oraya; yazmadıysa 3. H2'den hemen önce (en az
3 bölüm varsa), yoksa gövdenin sonuna. CTA metinleri admin'den (ContentBlock "blog-about-cta") düzenlenir.
"""
import re

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from apps.core.templatetags.site_tags import render_markdown

register = template.Library()

TOKEN = re.compile(r"<p>\s*\{\{\s*cta:about\s*\}\}\s*</p>")
H2 = re.compile(r"<h2\b")
MIN_SECTIONS = 3  # bu kadar H2 yoksa CTA gövde sonuna


def insert_cta(html, cta_html):
    """CTA'yı belirteç varsa belirtecin yerine, yoksa 3. H2'den önce, o da yoksa sona ekler."""
    if TOKEN.search(html):
        return TOKEN.sub(lambda m: cta_html, html, count=1)
    heads = list(H2.finditer(html))
    if len(heads) >= MIN_SECTIONS:
        pos = heads[MIN_SECTIONS - 1].start()
        return html[:pos] + cta_html + html[pos:]
    return html + cta_html


@register.simple_tag(takes_context=True)
def blog_body(context, content):
    html = str(render_markdown(content))
    cta = render_to_string("blog/_cta_about.html", context.flatten())
    return mark_safe(insert_cta(html, cta))
