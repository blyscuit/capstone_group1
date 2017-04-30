//DO NOT DELETE THIS
currentChatID = 0;
latestMessage = 0;
chatIDAvaiable = [];
notiDict = {};

$(document).ready(function() {

    var UserID = null;
    getSession();

    $("#notification").hide();
    $('#chatpage, #to_contact').hide();

    $(document).on('click', '.panel-heading span.icon_chat_tolist', function (e) {
        $('#contactpage').fadeIn();
        $('#chatpage, #to_contact').hide();
        e.stopPropagation();
    });

    $(document).on('click', '.panel div.top-bar', function (e) {
        var $this = $(this);
        if (!$this.hasClass('panel-collapsed')) {
            $this.parents('.panel').find('.panel-body, .panel-footer').slideUp();
            $this.addClass('panel-collapsed');
        } else {
            $this.parents('.panel').find('.panel-body, .panel-footer').slideDown();
            $this.removeClass('panel-collapsed');
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


function createDeal(img, itemName, user, isBuy, chatID){
    if(isBuy){
        statuspic = "img/buy_icon.png";
    }else{
        statuspic = "img/sell_icon.png";
    }
    // $("#itemList").append('<a href="#" onclick="getDealInfo(' + id + ')"><div class="well contact"><div class="col-md-2 col-xs-2 info_content"><img class="statuspic" src="' + statuspic + '"></img></div><div class="col-md-2 col-xs-2 info_content"><img class="itempic" src="' + img + '"></img></div><div class="col-md-6 col-xs-6 info_content"><h4>' + itemName + '</h4><h5>' + user +'</h5></div></div></a>');
    $("#itemList").append('<a href="#" onclick="getDealInfo(' + chatID + ')"><div class="well contact"><div class="col-md-2 col-xs-2 info_content"><img class="statuspic" src="' + statuspic + '"></img></div><div class="col-md-2 col-xs-2 info_content"><img class="itempic" src="' + img + '"></img></div><div class="col-md-6 col-xs-6 info_content"><h5 class="infotext">' + itemName + '</h5><h5 class="infotext">' + user +'</h5></div><div class="col-md-2 col-xs-2 info_content"><span class="badge" style="display:none" id="deal_chat_' + chatID + '"></span></div></div></a>');
}

function getDealList(){
    /* THE USER ID WILL BE SENT TO THE SERVER AND GET LIST OF DEALS MADE BY THE USER WHICH
    INCLUDE DEAL ID, PRODUCT IMAGE, PRODUCT NAME, AND IN-CONTACT USER NAME */
    $.ajax({
         type: 'GET',
         url: './get_deal_list',
         success: function(response){
            for(var i = 0; i < response.length; i++){
                if(response[i].BuyerID == UserID){
                    isBuy = true;
                    name = response[i].SellerName;
                }else{
                    isBuy = false;
                    name = response[i].BuyerName;
                }
                chatIDAvaiable[i] = response[i].ChatID;
                createDeal(response[i].ItemImage, response[i].ItemName, name, isBuy, response[i].ChatID);
            }
         },
         error: function(){
            window.alert("Cannot obtain lists");
         }
    });
}

function getDealInfo(ChatID){
    // GET PRODUCT IMAGE, PRODUCT NAME, INCONTACT USER ID + NAME + PROFILE PIC ACCORDING TO DEAL ID
    $.ajax({
         type: 'GET',
         url: './get_deal_info/' + ChatID,
         data: {
            ChatID: ChatID
         },
         success: function(response){
            $('#contactpage').hide();
            $('#chatpage, #to_contact').fadeIn();
            $(".msg_container_base").empty();
            $('#productImg').attr('src', response[0].ItemImage);
            $('#productName').text(response[0].ItemName);
            if(response[0].BuyerID == 0 || response[0].SellerID == 0){
                $('#targetImg').attr('src', '');
                $('#targetName').text('DELETED USER');
            }else if(response[0].BuyerID == UserID){
                //IF USER IS THE BUYER
                $('#targetImg').attr('src', response[0].SellerPic);
                $('#targetName').text(response[0].SellerName);
            }else{
                //IF USER IS THE SELLER
                $('#targetImg').attr('src', response[0].BuyerPic);
                $('#targetName').text(response[0].BuyerName);
            }
            getMessageHistory(ChatID);
            currentChatID = ChatID;
         },
         error: function(){
            window.alert("Cannot obtain information");
         }
    });
}

//WILL ADD USER ID LATER
function getMessageHistory(ChatID){
    /* GET ALL CHAT HISTORY ACCORDING TO DEAL ID. THE MESSAGE SHOULD INCLUDE:
    USER ID (ORIGIN OF EACH MESSAGE), MESSAGE, TIMESTAMP */
    delete notiDict["noti_chat_"+ChatID];
    $.ajax({
         type: 'GET',
         url: './get_message_history/' + ChatID,
         data: {
            ChatID: ChatID
         },
         success: function(response){
            if(response != '404'){
              latestMessage = response[0].MessageID;
                for(var i = 0; i < response.length; i++){
                    if(UserID == response[i].SenderID){
                        addMsgRow(true, true, response[i].Text, response[i].Timestamp);
                    }else{
                        addMsgRow(false, true, response[i].Text, response[i].Timestamp);
                        markAsRead(response[i].MessageID);
                    }
                }
                checkNotification();
                checkNotiForDeal(ChatID);
                scrollChatBoxDown();
            }else{
                //DO NOTHING
            }
         },
         error: function(){
            window.alert("Cannot obtain message history");
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
        url: './send_message',
        contentType:"application/json",
        dataType: "json",
        data: JSON.stringify(data),
        success: function(){
            $("#btn-input").val("");
            getLatestMessage(currentChatID);
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
        url: './get_latest_msg/' + ChatID,
        data: {
            ChatID: ChatID
        },
        success: function(response){
            if(response != 404){
                for(var i = response.length - 1; i >= 0; i--){
                    if(response[i].MessageID > latestMessage){
                        latestMessage = response[i].MessageID;
                        if(response[i].SenderID == UserID){
                            addMsgRow(true, false, response[i].Text, response[i].Timestamp);
                        }else{
                            addMsgRow(false, false, response[i].Text, response[i].Timestamp);
                        }
                        scrollChatBoxDown();
                    }
                    if($("#chatpage").is(":visible")){
                        if(response[i].SenderID != UserID){
                            markAsRead(response[i].MessageID);
                        }
                    }
                }
            }
        },
        error: function(){
            //DO NOTHING
        }
    });
}

function checkNotification(){
    temp = 0;
    for(var key in notiDict) {
        if(notiDict.hasOwnProperty(key)){
             temp += notiDict[key];
        }
    }
    if(temp == 0 || temp == undefined){
        $("#notification").hide();
    }else{
        $("#notification").show();
        $("#notification").text(temp);
    }
}

function checkNotiForDeal(chatid){
    if(notiDict["noti_chat_"+chatid] == 0 || notiDict["noti_chat_"+chatid] == undefined){
        $("#deal_chat_" + chatid).hide();
    }else{
        $("#deal_chat_" + chatid).show();
        $("#deal_chat_" + chatid).text(notiDict["noti_chat_"+chatid]);
    }
}

function countUnread(chatid){
    $.ajax({
        type: 'GET',
        url: './count_unread/' + chatid,
        success: function(response){
            for(var i = 0; i < response.length; i++){
                if(UserID != response[i].SenderID){
                    if(notiDict["noti_chat_"+chatid] != response[i].UnreadQty){
                        notiDict["noti_chat_"+chatid] = response[i].UnreadQty;
                        if(notiDict["noti_chat_"+chatid] == 0){
                            delete notiDict["noti_chat_"+chatid];
                        }
                    }else if(response == 404){
                        delete notiDict["noti_chat_"+chatid];
                    }
                }
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
        url: './set_as_read',
        contentType:"application/json",
        dataType: "json",
        data: JSON.stringify(data),
        success: function(){
            //NOTHING
        },
        error: function(){
            //NOTHING
        }
    });
}

function getSession(){

  console.log("GET SESSION")
  $.getJSON('./session_data', function(data) {
      if(data == 404){
        UserID = null;
        var $minus = $('.panel-heading span.icon_chat_minimize')
        $minus.parents('.panel').find('.panel-body, .panel-footer').hide();
        $minus.addClass('panel-collapsed');
        $minus.removeClass('glyphicon-minus').addClass('glyphicon-plus');
      }else{
        UserID = data.UserID;
        USERNAME = data.Display_name;
        getDealList();
        setInterval(function(){
            getLatestMessage(currentChatID);
            for(var i = 0; i < chatIDAvaiable.length; i++){
              countUnread(chatIDAvaiable[i]);
              checkNotiForDeal(chatIDAvaiable[i]);
            }
            checkNotification();
        }, 5000);
      }
  });
}

function startChat(itemID){
  console.log('create new chat for'+itemID+""+UserID)
    $.ajax({
        type: 'GET',
        url: './start_chat/' + itemID,
        success: function(response){
          if(response=='403'||response=='404'){
            alert('Please try again.');
          }else{
            newChatID = response[0].ChatID;
            if(chatIDAvaiable.indexOf(newChatID) == -1){
                chatIDAvaiable.push(newChatID);
            }
            $("#itemList").empty();
            getDealList();
            getDealInfo(newChatID);
          }
        },
        error: function(){

        }
    });
}

function scrollChatBoxDown(){
    $('#chat-textbox').scrollTop($('#chat-textbox').get(0).scrollHeight);
}