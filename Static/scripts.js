function get_page(name, bypass = false) {
    if (!page_urls.hasOwnProperty(name)) {alert("Invalid URL");return;}
    if (current_page == name && !bypass) {return;}
    $.ajax({
        type: "GET",
        url: page_urls[name],
        headers: {'X-CSRFToken': csrf_token},
        success: function (response) {
            root.html(response.content);
            $('title').html(response.title);
            $('.navbar-brand').html(response.heading);
        },
        complete: function () {
            refactor_screen()
            current_page = name
        }
    })
}

function get_modal(name, id = null, type = null) {
    if (!modal_urls.hasOwnProperty(name)) {alert("Invalid URL");return;}
    $.ajax({
        type: "GET",
        url: modal_urls[name],
        headers: {'X-CSRFToken': csrf_token},
        data: {
            id:id, type: type
        },
        success: function (response) {
            modal.html(response.content)
        },
        complete: function () {
            modal.modal('show')
            init_modal()
            current_dialog = name
        }
    })
}

function ubah_status(id, type, action, param = null) {
    const msg_start = ["Lunaskan ", "Selesaikan ", "Kembalikan ke Draft "]
    const message = msg_start[action] + (type===0? "Transaksi ini?" : "Purchase Order ini?")
    if (!confirm(message)) {return;}

    const url = [util_urls['lunaskan'], util_urls['selesaikan'], util_urls['kembali_ke_draft']]

    $.ajax({
        type: "POST",
        url: url[action],
        headers: {'X-CSRFToken': csrf_token},
        data: {
            id:id, type: type, param:param
        },
        complete: function () {
            modal.modal('hide')
            get_page(current_page, true)
        }
    })
}

function refactor_screen() {
    init_popover()
    init_tooltip()
    pad_document()
    resize_screen()
}

function init_item_list() {
    if (localStorage.getItem('timestamp') == null ||
        new Date() > new Date(localStorage.getItem('timestamp'))) {
        $.getJSON(util_urls['get_item_list'], {csrfmiddlewaretoken: csrf_token}, set_item_list)
        return
    }
    if (item_list == null) {
        item_list = JSON.parse(localStorage.getItem('item_list'))
    }
}

function set_item_list(response) {
    localStorage.setItem('item_list', JSON.stringify(response.item_list));
    localStorage.setItem('timestamp', new Date().toString());

    item_list = response.item_list
}

function init_modal() {
    tooltip_list.forEach((e) => e.hide())
    init_popover(modal)
    init_tooltip(modal)
}

function init_popover(parent = null) {
    if (parent) {
        const parent_triggers = parent.find('[data-bs-toggle="popover"]').toArray()
        const parent_elements = [...parent_triggers].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

        popover_list.concat([...parent_elements])
    } else {
        popover_list.forEach((e) => e.dispose())

        const popover_t_list = root.find('[data-bs-toggle="popover"]').toArray()
        popover_list = [...popover_t_list].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    }
}

function init_tooltip(parent = null)
{
    if (parent) {
        const parent_triggers = parent.find('[data-bs-toggle="tooltip"]').toArray()
        const parent_elements = [...parent_triggers].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        tooltip_list.concat([...parent_elements])
    } else {
        tooltip_list.forEach((e) => e.dispose())

        const tooltip_t_list = root.find('[data-bs-toggle="tooltip"]').toArray()
        tooltip_list = [...tooltip_t_list].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    }
}

function pad_document() {
    const filler = $("#filler")
    const header_height = ($('#header').outerHeight() > 100? 100 : $('#header').outerHeight())
    const footer_height = $('#footer').outerHeight()
    if ($('#root').outerHeight() < window.innerHeight) {
        filler_height = window.innerHeight - $('#root').outerHeight() - header_height - footer_height
        filler.css("height", (filler_height + "px"));
    } else{ filler.css("height", "0px") }
}

function resize_screen() {
    root.find('table.dt_table').each(function () {
        $(this).DataTable().destroy()
    })

    if ($(window).width() >= 992) {
        $('.min').each(function () {
            $(this).show()
        })
    } else {
        $('.min').each(function () {
            $(this).hide()
        })
    }

    root.find('table.dt_table').each(function () {
        $(this).DataTable(dt_settings)
    })
}

function init_dt(parent, use_regular = false) {
    parent.find('table.dt_table').each(function () {
        if($(this).DataTable.isDataTable())
        {
            $(this).DataTable().destroy()
        }
        $(this).DataTable((use_regular? dt_settings : dt_min_settings))
    })
}

// $(window).resize(function(){
//     resize_screen()
// })

$(function () {
    init_item_list()
    refactor_screen()
});