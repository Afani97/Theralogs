const recordAudio = () => {
    return  new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        const start = () => mediaRecorder.start();

        const stop = () =>
          new Promise(resolve => {
            mediaRecorder.addEventListener("stop", () => {
              const audioBlob = new Blob(audioChunks);
              const audioFile = new File([audioBlob], "audio.wav");
              resolve({ audioFile });
            });

            mediaRecorder.stop();
          });

        resolve({ start, stop });
    });
}


let recorder;
let timer = document.getElementById('stopwatch');

let hr = 0;
let min = 0;
let sec = 0;
let stoptime = true;

function startTimer() {
  timer.classList.remove("hidden");
  if (stoptime == true) {
        stoptime = false;
        timerCycle();
    }
}

function stopTimer() {
  timer.classList.add("hidden");
  if (stoptime == false) {
    stoptime = true;
  }
  resetTimer();
}

function timerCycle() {
    if (stoptime == false) {
    sec = parseInt(sec);
    min = parseInt(min);
    hr = parseInt(hr);

    sec = sec + 1;

    if (sec == 60) {
      min = min + 1;
      sec = 0;
    }
    if (min == 60) {
      hr = hr + 1;
      min = 0;
      sec = 0;
    }

    if (sec < 10 || sec == 0) {
      sec = '0' + sec;
    }
    if (min < 10 || min == 0) {
      min = '0' + min;
    }
    if (hr < 10 || hr == 0) {
      hr = '0' + hr;
    }

    timer.innerHTML = hr + ':' + min + ':' + sec;

    setTimeout("timerCycle()", 1000);
  }
}

function resetTimer() {
    timer.innerHTML = "00:00:00";
    stoptime = true;
    hr = 0;
    sec = 0;
    min = 0;
}

document.getElementById('start-recording-btn').addEventListener('click', async function(e) {
    recorder = await recordAudio();
    if (recorder !== null && myDropzone.files.length === 0) {
        recorder.start();
        document.getElementById('stop-recording-btn').classList.remove("hidden")
        document.getElementById('start-recording-btn').classList.add("hidden")
        startTimer();
    }
})

document.getElementById('stop-recording-btn').addEventListener('click', async function(e) {
    if (recorder !== null && myDropzone.files.length === 0) {
        const audio = await recorder.stop();
        myDropzone.addFile(audio.audioFile)
        stopTimer();
    }
})


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#my-dropzone", {
    url: `${window.location.origin}/main/file-upload/`,
    maxFiles: 1,
    maxFilesize: 120, // 120MB
    parallelUploads: 1,
    acceptedFiles: '.aiff,.wav,.mp3,.mp4,.m4a',
    dictDefaultMessage: 'Drop a file here to upload',
    autoProcessQueue: false,
    addRemoveLinks: true,
    uploadMultiple: false,
    init: function() {
        const submitButton = document.querySelector("#upload-btn")
        const myDropzone = this;
        submitButton.addEventListener("click", function() {
            const patientId = document.getElementById('selected-patient').value;
            if (patientId === "") {
                alert("Please select a patient to upload!")
            } else {
                myDropzone.processQueue();
            }
        });

        myDropzone.on("addedfile", function(file) {
            stopTimer();
            submitButton.classList.remove("hidden");
            document.getElementById('start-recording-btn').classList.add("hidden")
            document.getElementById('stop-recording-btn').classList.add("hidden")
        });

        myDropzone.on("maxfilesexceeded", function(file) {
            myDropzone.removeFile(file)
        });

        myDropzone.on("removedfile", function(file) {
            if (myDropzone.files.length === 0) {
                submitButton.classList.add("hidden");
                document.getElementById('start-recording-btn').classList.remove("hidden")
            }
        });

        myDropzone.on("sending", function(file, xhr, formData) {
            const patientId = document.getElementById('selected-patient').value;
            formData.append('patient-id', patientId);
            submitButton.disabled = true;
        });

        myDropzone.on("success", function(file) {
          setTimeout(function() {
            submitButton.disabled = false;
            myDropzone.removeAllFiles();
            document.getElementById('file-success-msg').classList.toggle("hidden");
            setTimeout(function() {
                document.getElementById('file-success-msg').classList.toggle("hidden");
            }, 3000);
          }, 1000);
        });
    },
})


document.getElementById('new-patient-form').addEventListener('submit', function(e) {
    e.preventDefault()
    const patientName = document.getElementById('patient-name').value;
    const patientEmail = document.getElementById('patient-email').value;

    const fd = new FormData()
    fd.append('patient-name', patientName)
    fd.append('patient-email', patientEmail)

    const csrftokenCookie = getCookie('csrftoken')

    fetch('/patient/create/', {
      method: 'POST',
      credentials: 'include',
      mode: 'same-origin',
      headers: {
        'X-CSRFToken': csrftokenCookie,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: fd
    })
    .then(async (resp) => {
        const response = await resp.json()
        if (resp.status !== 200) {
            document.getElementById('error-patient-msg').classList.toggle("hidden");
            setTimeout(function() {
                document.getElementById('error-patient-msg').classList.toggle("hidden");
            }, 3000);
        } else {
            document.getElementById('new-patient-msg').classList.toggle("hidden");
            const patientId = response.patient_id;
            document.getElementById('new-patient-form').reset();
            var option = document.createElement("option");
            option.text = patientName + " - " + patientEmail;
            option.value = patientId;
            var select = document.getElementById("selected-patient");
            select.appendChild(option);
            select.value = patientId;
            setTimeout(function() {
                document.getElementById('new-patient-msg').classList.toggle("hidden");
            }, 3000);
        }
    })
    .catch(error => console.log(error))
})