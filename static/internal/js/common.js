function get_secret_cookie() {
    var r = document.cookie.match("\\b_xsrf=([^;]*)\\b");
    return r ? r[1] : undefined;
}