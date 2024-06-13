// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
    getDatabase,
    ref,
    push,
    set,
    update,
    remove,
    onChildAdded,
    onChildRemoved,
    onChildChanged,
}
    from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
// ##############################API#←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←api
    authDomain: "chiburi-iot.firebaseapp.com",
    // databaseURL: "https://chiburi-iot-default-rtdb.firebaseio.com/",//remote用
    projectId: "chiburi-iot",
    storageBucket: "chiburi-iot.appspot.com",
    messagingSenderId: "837706859775",
    appId: "1:837706859775:web:ac30ba099d366f2538f8ca"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);
const dbRef = ref(db, "chat");
const dbRef_raspStatus = ref(db, "/led_status");
const sensTempHumi_ref = ref(db, "/sensTempHumi");

$('#send').on('click', function () {
    const msg = {
        uname: $('#uname').val(),
        text: $('#text').val(),
    }
    console.log(msg);
    const newPostRef = push(dbRef);//ユニークキーを生成
    set(newPostRef, msg);
});

onChildAdded(dbRef, function (data) {
    const msg = data.val();
    const key = data.key;
    //let h = `<p id=${key}>`;
    let h = `<p id="${key}">`;
    h += msg.uname;
    h += `<br>`;
    h += `<span contentEditable="true" id="${key}_update">${msg.text}</span>`;
    h += `<span class="remove" data-key="${key}" style="hover: {color: red}">[削除]</span>`;
    h += `<span class="update" data-key="${key}">[編集完了]</span>`;
    h += '</p>';

    // let o = `<option data-key="${key}"></option>`
    $('#output').prepend(h);
    // $('#meas_select').append()

});


//削除イベント
$('#output').on('click', '.remove', function () {
    const key = $(this).attr('data-key');
    const remove_item = ref(db, `chat/${key}`);
    remove(remove_item) //dbの`chat/${key}`という場所のデータを削除
});

//更新イベント
$('#output').on('click', '.update', function () {
    const key = $(this).attr('data-key');
    const update_item = ref(db, `chat/${key}`);
    update(update_item, {
        text: $(`#${key}_update`).html()
    });//dbの`chat/${key}`という場所のデータのtextを $(`#${key}_update`).html()に書き換え。
});

//削除処理がfireBaseで実行されたらイベント発生！
onChildRemoved(dbRef, (data) => {
    $(`#${data.key}`).remove();//dom操作関数。
});

//更新処理がfirebase側で実行されたらイベント発生。
onChildChanged(dbRef, (data) => {
    $(`#${data.key}_update`).html(data.val().text);
    $(`#${data.key}_update`).fadeOut(800).fadeIn(800);
});



onChildAdded(dbRef_raspStatus, function (data) {
    const inf = data.val();
    const key = data.key;
    let h = `<div class="raspPost" id="${key}_raspPost" >`;
    h += `<p id="${key}">`;
    h += `名称:${inf.raspName}`;
    h += `<br>`;
    h += `ID:${inf.raspId}`;
    h += `<br>`;
    h += `<span contentEditable="true" id="${key}_rz_txt">${inf.raspText}</span>`;
    // h += `<span class="rz_remove" data-key="${key}" style="hover: {color: red}">[削除]</span>`;
    h += `<span class="rz_update" data-key="${key}">[編集完了]</span>`;
    h += `<br>`;
    h += `<span class="status" id="${key}_status">${inf.status}</span>`;
    h += '</p>';
    h += `<button class="onButton"  data-key="${key}">On</button>`;
    h += `<button class="offButton"  data-key="${key}">Off</button>`;
    h += '</div>';

    let o = `<option value="${key}" data-key="${key}">${inf.raspName}→ID:${key}</option>`

    $('#raspberryPi_list_parent').prepend(h);
    $('#meas_select').append(o);

});
const newPostRef_rasp = push(dbRef_raspStatus);//ユニークキーを生成
$('#addRaspButton').on('click', function () {
    const whichRasp = {
        status: 'off',
        raspId: $('#raspId').val(),
        raspName: $('#raspName').val(),
        raspText: $('#raspText').val(),
        raspText: $('#raspText').val(),
    }
    // dbRef_raspStatus.set('on');
    console.log(whichRasp);
    set(newPostRef_rasp, whichRasp);
});

//On/Off更新イベント
$('#raspberryPi_list_parent').on('click', '.onButton', function () {
    const key = $(this).attr('data-key');
    console.log(key)
    const update_item = ref(db, `/led_status/${key}`);
    update(update_item, {
        status: 'on',
    });//dbの`/led_status/${key}`という場所のデータのstatusを 'on'に書き換え。
    addDataTable(key)
});
$('#raspberryPi_list_parent').on('click', '.offButton', function () {
    const key = $(this).attr('data-key');
    const update_item = ref(db, `/led_status/${key}`);
    update(update_item, {
        status: 'off',
    });//dbの`/led_status/${key}`という場所のデータのstatusを 'off'に書き換え。
});

