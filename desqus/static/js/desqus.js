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
