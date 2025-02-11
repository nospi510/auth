document.addEventListener("DOMContentLoaded", function () {
    let video = document.getElementById("webcam");
    let canvas = document.getElementById("canvas");
    let captureBtn = document.getElementById("capture-btn");
    let faceInput = document.getElementById("face_image");
    let statusMessage = document.getElementById("status-message");

    // Accès à la webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
        })
        .catch((err) => {
            console.error("Erreur accès caméra :", err);
            alert("Impossible d'accéder à la caméra. Vérifiez vos autorisations.");
        });

    // Capture de l'image
    captureBtn.addEventListener("click", function () {
        let context = canvas.getContext("2d");
        let newWidth = 320;
        let newHeight = 240;

        canvas.width = newWidth;
        canvas.height = newHeight;

        context.drawImage(video, 0, 0, newWidth, newHeight);

        // Vérifier si l'image capturée est valide
        let faceData = canvas.toDataURL("image/jpeg", 0.5);
        if (!faceData || faceData.length < 100) {
            alert("Échec de la capture. Essayez à nouveau.");
            return;
        }

        faceInput.value = faceData;
        statusMessage.textContent = "Image capturée avec succès !";
    });
});
