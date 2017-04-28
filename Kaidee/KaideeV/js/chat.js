// //FOR TESTING ONLY
UserID = null;
// USERNAME = "Newy";

//DO NOT DELETE THIS
currentChatID = 0;
latestMessage = 0;
chatIDAvaiable = [];
notiDict = {};

getSession();

$(document).ready(function() {
    //document.getElementById('#minim_chat_window').click();

    $("#notification").hide();
    $('#chatpage, #to_contact').hide();

    $(document).on('click', '.panel-heading span.icon_chat_tolist', function (e) {
        $('#contactpage').fadeIn();
        $('#chatpage, #to_contact').hide();
    });

    $(document).on('click', '.panel-heading span.icon_chat_minimize', function (e) {
        var $this = $(this);
        if (!$this.hasClass('panel-collapsed')) {
            $this.parents('.panel').find('.panel-body, .panel-footer').slideUp();
            $this.addClass('panel-collapsed');
            $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
        } else {
            $this.parents('.panel').find('.panel-body, .panel-footer').slideDown();
            $this.removeClass('panel-collapsed');
            $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
        }
    });

    $(document).on('click', '#new_chat', function (e) {
        var size = $( ".chat-window:last-child" ).css("margin-left");
        size_total = parseInt(size) + 400;
        alert(size_total);
        var clone = $( "#chat_window_1" ).clone().appendTo( ".container" );
        clone.css("margin-left", size_total);
    });


    $(document).on('click', '#btn-chat', function (e) {
        sendMessage();
    });

    $(document).on('keypress', '#btn-input', function (e) {
        if (e.keyCode == 13) {
            sendMessage();
            return false; // prevent the button click from happening
        }
    });

});

//Origin: 1 = Send, 2 = Receive
function addMsgRow(isSender, isHistory, msg, timestamp){
    dt = new Date(timestamp).toLocaleString();
    console.log(msg);
    if(isSender){
        var $newmsg = $('<div class="row msg_container base_sent" style="display: none;"><div class="col-md-10 col-xs-10"><div class="messages msg_sent"><p>' + msg + '</p></div><time class="time_send">' + dt + '</time></div></div>');
    }else{
        var $newmsg = $('<div class="row msg_container base_receive" style="display: none;"><div class="col-md-10 col-xs-10"><div class="messages msg_receive"><p>' + msg + '</p></div><time class="time_receive">'+ dt + '</time></div></div>');
    }
    if(isHistory){
        $(".msg_container_base").prepend($newmsg);
    }else{
        $(".msg_container_base").append($newmsg);
    }
    $newmsg.fadeIn();
}


function createDeal(id, img, itemName, user, isBuy, chatID){
    if(isBuy){
        statuspic = "img/buy_icon.png";
    }else{
        statuspic = "img/sell_icon.png";
    }
    console.log(chatID);
    // $("#itemList").append('<a href="#" onclick="getDealInfo(' + id + ')"><div class="well contact"><div class="col-md-2 col-xs-2 info_content"><img class="statuspic" src="' + statuspic + '"></img></div><div class="col-md-2 col-xs-2 info_content"><img class="itempic" src="' + img + '"></img></div><div class="col-md-6 col-xs-6 info_content"><h4>' + itemName + '</h4><h5>' + user +'</h5></div></div></a>');
    $("#itemList").append('<a href="#" onclick="getDealInfo(' + id + ')"><div class="well contact"><div class="col-md-2 col-xs-2 info_content"><img class="statuspic" src="' + statuspic + '"></img></div><div class="col-md-2 col-xs-2 info_content"><img class="itempic" src="' + img + '"></img></div><div class="col-md-6 col-xs-6 info_content"><h5 class="infotext">' + itemName + '</h5><h5 class="infotext">' + user +'</h5></div><div class="col-md-2 col-xs-2 info_content"><span class="badge" id="deal_chat_' + chatID + '"></span></div></div></a>');
    console.log(notiDict["noti_chat_"+chatID]);
}

