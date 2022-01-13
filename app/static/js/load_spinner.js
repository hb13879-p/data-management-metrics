$(document).ready(function() {
    $("#spinner").hide();
    $("#runButton").click(function() {
        console.log("clicked");
        $(this).hide();
        $("#spinner").show()
        $.post('/download', {name: "testdata"}, function(data, status) {
            $("#runButton").show();
            $("#spinner").hide();
            console.log(status);
            const blob = new Blob([data], {type: "octet/stream"}),
                url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = fileName;
            a.click();
            window.URL.revokeObjectURL(url);
        });
    });
});