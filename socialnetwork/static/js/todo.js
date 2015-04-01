$(function(){
window.setInterval(function () {
    latest_id=$('#finalpost').val();
    if(latest_id != ""){
    $.ajax({
        url: "/socialnetwork/refresh_page",
        dataType : "json",
        data : {"id": latest_id},
        success: function( rendered ) {
            $("#finalpost").val(rendered['finalpost']);
            $("div#attachhere").prepend(rendered['html']);
        }
    });
    }
}, 5000);
});

$(".postsform").submit(function(){
    event.preventDefault();
    post_id = ($(this).find('.addcommentpost').data('pid'));
    commenttext = ($(this).find('#comment').val());
    $.ajax({
        url : "/socialnetwork/add-comment",
        dataType : "json",
        data : {"post_id": post_id, "commenttext": commenttext},
        success: function ( rendered ) {
            $("div#commentsection-"+post_id).parent().append(rendered['html']);
        }
    });
});

