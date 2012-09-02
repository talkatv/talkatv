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

from flask import g, render_template, flash

from talkatv.decorators import require_active_login
from talkatv.site.forms import SiteForm
from talkatv.models import Site, Item
from talkatv import app, db


@app.route('/site/add', methods=['GET', 'POST'])
@require_active_login()
def add_site():
    form = SiteForm()

    if form.validate_on_submit():
        site = Site(g.user, form.domain.data)

        items = Item.query.filter(Item.url.ilike('%{0}%'.format(
            form.domain.data)))

        for item in items.all():
            item.site = site
            db.session.commit()

        flash('''Site added, {0} items registered
        as belonging to the domain'''.format(items.count()))

        db.session.add(site)
        db.session.commit()

    return render_template('talkatv/site/add.html', form=form)
