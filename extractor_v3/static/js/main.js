jQuery(document).ready(function ($) {
    $(document).on('click', '#dashboard .menu_list', function (e) {
        e.preventDefault();

        var currentBtn = $(e.currentTarget);

        if (!currentBtn.hasClass('active')) {
            var oldBtn = currentBtn.siblings('.menu_list.active');
            var dataId = currentBtn.attr('data-id');

            var oldTab = $('#dashboard .items_content .text_list.active');
            var newTab = $(`#dashboard .items_content .text_list[id="${dataId}"]`);

            currentBtn.addClass('active');
            oldBtn.removeClass('active');

            oldTab.removeClass('active');
            newTab.addClass('active');
        }
    });

    // dashboard -> faq 
    var contents = $('.accordeon-content');
    var titles = $('.accordeon-title');
    titles.on('click', function () {
        var title = $(this);
        contents.filter(':visible').slideUp(function () {
            $(this).prev('.accordeon-title').removeClass('is-opened');
        });

        var content = title.next('.accordeon-content');

        if (!content.is(':visible')) {
            content.slideDown(function () { title.addClass('is-opened') });
        }
    });

    $('.accordeon .item__title').on('click', function () {
        $(this).toggleClass('active');
        $(this).siblings('.item__childs').slideToggle();
    });


    function init() {
        // Открывашки в меню
        $(".sub-menu").each(function () {
            $(this).next().toggle('hidden');
        });

        $(".sub-menu").on('click', function () {
            $(this).next().toggle('hidden');
        });
        // =================

        $('label').on('click', function () {
            if ($(this).attr("id") == "radio-mini") {
                $('#test').addClass('scale-none');
            }
            else {
                $('#test').removeClass('scale-none');
            }
        });
    }

    init();


    $('#add-domain input[name=old_site_name]').closest('.input-holder').addClass('hidden');
    $('#add-domain input[name=type]').on('click', function () {
        if ($(this).attr('value') == '0') {
            $('#add-domain input[name=old_site_name]').closest('.input-holder').addClass('hidden');
        }
        else {
            $('#add-domain input[name=old_site_name]').closest('.input-holder').removeClass('hidden');
        }
    });

    // CATS LOANDER

    $('input[type=submit]').on('click', function e() {
        console.log($(this).attr('клик'));
        if ($(this).attr('value') == 'Начать') {
            $('#add-domains .cat_container').removeClass('hidden');
        }
        else {
            $('#add-domains .cat_container').addClass('hidden');
        }
    });

    // $('.input[type=submit]').click(function() {
    //     $('.cat_container').removeClass('hidden');
    // });

    // $('.input[type=submit]').click(function() {
    //     $('.cat_container').addClass('hidden');
    // });

    $('button.guest').on('click', function () {
        $('#login .image').addClass('opened');
    });

    $('.opener').on('click', function () {
        $(this).prev().toggleClass('opened');
    });

    ($("#add-domain input[name=type]")).on('click', function () {
        if ($('#add-domain input[name=type]:checked').val() == '1') {
            $('#add-domain input[name=ssl]').closest('.input-holder').css('display', 'none')
        }
        else {
            $('#add-domain input[name=ssl]').closest('.input-holder').css('display', 'flex')
        }
    });

    ($("#create-form input[name=sitewar]")).on('click', function () {
        if ($('#create-form input[name=sitewar]:checked').val() == '1') {
            $('#create-form input[name=withssl]').closest('.input-holder').css('display', 'none')
        }
        else {
            $('#create-form input[name=withssl]').closest('.input-holder').css('display', 'flex')
        }
    });

    $('#create-form input[name=archive]').on('change', function () {
        $(this).closest('.input-holder').next().removeClass('hidden');
    });

    $('#http_change').on('click', function () {
        if ($(this).is(':checked')) {https://compliment-dent.ru/
            $(this).closest('.input-holder').find('h5').html('Менять с HTTP[S] на HTTP[]');
        } else {
            $(this).closest('.input-holder').find('h5').html('Менять с HTTP[] на HTTP[S]');
        }
    });


    $('#servers .tab').on('click', function () {
        let tab_id = $(this).attr('tab-id');
        $('#servers .panel').addClass('hidden');
        $('#servers .panel-id-' + tab_id).removeClass('hidden');

    });

    // FOR MENU
    url = '/api/page/get_list'
    $.ajax({
        url: url,
        method: "POST",
        success: function (data) {
            let wrapper = $('#sub-menu:first');
            data.forEach(element => {
                wrapper.append(
                    "<li>"+
                    "<a href='/info/" + element + ".html'>" + element + "</a>"+
                    "</li>"
                );
            });
        }
    });

});

