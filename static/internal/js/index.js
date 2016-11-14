$(document).ready(function () {
    $(".g-date-picker").datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        pickerPosition: "bottom-left",
        language: 'zh-CN',
        clearBtn: true
    })

    $("#search-text").keypress(function (e) {
        if (e.keyCode == 13) {
            $('#img_container').empty();
            $('#go_next input').val(0);
            search()
        }
    })

    $(window).scroll(function () {
        if ($(document).height() - $(document).scrollTop() <= document.documentElement.clientHeight) {
            search()
        }
    })

})
function popup_upload_window() {
    layer.open({
        type: 2,
        title: '文件上传',
        content: '/upload',
        area: ['1050px', '600px']
    })
}

function login(_this) {
    var username = $(_this).parent().find("input[name='username']").val()
    var password = $(_this).parent().find("input[name='password']").val()
    $.post("/login", {
            username: username, password: password
        }, function (data) {
            var response = eval('(' + data + ')');
            var message = response.message;
            if (message == "succ") {
                window.location.href = "/"
            } else {
                layer.msg(message)
            }
        }
    )
}


function assign(_this) {
    var username = $(_this).parent().find("input[name='username']").val()
    var password = $(_this).parent().find("input[name='password']").val()
    $.post("/assign_account", {
            username: username, password: password
        }, function (data) {
            var response = eval('(' + data + ')');
            var message = response.message;
            layer.msg(message)
            layer.closeAll('tips')
        }
    )
}

function check_key(event, _this, action) {
    if (event.keyCode == 13)
        if (action == "login")
            login(_this)
        else if (action == "assign")
            assign(_this)

}

function popup_login_window() {
    layer.tips('<form><input type="text" class="login_controller" placeholder=" 用户名"  name="username" style="color:#34495E" onkeypress="check_key(event, this, \'login\')"/><input class="login_controller" style="margin-top:5px;color:#34495E" placeholder=" 密码" type="password" name="password" onkeypress="check_key(event, this, \'login\')"/> <input value="登 录" type="button" onclick="login(this)" class="header-button" style="width:150px; height:32px;margin-top:3px;"/></form>', "#login-button", {
        tips: 3,
        closeBtn: true,
        time: 0
    })
}

function popup_assign_account_window() {
    layer.tips('<form action="/assign_account" method="post"><input type="text" onkeypress="check_key(event, this, \'assign\')" class="login_controller" placeholder=" 用户名" name="username" style="color:#34495E"/><input class="login_controller" style="margin-top:5px;color:#34495E" onkeypress="check_key(event, this, \'assign\')" placeholder=" 密码" type="password" name="password"/> <input type="button" onclick="assign(this)"  value="分 配" class="header-button" style="width:150px; height:32px;margin-top:3px;"/></form>', "#assign_button", {
        tips: 2,
        closeBtn: true,
        time: 0
    })
}


function search() {
    var search_text = $("#search-text").val();
    var start_date = $("#search-wrapper > section input:first-child").val();
    var end_date = $("#search-wrapper > section input:last-child").val();
    $.post('/search', {
        "search_keys": search_text,
        "start_date": start_date,
        "end_date": end_date,
        "page": function () {
            var value = $("#go_next input").val();
            return value
        }
    }, function (data) {
        var response = eval('(' + data + ')');
        var message = response.message;
        if (message == "succ") {
            for (var x = 0; x < response.data.length; x++) {
                var img_container = document.getElementById("img_container");
                img_container.appendChild(build_vessel(response.data[x]))
            }

            $('#img_container > section').on('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
                $(this).removeClass('animated');
                $(this).addClass("image_vessel_h")
            });

            $("#go_next").css("visibility", "visible");
            $("#go_next input").val(parseInt($("#go_next input").val()) + 1)
        } else {
            $("#go_next").css("visibility", "hidden");
            layer.msg(message)
        }
    })
}

function build_vessel(picture) {
    var image_vessel = document.createElement("section");
    image_vessel.className = "image_vessel animated flipInX";

    var a = document.createElement("a");
    a.href = "/picture/" + picture._id.$oid;

    var image_span = document.createElement("div");
    image_span.className = "image_span";


    var img = document.createElement("img");
    img.src = "/image/" + picture._id.$oid;
    img.className = "image";

    var description_span = document.createElement("span");
    description_span.className = "description_span"

    var p_name = document.createElement("p");
    p_name.innerHTML = picture.file_name;

    var p_tag = document.createElement("p");
    p_tag.innerHTML = "标签:" + picture.tag;
    p_tag.className = "ready_display"

    var p_upload_date = document.createElement("p");
    p_upload_date.innerHTML = "上传日期:" + picture.upload_date;
    p_upload_date.className = "ready_display"

    description_span.appendChild(p_name)
    description_span.appendChild(p_tag)
    description_span.appendChild(p_upload_date)

    image_span.appendChild(img)
    image_span.appendChild(description_span)

    a.appendChild(image_span)

    image_vessel.appendChild(a)

    return image_vessel
}