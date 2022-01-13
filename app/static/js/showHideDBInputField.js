$(document).ready(function() {
    showHideField();
});


function showHideField() {
    let box_value = $("#connector_f").val();
    if (box_value === "csv") {
        $('#db_settings').hide();
        // $('#dbServer_p').hide();
        // $('#dbUser_p').hide();
        // $('#dbPword_p').hide();
        // $('#dbName_p').hide();
        // $('#dbPort_p').hide();
        $("#upload_csv").show();
    } 
    else if (box_value === "db") {
        $('#db_settings').show();
        // $('#dbServer_p').show();
        // $('#dbUser_p').show();
        // $('#dbPword_p').show();
        // $('#dbName_p').show();
        // $('#dbPort_p').show();
        $("#upload_csv").hide();
    }
}