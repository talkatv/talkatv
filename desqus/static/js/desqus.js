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
    dq.client = new XMLHttpRequest();

    if ( ! desqus_home ) {
        alert('Can\'t find desqus_home');
    }
    dq.home = desqus_home;

    dq.render = function () {
        dq.container = document.getElementById('desqus-comments-container');
        dq.container.innerHTML = 'Loading...';

        dq.request('/comments', function (res, status) {
            dq.container.innerHTML = '<p>This content has been loaded from '
                + dq.home + ' via CORS:</p><pre>' + res + '</pre>';
        });
    };

    dq.request = function (url, callback, method) {
        //$.getJSON(dq.home + '/api' + url, callback);

        if ( ! method ) {
            method = 'GET';
        }
        dq.client.open(method, dq.home + '/api' + url, true);
        dq.client.withCredentials = true;

        dq.client.onreadystatechange = function () {
            switch (this.readyState) {
                case this.DONE:
                    callback(this.response, this.status);
                    break;
                default:
                    dq.log(['readyState: ', this.readyState]);
            }
        };

        dq.client.send();
    };

    dq.log = function(msg) {
        console.log(msg);
    }
})(desqus);

$(document).ready(function () {
    desqus.render();
});
