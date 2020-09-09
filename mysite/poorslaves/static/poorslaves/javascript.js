
function add_row()
{
    var rows = $("tr.answer-row").length;
    var html = $("#templaterow").html()
    var id = 'row-'+rows;
    console.log("id: %s", id);
    $("tbody").append("<tr id='"+id+"' class='answer-row'>"+html+"</tr>");
    var selects = $("#"+id+" select");
    for(var i=0; i < selects.length; i++)
    {
        var select = $(selects[i]);
        if (select.attr("id")) select.attr("id", select.attr("id")+"-"+rows);
        if (select.attr("name")) select.attr("name", select.attr("name")+"-"+rows);
    }
    $('#'+id+" select.max").select2({maximumSelectionLength: 2});
    $('#'+id+" select:not(.max)").select2();

    toggleDisabled();
    return id;
}

function toggleDisabled()
{
    var rows = $("tr.answer-row").length;
    if (rows > 2)
    {
        $("#remove").removeAttr('disabled');
    }
    else
    {
        $("#remove").attr('disabled', true);
    }

    if (rows > 4)
    {
        $("#submit").removeAttr('disabled');
    }
    else
    {
        $("#submit").attr('disabled', true);
    }
}

function remove_last_row()
{
    var answers = $(".answer-row");
    var last = $(answers[answers.length - 1]);
    last.remove();
    toggleDisabled();
    return false;
}

function add_court_row()
{
    var id = add_row();
    $("#"+id+" .judgebased").remove();
    $("#"+id+" .courtbased").show();
    $($("#"+id+" .select2").get(0)).remove();
    $($("#"+id+" br").get(0)).remove();
    $("#"+id).addClass("court-row");

}

function add_judge_row()
{
    var id = add_row();
    $("#"+id+" .judgebased").show();
    $("#"+id+" .courtbased").remove();

    var ids = ['disposition', 'outcome', 'winner', 'issue'];
    var row_number = $(".answer-row").length-1;
    for(var i=0; i < ids.length; i++)
    {
        var selector = "#"+ids[i];
        console.log("selector %s", selector);
        var court_value = $(selector+"-1").val();
        console.log("val %o", court_value);
        var dest = selector+"-"+row_number;
        console.log("dest %s", dest);
        $(dest).val(court_value);
        $(dest).trigger('change');
    }
    return false;
}

$(document).ready(function() {

    $("#add").click(add_judge_row);
    $("#remove").click(remove_last_row);
    $("#submit").attr('disabled', true);
    add_court_row();
});

