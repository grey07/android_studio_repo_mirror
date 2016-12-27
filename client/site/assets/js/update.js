$("#update_repo_progress").hide();

var refresh_table = function() {
    $("#source_table").empty();
    $.ajax({
        url: '/get_source_table',
        type: 'GET',
        success: function(data) {
            $("#source_table").append(data);
        }
    });
};

$("#source_table").ready(function() {
    refresh_table();
});

$("#refresh_table").click(function() {
    refresh_table();
});

$("#update_repo").change(function() {
    var formData = new FormData();
    formData.append('file', this.files[0]);
    $("#update_repo_progress").show();

    $.ajax({
        url: '/push_update',
        type: 'POST',
        xhr: function() {
            var xhr = $.ajaxSettings.xhr();
            if (xhr.upload) {
                xhr.upload.addEventListener('progress', function(evt) {
                    var percent = (evt.loaded / evt.total) * 100;
                    $("#update_repo_progress").find(".bar").width(percent + "%");
                }, false);
            }
            return xhr;
        },
        success: function(data) {
            $("#update_repo_progress").hide();
            $("#update_repo").closest("form").trigger("reset");
        },
        error: function() {
            $("#update_repo_progress").hide();
            $("#update_repo").closest("form").trigger("reset");
        },
        data: formData,
        cache: false,
        contentType: false,
        processData: false
    }, 'json');
});
