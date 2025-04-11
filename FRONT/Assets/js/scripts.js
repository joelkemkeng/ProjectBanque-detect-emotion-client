let isRecording = false;
let audioContext = null;
let socket = null;
let liveStreamActive = false;

let cibles_component_top_sensation = null

const loaderContainer = document.getElementById("loader-container");

// Initialisation des WebSocket
function initWebSocket() {
  socket = new WebSocket("ws://127.0.0.1:8000/ws/audio"); // Remplacez avec votre URL WebSocket

  socket.onmessage = (event) => {
    const data_parse = JSON.parse(event.data);
    let data_score_sensational = data_parse.data;

    loaderContainer.style.display = "none";


    document.getElementById("score-joie-component").classList.remove("highlight");
    document.getElementById("score-amour-component").classList.remove("highlight");
    document.getElementById("score-tristesse-component").classList.remove("highlight");
    document.getElementById("score-surprise-component").classList.remove("highlight");
    document.getElementById("score-peur-component").classList.remove("highlight");
    document.getElementById("score-colere-component").classList.remove("highlight");
    

    // Verification du message serveur 
    if (data_parse.typeResponse === "alert") {
      console.log("\n \n Message recue du serveur  :: ");
      console.log(data_parse.data);
      
    }else if (data_parse.typeResponse === "resultSensationScan"){
        
        console.log("Message du serveur top_sensation : data_parse.top_sensation :: ", data_parse.top_sensation);
        console.log("Message du serveur : data_parse :: ", data_parse);

        document.getElementById("score-colere").textContent = `${data_score_sensational.colere} / 5`;
        document.getElementById("score-peur").textContent = `${data_score_sensational.peur} / 5`;
        document.getElementById("score-joie").textContent = `${data_score_sensational.joie} / 5`;
        document.getElementById("score-amour").textContent = `${data_score_sensational.amour} / 5`;
        document.getElementById("score-tristesse").textContent = `${data_score_sensational.tristesse} / 5`;
        document.getElementById("score-surprise").textContent = `${data_score_sensational.surprise} / 5`;

        let topsensation = "score-"+data_parse.top_sensation+"-component";
        cibles_component_top_sensation = document.getElementById(topsensation);
        if (cibles_component_top_sensation) {
            // Ajout de la classe pour mettre en surbrillance
            cibles_component_top_sensation.classList.add("highlight");
          }
        
    } else{
        console.log("Message du serveur :", event.data);
 
    }

   
  };

  socket.onopen = () => console.log("WebSocket connecté");
  socket.onclose = () => console.log("WebSocket déconnecté");
}


function init_state() {
    
    if (cibles_component_top_sensation) {
        // Ajout de la classe pour mettre en surbrillance
        cibles_component_top_sensation.classList.remove("highlight");
      }

      document.getElementById("score-colere").textContent = `0 / 5`;
      document.getElementById("score-peur").textContent = `0 / 5`;
      document.getElementById("score-joie").textContent = `0 / 5`;
      document.getElementById("score-amour").textContent = `0 / 5`;
      document.getElementById("score-tristesse").textContent = `0 / 5`;
      document.getElementById("score-surprise").textContent = `0 / 5`;

      loaderContainer.style.display = "none";

     

}


// Gestion de l'enregistrement audio
async function startRecording() {

    // Démarrage WebSocket
    initWebSocket();



  const recordingCircle = document.querySelector(".recording-circle");
  isRecording = true;
  recordingCircle.classList.add("active");

  // Configuration AudioContext
  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;

  // Récupérer le flux audio
  audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const source = audioContext.createMediaStreamSource(audioStream);
  source.connect(analyser);

  visualizeAudio(analyser);





   // Création du MediaRecorder pour envoyer les chunks audio au serveur
   mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });
  
   // À chaque disponibilité d'un chunk (ici, toutes les 1 seconde), on l'envoie au serveur
   mediaRecorder.ondataavailable = (event) => {
     if (event.data && event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
       // On envoie le chunk en tant que données binaires
       console.log('donnee envoyer au serveur ::  '+event.data+ '       //  TAILLE :' + event.data.size);
       socket.send(event.data);
     }
   };
   
   // Démarrer l'enregistrement avec un intervalle de 1 seconde
   mediaRecorder.start(1000);


}




function stopRecording() {


    loaderContainer.style.display = "block";


  const recordingCircle = document.querySelector(".recording-circle");
  isRecording = false;
  recordingCircle.classList.remove("active");

    // Arrêter MediaRecorder pour stopper l'envoi de chunks
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
      }

  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }

  // Envoi d'une requête au serveur WebSocket
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ action: "stop-recording" }));
  }

   // Libérer le micro
   if (audioStream) {
    audioStream.getTracks().forEach((track) => track.stop());
    audioStream = null;

    let intensity_reset = 0.5
    const recordingCircle = document.querySelector(".recording-circle");
    recordingCircle.style.transform = `scale(${intensity_reset})`;
    recordingCircle.style.boxShadow = `0 0 25px 5px #0f3460`;
  }
}

// Visualisation des données audio
function visualizeAudio(analyser) {


  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function draw() {
    if (!isRecording) return;

    // Récupérer les données de fréquence audio
    analyser.getByteFrequencyData(dataArray);

    // Calculer l'intensité moyenne
    const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;

    // Définir une échelle minimale pour les pulsations
    const minScale = 1; // État de base
    const maxScale = 1.5; // État maximal

    // Seuil pour considérer un silence (20 ou moins)
    const silenceThreshold = 20;
    const intensity = avg > silenceThreshold 
      ? Math.min(minScale + avg / 256, maxScale) 
      : minScale;

    // Appliquer l'échelle calculée à l'élément
    const recordingCircle = document.querySelector(".recording-circle");
    recordingCircle.style.transform = `scale(${intensity})`;
    recordingCircle.style.boxShadow = `0 0 ${intensity * 20}px ${intensity * 10}px #00f2fe`;


    // Afficher l'intensité dans la console pour diagnostic
    console.log(`Intensité sonore : ${avg.toFixed(2)}, Échelle : ${intensity.toFixed(2)}`);

    // Demander un nouveau dessin
    requestAnimationFrame(draw);
  }

  draw();


}




// JS : Gérer le switcher
/*
document.getElementById("live-switch").addEventListener("change", (event) => {
    const isLive = event.target.checked;
  
    if (isLive) {
      console.log("Analyse en direct activée !");
      liveStreamActive = true;
      // Ajoutez ici la logique pour activer l'analyse en direct
    } else {
      console.log("Analyse en direct désactivée !");
      liveStreamActive = false;
      // Ajoutez ici la logique pour désactiver l'analyse en direct
    }
  }); */

// Initialisation des événements
document.getElementById("start-btn").addEventListener("click", () => {
  startRecording();
  document.getElementById("start-btn").disabled = true;
  document.getElementById("stop-btn").disabled = false;
});

document.getElementById("stop-btn").addEventListener("click", () => {
  stopRecording();
  document.getElementById("start-btn").disabled = false;
  document.getElementById("stop-btn").disabled = true;
});

// Démarrage WebSocket
initWebSocket();