function getDealList(UserID){
    /* THE USER ID WILL BE SENT TO THE SERVER AND GET LIST OF DEALS MADE BY THE USER WHICH
    INCLUDE DEAL ID, PRODUCT IMAGE, PRODUCT NAME, AND IN-CONTACT USER NAME */
    $.ajax({
         type: 'GET',
         url: 'http://snowywords2.ddns.net:5000/get_deal_list/' + UserID,
         data: {
            UserID: UserID
         },
         success: function(response){
            $('#status').text("ONLINE"); //FOR DEBUGGING
            for(var i = 0; i < response.length; i++){
                if(response[i].Display_name == USERNAME){
                    isBuy = false;
                }else{
                    isBuy = true;
                }
                chatIDAvaiable[i] = response[i].ChatID[0];
                createDeal(response[i].ItemID, response[i].ItemImage, response[i].ItemName, response[i].Display_name, isBuy, response[i].ChatID[0]);
            }
         },
         error: function(){
            $('#status').text("OFFLINE"); //FOR DEBUGGING
         }
    });
}

function getDealInfo(ItemID){
    // GET PRODUCT IMAGE, PRODUCT NAME, INCONTACT USER ID + NAME + PROFILE PIC ACCORDING TO DEAL ID
    $.ajax({
         type: 'GET',
         url: 'http://snowywords2.ddns.net:5000/get_deal_info/' + ItemID,
         data: {
            ItemID: ItemID
         },
         success: function(response){
            $('#contactpage').hide();
            $('#chatpage, #to_contact').fadeIn();
            $(".msg_container_base").empty();
            $('#productImg').attr('src', response[0].ItemImage); //CHANGE PRODUCT IMAGE
            $('#productName').text(response[0].ItemName); //CHANGE PRODUCT NAME
            $('#targetImg').attr('src', response[0].ProfilePic); //CHANGE INCONTACT_USER_NAME
            $('#targetName').text(response[0].Display_name); //CHANGE INCONTACT_PROFILE_PIC
            getMessageHistory(response[0].ChatID[0]);
            currentChatID = response[0].ChatID[0];
         },
         error: function(){
            console.log("Cannot obtain the information");
         }
    });
}

//WILL ADD USER ID LATER
function getMessageHistory(ChatID){
    /* GET ALL CHAT HISTORY ACCORDING TO DEAL ID. THE MESSAGE SHOULD INCLUDE:
    USER ID (ORIGIN OF EACH MESSAGE), MESSAGE, TIMESTAMP */
    $.ajax({
         type: 'GET',
         url: 'http://snowywords2.ddns.net:5000/get_message_history/' + ChatID,
         data: {
            ChatID: ChatID
         },
         success: function(response){
            if(response != 'No data found at the index'){
              latestMessage = response[0].MessageID;
                for(var i = 0; i < response.length; i++){
                    if(UserID == response[i].SenderID){
                        addMsgRow(true, true, response[i].Text, response[i].Timestamp);
                    }else{
                        addMsgRow(false, true, response[i].Text, response[i].Timestamp);
                        markAsRead(response[i].MessageID);
                    }
                }
                scrollChatBoxDown();
            }else{
                //DO NOTHING
            }
         },
         error: function(){
            window.alert("Cannot obtain the messages");
         }
    });
}

function sendMessage(){
    var dt = new Date().getTime();
    var msg = $("#btn-input").val();
    data = {
        "chatID": currentChatID,
        "senderID": UserID,
        "message": msg,
        "timestamp": dt
    };
    $.ajax({
        type: 'POST',
        url: 'http://snowywords2.ddns.net:5000/send_message',
        contentType:"application/json",
        dataType: "json",
        data: JSON.stringify(data),
        success: function(){
            getLatestMessage(currentChatID);
            $("#btn-input").val("");
        },
        error: function(){
            //DO NOTHING
        }
    });
}

