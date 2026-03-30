<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset = UTF-8">

    <link href="https://yastatic.net/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet">
    <link type="text/css" href="https://yandex.st/highlightjs/8.0/styles/github.min.css" rel="stylesheet"/>

    <script src="https://yandex.st/highlightjs/8.0/highlight.min.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>

    <style>
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>

<h3>Status: {{response.status_code}}</h3>

{% if response.headers %}
<h4>Headers</h4>
{% for key, value in response.headers.items() %}
<pre><code><b>{{key}}</b>: {{value}}</code></pre>
{% endfor %}
{% endif %}

{% if body %}
<h4>Body</h4>
<pre><code>{{body}}</code></pre>
{% endif %}

</body>
</html>
