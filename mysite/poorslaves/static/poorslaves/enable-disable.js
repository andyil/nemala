$(function()
{
    $(".accept").click(function(e){
        var t = $(e.target);
        var id = t.attr('data-id');
        var checked = t.is(":checked");
        console.log(id+" "+checked);
        t.hide();
        console.log('dis');
        $.ajax("accept-reject", {
            type: 'post',
            data: {id: id, checked: checked},
            success: function(){
                console.log('en');
                t.show();
            }
        });
    });
});