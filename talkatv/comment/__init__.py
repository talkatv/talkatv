# talkatv - Commenting backend for static pages
# Copyright (C) 2012  talkatv contributors, see AUTHORS
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from markdown import Markdown

from lxml.html.clean import Cleaner

MARKDOWN = Markdown(output_format='xhtml5')

HTML_CLEANER = Cleaner(
    scripts=True,
    javascript=True,
    comments=True,
    style=True,
    links=True,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=True,
    annoying_tags=True,
    allow_tags=[
        'div', 'b', 'i', 'em', 'strong', 'p', 'ul', 'ol', 'li', 'a', 'br',
        'pre', 'code', 'blockquote'],
    remove_unknown_tags=False,  # can't be used with allow_tags
    safe_attrs_only=True,
    add_nofollow=True,  # for now
    host_whitelist=(),
    whitelist_tags=set())


def parse_comment(comment):
    if comment:
        html = MARKDOWN.convert(comment)
        clean_html = HTML_CLEANER.clean_html(html)
        return clean_html
    else:
        return ''