function getLatestMessage(ChatID){
    /* GET LATEST MESSAGE FROM THE SERVER. CLIENT-SIDE WILL CALL THIS MESSAGE REPEATLY TO LOOK FOR UPDATE
    IF THERE'S AN UPDATE, RETURN THE LATEST MESSAGE. ELSE, RETURN ANYTHING "SMALL" (AND PLZ TELL ME WHAT IT IS) */
    $.ajax({
        type: 'GET',
        url: 'http://snowywords2.ddns.net:5000/get_latest_msg/' + ChatID,
        data: {
            ChatID: ChatID
        },
        success: function(response){
            if(response[0].MessageID != latestMessage){
                latestMessage = response[0].MessageID;
                if(response[0].SenderID == UserID){
                    addMsgRow(true, false, response[0].Text, response[0].Timestamp);
                }else{
                    addMsgRow(false, false, response[0].Text, response[0].Timestamp);
                }
            }
            if($("#chat-textbox").is(":visible")){
              if(response[0].IsRead == 0 && response[0].SenderID != UserID){
                markAsRead(response[0].MessageID);
              }
                scrollChatBoxDown();
            }
        },
        error: function(){
            //DO NOTHING
        }
    });
}

function getUserData(id){
    $.ajax({
        type: 'GET',
        url: 'http://snowywords2.ddns.net:5000/users/' + id,
        data: {
            UserID: id
        },
        success: function(response){
            if(response != 'No data found at the index'){
                return response[0];
            }else{
                return response;
            }
        },
        error: function(){
            //DO NOTHING
        }
    });

}

function getDisplayName(id){
    info = getUserData(id).Display_name;
    if(response != 'No data found at the index'){
        return info.Display_name;
    }else{
        return info;
    }
}

function checkNotification(){
    temp = 0;
    for(var key in notiDict) {
        if(notiDict.hasOwnProperty(key)){
             temp += notiDict[key];
        }
    }
    if(temp == 0){
        $("#notification").hide();
    }else{
        $("#notification").show();
        $("#notification").text(temp);
    }
}

function checkNotiForDeal(chatid){
    temp = notiDict["noti_chat_"+chatid];
    if(temp == 0){
        $("#deal_chat_" + chatid).hide();
    }else{
        $("#deal_chat_" + chatid).show();
        $("#deal_chat_" + chatid).text(temp);
    }
}

function countUnread(chatid){
    $.ajax({
        type: 'GET',
        url: 'http://snowywords2.ddns.net:5000/count_unread/' + chatid,
        success: function(response){
            if(response != 'No data found at the index'){
                if(notiDict["noti_chat_"+chatid] != response[0].UnreadQty){
                    notiDict["noti_chat_"+chatid] = response[0].UnreadQty;
                }
                checkNotification();
            }else{
                return response;
            }
        },
        error: function(){
            //DO NOTHING
        }
    });
}

function markAsRead(msgID){
    data = {
         "messageID": msgID
    };
    $.ajax({
        type: 'POST',
        url: 'http://snowywords2.ddns.net:5000/set_as_read',
        contentType:"application/json",
        dataType: "json",
        data: JSON.stringify(data),
        success: function(){
            console.log(msgID + " has been readed")
        },
        error: function(){
            //DO NOTHING
        }
    });
}

function getSession(){

  console.log("GET SESSION")
  // $.getJSON('http://snowywords2.ddns.net:5000/session_data', function(data) {
  $.getJSON('http://localhost:5000/session_data', function(data) {
      if(data == 404){
          UserID = null;
      }else{
          UserID = data.UserID;
          USERNAME = data.Display_name;
          getDealList(UserID);
          console.log(UserID);
          setInterval(function(){
              checkNotification();
              getLatestMessage(currentChatID);
              for(var i = 0; i < chatIDAvaiable.length; i++){
                  countUnread(chatIDAvaiable[i]);
                  checkNotiForDeal(chatIDAvaiable[i]);
              }
          }, 1000);
      }
  });
}

function scrollChatBoxDown(){
    $('#chat-textbox').scrollTop($('#chat-textbox').get(0).scrollHeight);
}
