$(document).ready(function() {
    showHideSchemaField();
});

function showHideSchemaField() {
    var db_selected = {{db_selected}};
    console.log(db_selected);
    $('#db_schema').hide();
}