//更新処理がfirebase側で実行されたらイベント発生。
onChildChanged(dbRef_raspStatus, (data) => {
    console.log(`#${data.key}_status`)
    console.log(`#${data.key}_rz_txt`)
    $(`#${data.key}_status`).html(data.val().status);
    $(`#${data.key}_rz_txt`).html(data.val().raspText)
    $(`#${data.key}_status`).fadeOut(800).fadeIn(800);
    $(`#${data.key}_rz_txt`).fadeOut(800).fadeIn(800);
});

//ラズパイテキスト情報更新イベント[編集完了]について
$('#raspberryPi_list_parent').on('click', '.rz_update', function () {
    const key = $(this).attr('data-key');
    // console.log(key)
    const update_item = ref(db, `/led_status/${key}`);
    update(update_item, {
        raspText: $(`#${key}_rz_txt`).html(),
    });//dbの`/led_status/${key}`という場所のデータのstatusを 'on'に書き換え。
});

//ラズパイの削除イベント[削除]に関して。
$('#raspberryPi_list_parent').on('click', '.rz_remove', function () {
    const key = $(this).attr('data-key');
    const remove_item = ref(db, `/led_status/${key}`);
    remove(remove_item) //dbの`/led_status/${key}`という場所のデータを削除
});



//削除処理がfireBaseで実行されたらイベント発生！
onChildRemoved(dbRef_raspStatus, (data) => {
    //raspPostのdivごと削除
    $(`#${data.key}_raspPost`).remove();//dom操作関数。
});



// Main部分  初期値
onChildAdded(sensTempHumi_ref, function (data) {
    const msg = data.val();
    const key = data.key;
    //let h = `<p id=${key}>`;
    let h = `<p id="${key}">`;
    h += `<br>`;
    h += `<span contentEditable="true" id="${key}_update">ラズパイID：${msg.raspKey}</span>`;
    h += `<br>`;
    h += `<span contentEditable="true">観測気温：${Number(msg.sensTemp).toFixed(2)}℃</span>`;
    h += `<br>`;
    h += `<span contentEditable="true">観測湿度：${Number(msg.sensHumi).toFixed(2)}%</span>`;
    h += `<br>`;
    h += `<span contentEditable="true">API天気：${msg.apiWeather}</span>`;
    h += `<br>`;
    h += `<span contentEditable="true">API気温：${msg.apiTemp}℃</span>`;
    h += `<br>`;
    h += `<span contentEditable="true">API天気：${msg.apiHumi}%</span>`;
    h += '</p>';
    $('#sensResult').prepend(h);

});

//見たいデータ表示
$('#meas_btn').on('click', function () {
    let select_key = $('#meas_select').val();
    // console.log(`select_key:${select_key}`)
    // const key = $('#meas_select').attr('data-key');
    $('#sensResult').empty();
    onChildAdded(sensTempHumi_ref, function (data) {
        const msg = data.val();
        const key = data.key;
        // console.log(`msg.raspKey:${msg.raspKey}`)
        if (msg.raspKey == select_key) {
            // console.log('ok')
            let h = `<p id="${key}">`;
            h += `<br>`;
            h += `<span contentEditable="true" id="${key}_update">ラズパイID：${msg.raspKey}</span>`;
            h += `<br>`;
            h += `<span contentEditable="true">観測気温：${Number(msg.sensTemp).toFixed(2)}℃</span>`;
            h += `<br>`;
            h += `<span contentEditable="true">観測湿度：${Number(msg.sensHumi).toFixed(2)}%</span>`;
            h += `<br>`;
            h += `<span contentEditable="true">API天気：${msg.apiWeather}</span>`;
            h += `<br>`;
            h += `<span contentEditable="true">API気温：${msg.apiTemp}℃</span>`;
            h += `<br>`;
            h += `<span contentEditable="true">API天気：${msg.apiHumi}%</span>`;
            h += '</p>';
            console.log(h)
            $('#sensResult').prepend(h);
        }
    });

});






// もし、onを押したラズパイid(key)のデータ:sensTempHumiだったら
// function addDataTable(rasp_key) {
//     constdata = ref(db, "/sensTempHumi");
//     console.log(data);
//     // console.log(ref(db, "/sensTempHumi"));
//     const filteredData = {};
//     for (const key in data) {
//         if (data[key].raspKey === rasp_key) {
//             filteredData[key] = data[key];

//         }
//     }


//     console.log(filteredData);
//     // console.log(raspKey);
//     // for
//     // if (raspKey == sensTempHumi_ref.data) {

//     // }


// }


/*
        // ラズパイ遠隔処理
                // ????????
                const onButton = document.getElementById('onButton');
                const offButton = document.getElementById('offButton');

                // Firebase Realtime Database???
                // const dbRef_raspStatus = firebase.database().ref('/led_status');

                // ????????????????????
                onButton.addEventListener('click', () => {
                    dbRef_raspStatus.set('on');
                });

                offButton.addEventListener('click', () => {
                    dbRef_raspStatus.set('off');
                });
*/


// ==========================mytable============================



// ====================↑↑↑mytable↑↑↑======================
