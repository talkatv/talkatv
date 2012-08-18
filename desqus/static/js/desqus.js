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

        dq.formContainer = document.createElement('div');
        dq.container.appendChild(dq.formContainer);

        dq.commentContainer = document.createElement('ul');
        dq.container.appendChild(dq.commentContainer);

        dq.request('/check-login', function (res, status) {
            data = JSON.parse(res);
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
            dq.jsonData = JSON.parse(res);
            dq.log(res);
            dq.renderComments(dq.jsonData.comments);

        }, {
            item_url: document.baseURI,
            item_title: document.title});
    };

    dq.renderComments = function (comments) {
        dq.commentContainer.innerHTML = '';
        dq.log(comments);
        for (comment in comments) {
            var comment = comments[comment];
            var container = document.createElement('li');
            var text = document.createElement('p');
            text.textContent = comment.text
                + ' at ' + comment.created + ' by ' + comment.username;
            container.appendChild(text);
            dq.commentContainer.appendChild(container);
        }
    };

    dq.onCommentSubmit = function (e) {
        e.preventDefault();
        dq.submitButton.disabled = true;

        callback = function (res, status) {
            dq.log(res);
            dq.log(status);
            dq.submitButton.disabled = false;
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
        dq.form = document.createElement('form');

        dq.commentField = document.createElement('textarea');
        dq.form.appendChild(dq.commentField);

        dq.submitButton = document.createElement('button');
        dq.submitButton.textContent = 'Post comment';
        dq.submitButton.onclick = dq.onCommentSubmit;
        dq.form.appendChild(dq.submitButton);

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
                    callback(this.response, this.status);
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

    dq.log = function(msg) {
        console.log(msg);
    }
})(desqus);

$(document).ready(function () {
    desqus.render();
});
