/**
 * desqus - Commenting backend for static pages
 * Copyright (C) 2012  desqus contributors, see AUTHORS
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

var desqus = new Object();

(function (dq){
    dq.getClient = function () {
         return new XMLHttpRequest();
    };

    dq.client = new XMLHttpRequest();

    if ( ! desqus_home ) {
        alert('Can\'t find desqus_home');
    }
    dq.home = desqus_home;

    dq.render = function () {
        dq.container = document.getElementById('desqus-comments-container');

        dq.container.innerHTML = '';

        dq.formContainer = dq.makeElement('div', {
            class: 'desqus-form'});
        dq.container.appendChild(dq.formContainer);

        dq.commentContainer = dq.makeElement('ul', {
            class: 'comment-list'});

        dq.container.appendChild(dq.commentContainer);

        dq.request('/check-login', function (res, status) {
            data = res;
            dq.log(['check-login', data]);
            if (! 'OK' == data.status) {
                dq.renderRegister();
            } else {
                dq.renderForm();
            }
        });
        dq.getComments();
    };

    dq.renderRegister =  function () {
        dq.formContainer.innerHTML = '<p>You need to <a href="'
            + dq.home + '/login?next=' + encodeURIComponent(document.baseURI) + '">login</a> or <a href="' + dq.home
            + '/register">register</a> to post a comment.</p>';
    };

    dq.getComments = function () {
        dq.request('/comments', function (res, status) {
            dq.jsonData = res;
            dq.log(res);
            dq.renderComments(dq.jsonData.comments);
        }, {
            item_url: document.baseURI,
            item_title: document.title});
    };

    dq.makeElement = function (type, o, children) {
        em = document.createElement(type);

        if (o) {
            if (o.class)
                em.className = o.class;
            if (o.id)
                em.id = o.id;
            if (o.text)
                em.textContent = o.text;
            if (o.html)
                em.innerHTML = o.html;
            if (o.placeholder)
                em.placeholder = o.placeholder;
            if (o.name)
                em.name = o.name;
        }

        if (children && ! children.length)
            em.appendChild(children);
        else
            for (i in children)
                em.appendChild(children[i]);

        return em;
    };

    dq.renderComments = function (comments) {
        dq.commentContainer.innerHTML = '';
        dq.log(comments);
        for (comment in comments) {
            var comment = comments[comment];
            var container = dq.makeElement('li');

            container.appendChild(
                    dq.makeElement('p', {
                        text: comment.text,
                        class: 'comment-text'}));
            container.appendChild(
                    dq.makeElement('span', {
                        text: comment.created,
                        class: 'comment-created'}));
            container.appendChild(
                    dq.makeElement('span', {
                        text: comment.username,
                        class: 'comment-username'}));
            dq.commentContainer.appendChild(container);
        }
    };

    dq.onCommentSubmit = function (e) {
        e.preventDefault();
        dq.submitButton.disabled = true;
        dq.commentField.disabled = true;

        callback = function (res, status) {
            dq.log(res);
            dq.log(status);
            dq.submitButton.disabled = false;
            dq.commentField.disabled = false;
            dq.commentField.value = '';
            dq.getComments();
        };

        body = JSON.stringify({
            comment: dq.commentField.value,
            item: dq.jsonData.item.id});

        headers = {'Content-Type': 'application/json'};

        dq.request('/comments',
                callback,
                body,
                'POST',
                headers);
    };

    dq.renderForm = function () {
        dq.form = dq.makeElement('form', {
            id: 'desqus-comment-form'});

        dq.form.appendChild(
            dq.makeElement('div', {
                id: 'comment-field-wrapper'},
                dq.commentField = dq.makeElement('textarea', {
                    name: 'comment',
                    id: 'comment',
                    placeholder: 'Write a comment...'})));

        dq.form.appendChild(
            dq.submitButton = dq.makeElement('button', {
                text: 'Post comment'}));

        dq.form.onsubmit = dq.onCommentSubmit;

        dq.formContainer.appendChild(dq.form);
    };

    dq.request = function (uri, callback, params, method, headers) {
        client = dq.getClient();
        //$.getJSON(dq.home + '/api' + uri, callback);
        var queryString = '';

        if (! method || method == 'GET') {
            method = 'GET';
            for (param in params) {
                queryString += '&' + param + '=' + encodeURIComponent(params[param]);
            }
        } else if (method == 'POST') {
            for (header in headers) {
            }
        }
        dq.log(method + ' ' + uri);

        uri = dq.home + '/api' + uri;
        if (queryString.length) {
            uri += '?' + queryString;
        }

        client.open(method, uri, true);
        client.withCredentials = true;

        client.onreadystatechange = function () {
            switch (this.readyState) {
                case this.DONE:
                    data = null;

                    try {
                        data = JSON.parse(this.response)
                    } catch (e) {
                        dq.log(e);
                    }

                    callback(data || this.response, this.status);
                    delete client;
                    break;
                default:
                    dq.log(['readyState: ', this.readyState]);
            }
        };

        if (method == 'POST') {
            client.send(params);
        } else {
            client.send();
        }
    };

    dq.log = console.log;
})(desqus);

desqus.render();
