console.log("Synchrophasor live data dashboard")

const socket = new WebSocket('ws://' + window.location.host + '/ws/udp/');

console.log(socket)
socket.onmessage = function(e) {
    console.log('Server:' + e.data);
};
socket.onopen = function(e) {
    socket.send(JSON.stringify({
        'message':'Hello from client',
    }));
};

// socket.onerror
// socket.onclose