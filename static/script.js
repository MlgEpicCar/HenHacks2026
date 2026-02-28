function openModal() {
  document.getElementById("popup").classList.add("active");
}

function closeModal() {
  document.getElementById("popup").classList.remove("active");
}

window.onclick = function(event) {
  const modal = document.getElementById("popup");
  if (event.target === modal) {
    modal.classList.remove("active");
  }
}