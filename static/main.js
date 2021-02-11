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
    url: "file-upload/",
    maxFiles: 1,
    maxFilesize: 50, // 50MB
    parallelUploads: 1,
    acceptedFiles: '.wav,.mp3,.mp4',
    dictDefaultMessage: 'Drop a file here to upload',
    autoProcessQueue: false,
    addRemoveLinks: true,
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

        myDropzone.on("sending", function(file, xhr, formData) {
            const patientId = document.getElementById('selected-patient').value;
            formData.append('patient-id', patientId);
        });

        myDropzone.on("complete", function(file) {
          setTimeout(function() {
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

const sendButtons = document.getElementsByClassName('send-email-btn');
for (var i = 0; i < sendButtons.length; i++) {
  sendButtons[i].addEventListener('click', function(e) {
    e.preventDefault()

    const id = e.target.id

    fetch(`resend-email/${id}/`, {
      method: 'GET',
      credentials: 'include',
      mode: 'same-origin',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
    })
    .then(resp => resp.json())
    .then(resp => {
        document.getElementById('email-sent-msg').classList.toggle("hidden");
        setTimeout(function() {
            document.getElementById('email-sent-msg').classList.toggle("hidden");
        }, 3000);
    })
  });
}