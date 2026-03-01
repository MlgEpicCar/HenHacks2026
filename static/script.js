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
function addItem() {
    const input = document.getElementById("itemInput");
    const value = input.value.trim();

    if (value === "") return;

    // create goal structure similar to existing markup
    const goalDiv = document.createElement("div");
    goalDiv.classList.add("goals");

    const p = document.createElement("p");
    p.classList.add("goaltxt");
    p.textContent = value;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.classList.add("goal-checkbox");

    goalDiv.appendChild(p);
    goalDiv.appendChild(checkbox);

    const container = document.getElementById("goals_Container") || document.querySelector(".goals_container");
    // Find the Add Goal button (first .goals child with a button inside) and insert before it
    const addGoalButton = container.querySelector(".goals:has(button)");
    if (addGoalButton) {
        container.insertBefore(goalDiv, addGoalButton);
    } else {
        container.appendChild(goalDiv);
    }

    input.value = "";
}
