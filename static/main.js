let currentLanguage = "english";
let recognition;

function setLanguage(lang) {
    currentLanguage = lang;
    document.getElementById("status").innerHTML = `Listening (${lang})...`;
}

function startListening() {
    recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onresult = async function(event) {
        let transcript = event.results[event.results.length - 1][0].transcript;
        document.getElementById("result").innerHTML = `Heard: ${transcript}`;

        let res = await fetch("/process_text", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text: transcript, language: currentLanguage })
        });

        let data = await res.json();
        if (data.audio_url) {
            let audio = new Audio(data.audio_url);
            audio.play();
        }
    };

    recognition.start();
    document.getElementById("status").innerHTML = "Listening...";
}

window.onload = startListening;
