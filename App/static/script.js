// static/script.js

let draggedItem = null;

document.querySelectorAll(".draggable").forEach(item => {
    item.addEventListener("dragstart", function () {
        draggedItem = this;
    });
});

document.querySelectorAll(".dropzone").forEach(zone => {

    zone.addEventListener("dragover", function (e) {
        e.preventDefault();
    });

    zone.addEventListener("drop", function () {

        this.innerHTML = draggedItem.innerHTML;

        const submissionId = draggedItem.dataset.id;
        const slot = this.parentElement.dataset.slot;

        // send to backend
        fetch("/assign-slot", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                submission_id: submissionId,
                slot: slot
            })
        });

    });
});
