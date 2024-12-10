
jQuery(document).ready(function ($) {

    // FORM ADD DOMAIN
    $('#add-domain button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let site_type = form.find('input[name=type]:checked').val();
        let old_site_name = form.find('input[name=old_site_name]').val();
        let new_site_name = form.find('input[name=new_site_name]').val();
        let ssl = form.find('input[name=ssl]:checked').val();
        let apache = form.find('input[name=apache]:checked').val();

        let need_config = form.find('input[name=need_config]').is(':checked');
        let need_new_folder = form.find('input[name=need_new_folder]').is(':checked');
        let need_bd = form.find('input[name=need_bd]').is(':checked');

        new_site_name = new_site_name.replace(' ', '');
        old_site_name = old_site_name.replace(' ', '');

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if ((input_check(old_site_name, exceptions, 'Старое название сайта') || site_type == "0") &&
            input_check(new_site_name, exceptions, 'Новое название сайта')) {

            $('.cat_container').removeClass('hidden');
            form.addClass('not-touch');

            url = '/api/add_domain'
            data = {
                sitetype: site_type,
                old_site_name: old_site_name,
                new_site_name: new_site_name,
                ssl: ssl,
                apache: apache,
                need_config: need_config,
                need_new_folder: need_new_folder,
                need_bd: need_bd,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != '') {
                        alert(data);
                    }
                    else {
                        alert("Успешно")
                    }
                    $('.cat_container').addClass('hidden');
                    form.removeClass('not-touch');
                }
            });
        }
    });


    // FORM LOGIN
    $('#login-form button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        username = form.find('input[name=username]').val();
        password = form.find('input[name=password]').val();

        url = '/api/login'
        data = {
            username: username,
            password: password
        }

        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {
                if (data == "1") {
                    window.location.replace('/dashboard');
                }
                else {
                    alert(data);
                }
            }
        });
    });


    // DEL FORM
    $('#del-domain button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        site_name = form.find('input[name=site_name]').val();

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, "Название сайта")) {

            url = '/api/delete_domain'
            data = {
                site_name: site_name,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                    }
                    else {
                        alert("Успешно")
                    }
                }
            });
        }
    });


    // Create FORM
    $('#create-form button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let site_name = form.find('input[name=site_name]').val();

        var formData = new FormData();
        formData.append('sitewar', form.find('input[name=sitewar]:checked').val());
        formData.append('sitetype', form.find('input[name=sitetype]:checked').val());
        formData.append('withssl', form.find('input[name=withssl]:checked').val());
        formData.append('archive', document.getElementById("archive").files[0]);
        formData.append('apache_version', form.find('input[name=apache]:checked').val())

        formData.append('archive-type', form.find('input[name=archive-type]:checked').val())
        formData.append('site_name', site_name);
        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        alert(form.find('input[name=apache]:checked').val());

        if (input_check(site_name, exceptions, 'Название сайта')) {

            form.addClass('no-touch');
            $('.cat_container').removeClass('hidden');

            url = '/api/create_domain'
            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                    } else {
                        alert("Успешно!");
                    }

                    form.removeClass('no-touch');
                    $('.cat_container').addClass('hidden');
                }
            });
        }
    });

    //USER CREATE FORM
    $('#create-new-user button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let user_login = form.find('input[name=user_login]').val();
        let user_password = form.find('input[name=user_password]').val();
        let user_confirm_password = form.find('input[name=user_confirm_password]').val();
        let user_access = form.find('input[name=user_access]').val();

        let exceptions = ['/', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (user_password != user_confirm_password) {
            alert("Пароли не совпадают!");
        }

        else {
            if (input_check(user_login, exceptions, 'Логин')
                && input_check(user_password, exceptions, 'Пароль')) {

                form.addClass('no-touch');

                url = '/api/user/create'
                data = {
                    user_login: user_login,
                    user_password: user_password,
                    user_confirm_password: user_confirm_password,
                    user_access: user_access,
                }

                $.ajax({
                    url: url,
                    method: "POST",
                    data: data,
                    success: function (data) {
                        if (data != "") {
                            alert(data);
                        }
                        else {
                            form.find('input').val('');
                        }
                        form.removeClass('no-touch');
                    }
                });
            }
        }
    });

    //USER DELETE FORM
    $('#delete-user button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let user_login = form.find('input[name=user_login]').val();

        let exceptions = ['/', '\\', ' ', '#', '+', '=', '\n', '%'];


        if (input_check(user_login, exceptions, 'Логин')) {

            form.addClass('no-touch');

            url = '/api/user/delete'
            data = {
                user_login: user_login,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                    }
                    else {
                        form.find('input').val('');
                        alert('Успешно!');
                    }

                    form.removeClass('no-touch');
                }
            });
        }

    });

    // USER LIST
    if (window.location.pathname == '/users') {
        reload_user_list();
    }
    $('#reload-user-list-button').on('click', function () {
        reload_user_list();
    });

    function reload_user_list() {
        wrapper = $('#users .items');
        url = '/api/user/list'
        $.ajax({
            url: url,
            method: "POST",
            success: function (data) {
                if (data != "") {
                    text = ''
                    data.forEach(element => {
                        text +=
                            '<div class="item">' +
                            '<p>' + element['username'] + '</p><h6>' + element['access'] + '</h6>' +
                            '</div>'
                    });
                    wrapper.html('');
                    wrapper.append(text);
                }
            }
        });
    }

    // ADD SSL FORM
    $('#add-ssl-form button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');
        let site_name = form.find('input[name=site_name]').val();
        let certbot = form.find('input[name=certbot]').is(':checked');
        let wp_cli = form.find('input[name=wp_cli]').is(':checked');
        let nginx = form.find('input[name=nginx]').is(':checked');

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            form.addClass('no-touch');

            url = '/api/ssl/add'
            data = {
                site_name: site_name,
                certbot: certbot,
                wp_cli: wp_cli,
                nginx: nginx,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                    }
                    else {
                        alert('Успешно!');
                        form.find('input').val('');
                    }

                    form.removeClass('no-touch');
                }
            });
        }

    });

    // REMOVE SSL FORM
    $('#delete-ssl-form button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let site_name = form.find('input[name=site_name]').val();
        let certbot = form.find('input[name=certbot-del]').is(':checked');
        let wp_cli = form.find('input[name=wp_cli-del]').is(':checked');
        let nginx = form.find('input[name=nginx-del]').is(':checked');

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            form.addClass('no-touch');

            url = '/api/ssl/remove'
            data = {
                site_name: site_name,
                certbot: certbot,
                wp_cli: wp_cli,
                nginx: nginx,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                        form.find('input').val('');
                    }
                    else {
                        alert('Успешно');
                        form.find('input').val('');
                    }

                    form.removeClass('no-touch');
                }
            });
        }

    });

    // ADD FTP FORM
    $('#form-add-ftp button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let site_name = form.find('input[name=site_name]').val();

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];


        if (input_check(site_name, exceptions, 'Название сайта')) {

            form.addClass('no-touch');

            url = '/api/ftp/add'
            data = {
                site_name: site_name,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        $('.ftp-wrapper').append(data);
                        form.find('input').val('');
                    }
                    else {
                        form.find('input').val('');
                    }

                    form.removeClass('no-touch');
                }
            });
        }

    });

    // DELETE FTP FORM
    $('#form-delete-ftp button').on('click', function (e) {
        e.preventDefault();
        let form = $(this).closest('form');

        let site_name = form.find('input[name=site_name]').val();

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];


        if (input_check(site_name, exceptions, 'Название сайта')) {

            form.addClass('no-touch');

            url = '/api/ftp/remove'
            data = {
                site_name: site_name,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {
                    if (data != "") {
                        alert(data);
                    }
                    else {
                        form.find('input').val('');
                    }

                    form.removeClass('no-touch');
                }
            });
        }

    });


    // ADMIN PARSING
    $('#parse-nginx').on('click', function (e) {
        e.preventDefault();
        var it = $(this)
        it.addClass('no-touch');

        url = '/api/parser'

        $.ajax({
            url: url,
            method: "POST",
            success: function (data) {
                if (data != "") {
                    alert("Всего записано: " + data + " сайтов");
                }
                it.removeClass('no-touch');
            }
        });
    });

    // ALL DOMAINS
    if (document.location.pathname == '/all_domain') {

        get_domains('', false);

        $('#search-domains button').on('click', function (e) {
            e.preventDefault();
            var it = $(this)
            var form = it.closest('form');
            get_domains(form.find('input[name=search_input]').val(),
                form.find('#sort_revert').is(':checked')
            );
        });


        function get_domains(search_query, sort_revert) {
            var formData = new FormData();
            formData.append('search', search_query);
            formData.append('sort_revert', sort_revert);
            url = '/api/domains/get'
            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {
                    var wrapper = $('#all-domains .domains_view');
                    wrapper.html('');
                    var count = 0;
                    if (data != "") {
                        data.forEach((element) => {

                            var ssl = '';
                            var http_type = 'http://';
                            if (element['ssl_avaliable'] == 0) {
                                ssl = "Отсутствует";
                            } else {
                                http_type = 'https://';
                                ssl = "Присутствует";
                            }
                            count += 1;
                            wrapper.append(
                                "<div class='domain'>" +
                                "<a href='" + http_type + element["site_name"] + "' class='name p2' target='_blank'>" + element['site_name'] + "</a>" +
                                "<div class='decoded_name p2'>" + element['decoded_name'] + "</div>" +
                                "<div class='ssl p2'>" + ssl + "</div>" +
                                "<div class='php p2'>" + element['site_php'] + "</div>" +
                                "<div class='php p2'>" + element['site_weight'] + "мб</div>" +
                                "</div>"
                            );
                        });

                        $('#search-domains .total-sites').html('<h5> Всего найдено сайтов:' + count + '</h5>')
                    }
                    else {
                        wrapper.append('<h5>Сайтов не найдено...</h5>');
                    }
                }
            });
        }
    }



    // CREATE DOMAIN
    $('#save-domain button').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        let input_val = form.find('input').val();
        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(input_val, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/save_domain'
            data = {
                input: input_val,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {

                    console.log(data);
                    $('.cat_container').addClass('hidden');

                    var download_btn = document.createElement('a');
                    download_btn.setAttribute('href', data);
                    download_btn.setAttribute('download', data);
                    download_btn.text = 'Скачать файл';
                    form.next().append(download_btn);
                    download_btn.click();
                }
            });
        }
    });


    // AUTO UPDATE SSL
    $('#parse-ssl').on('click', function () {

        url = '/api/ssl/autoupdate'
        $.ajax({
            url: url,
            method: "POST",
            success: function (data) {
                console.log(data);
            }
        });

    });



    // SAVE BD
    $('#bd-save-form button').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        let site_name = form.find('input[name=site_name]').val();
        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/bd/save'
            data = {
                site_name: site_name,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {

                    if (data.errors != '') alert(data.errors)

                    console.log(data);
                    $('.cat_container').addClass('hidden');

                    var download_btn = document.createElement('a');
                    download_btn.setAttribute('href', data.bd);
                    download_btn.setAttribute('download', data.bd);
                    download_btn.text = 'Скачать файл';
                    form.next().append(download_btn);
                    download_btn.click();
                }
            });
        }
    });


    // LOAD BD
    $('#bd-load-form button').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        var formData = new FormData();
        let site_name = form.find('input[name=site_name]').val();
        formData.append('site_name', site_name);
        formData.append('bd_file', document.getElementById("bd_file").files[0]);

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/bd/load'
            data = {
                site_name: site_name,
            }

            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {

                    if (data != '') {
                        alert(data)
                    }
                    else {
                        alert('Успешно');
                    }

                    $('.cat_container').addClass('hidden');

                }
            });
        }
    });


    // WP REPLACE BD
    $('#bd-replace-form button').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        var formData = new FormData();
        let site_name = form.find('input[name=site_name]').val();
        let new_site_name = form.find('input[name=new_site_name]').val();
        formData.append('site_name', site_name);
        formData.append('new_site_name', new_site_name);
        formData.append('http_text', form.find('input[name=http_change]').is(':checked'))

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта') && input_check(new_site_name, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/bd/replace'

            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {

                    if (data != '') {
                        alert(data)
                    }
                    else {
                        alert('Успешно');
                    }

                    $('.cat_container').addClass('hidden');

                }
            });
        }
    });


    // DELETE BD USER
    $('#bd-delete-form .delete-user').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        var formData = new FormData();
        let site_name = form.find('input[name=site_name]').val();

        formData.append('site_name', site_name);

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/bd/delete_user'

            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {

                    if (data != '') {
                        alert(data)
                    }
                    else {
                        alert('Успешно');
                    }

                    $('.cat_container').addClass('hidden');

                }
            });
        }
    });

    // DELETE BD USER
    $('#bd-delete-form .delete-database').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        var formData = new FormData();
        let site_name = form.find('input[name=site_name]').val();

        formData.append('site_name', site_name);

        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];

        if (input_check(site_name, exceptions, 'Название сайта')) {

            $('.cat_container').removeClass('hidden');

            url = '/api/bd/delete_database'

            $.ajax({
                url: url,
                method: "POST",
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {

                    if (data != '') {
                        alert(data)
                    }
                    else {
                        alert('Успешно');
                    }

                    $('.cat_container').addClass('hidden');

                }
            });
        }
    });

    // IP CONTROLLERS
    $('#ip-ban .ban').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        let ip = form.find('input[name=ip]').val();

        url = '/api/ip_ban'

        data = {
            ip: ip
        }

        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {

                if (data != '') {
                    alert(data)
                }
                else {
                    alert('Успешно');
                }
            }
        });
    });

    $('#ip-ban .unban').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        let ip = form.find('input[name=ip]').val();

        url = '/api/ip_unban'

        data = {
            ip: ip
        }

        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {

                if (data != '') {
                    alert(data)
                }
                else {
                    alert('Успешно');
                }
            }
        });
    });


    $('#ip-ban input').on('change', function (e) {

        ip = $(this).val();
        url = 'https://www.abuseipdb.com/check/' + ip

        $('#ip-ban a.btn').attr('href', url);
    });


    // PAGE ADMIN



    url = window.location.pathname;
    if (url == '/servers') {
        view_page_list();
    }

    $('#pages-form #add-new-page').on('click', function (e) {
        e.preventDefault();

        let form = $(this.closest('form'));
        let page_name = form.find('input[name=page_name]').val();

        if (input_check(page_name, [], 'Название страницы')) {

            url = '/api/page/add_new'

            data = {
                page_name: page_name,
                textarea: '',
            }

            $.ajax({
                url: url,
                method: "POST",
                data: data,
                success: function (data) {

                    if (data != '') {
                        alert(data)
                    }
                    else {
                        alert('Успешно');
                        view_page_list();
                    }
                }
            });
        }
    });


    $('#pages-form').on('click', 'a.del', function () {

        let page_el = $(this.closest('.page-el'));
        page_name = page_el.find('.main-info p').html()

        url = '/api/page/delete_page'

        data = {
            page_name: page_name
        }
        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {

                if (data != '') {
                    alert(data)
                }
                else {
                    alert('Успешно');
                    view_page_list();
                }
            }
        });
    });


    $('#pages-form').on('click', 'a.redact', function () {

        let page_el = $(this.closest('.page-el'));
        page_name = page_el.find('.main-info p').html()
        url = '/api/page/load_page'
        $('.save').removeClass('disable');
        data = {
            page_name: page_name
        }
        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {
                let name = $('#pages-form .readctor .name h4');
                tinyMCE.activeEditor.setContent(data);

                name.html(page_name);
                view_page_list();

            }
        });
    });

    $('#pages-form').on('click', 'a.save', function () {

        let readctor = $(this.closest('.readctor'));
        page_name = readctor.find('.name h4').html();

        tinyMCE.triggerSave();
        textarea = tinyMCE.activeEditor.getContent(data);

        url = '/api/page/add_new'

        data = {
            page_name: page_name,
            textarea: textarea
        }
        $.ajax({
            url: url,
            method: "POST",
            data: data,
            success: function (data) {

                alert("Сохранено!");

                tinyMCE.activeEditor.setContent('empty...');
                let name = $('#pages-form .readctor h4');
                name.html('Выберите файл');
                $('.save').addClass('disable');
                view_page_list();

            }
        });
    });

    function view_page_list() {

        url = '/api/page/get_list'

        $.ajax({
            url: url,
            method: "POST",
            success: function (data) {
                let wrapper = $('#pages-form .page-list');
                wrapper.html('');
                data.forEach(element => {
                    wrapper.append(
                        '<div class="page-el">' +
                        ' <div class="main-info">' +
                        '<p>' +
                        element
                        + '</p>' +
                        ' </div>' +
                        '<div class="btns">' +
                        '<a class="btn redact">' +
                        'Редак.' +
                        '  </a>' +
                        '<a class="btn del">' +
                        '  Удалить' +
                        '</a>' +
                        '</div>' +
                        ' </div>'
                    );
                });
            }
        });

    }

    if (url.split('/')[1] == 'info') {

        page_name = $('#helper').html();

        if (page_name != '') {
            url = '/api/page/load_page'

            data = {
                page_name: page_name.replace('\n', '').trim()
            }

            $.ajax({
                url: url,
                data: data,
                method: "POST",
                success: function (data) {
                    let wrapper = $('.container');
                    wrapper.append(data);
                }
            });
        }
    }


    // Chown
    $('#chown-by').on('click', function () {
        let site_name = form.find('input[name=site_name]').val();
        let exceptions = ['xn-', '/', 'https', '\\', ' ', '#', '+', '=', '\n', '%'];
        let url = '/api/page/load_page';

        if (input_check(site_name, exceptions, 'Название сайта')) {
            data = {
                site_name: site_name.trim(),
            };

            $.ajax({
                url: url,
                data: data,
                method: "POST",
                success: function (data) {
                    alert(data);
                }
            });
        }
    });

    //reload server
    $('#reload-server').on('click', function () {
        let url = '/api/reload_server';
        // alert('ГОВНО');
        alert('ПИВО');
        $.ajax({
            url: url,
            data: data,
            method: "POST",
            success: function (data) {
                alert(data);
            }
        });
    });


    function input_check(input_val, exceptions, name) {
        let normal = true;
        if (input_val == '') {
            alert('Поле "' + name + '" не заполнено!');
            normal = false;
        }

        for (let el in exceptions) {
            if (input_val.includes(exceptions[el])) {
                alert('Недопустимый символ в "' + name + '" - "' + exceptions[el] + '"')
                normal = false;
                break
            }
        }

        return normal
    }

    //reload server
    $('#resrt-server').on('click', function () {
        let url = '/api/reload_server';
        // alert('ГОВНО');
        alert('Начата перезагрузка, перезагрузка сервера будет длиться мин 10');
        // $.ajax({
        //     url: url,
        //     data: data,
        //     method: "POST",
        //     success: function (data) {
        //         alert(data);
        //     }
        // });
    });


});