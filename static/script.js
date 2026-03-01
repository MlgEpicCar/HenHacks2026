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

    // send to server for persistence
    fetch("/add_goal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value })
    })
        .then(res => {
            if (!res.ok) throw res;
            return res.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const goalDiv = document.createElement("div");
            goalDiv.classList.add("goals");
            goalDiv.dataset.goalId = data.id;

            const p = document.createElement("p");
            p.classList.add("goaltxt");
            p.textContent = data.text;

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.classList.add("goal-checkbox");
            if (data.completed) checkbox.checked = true;

            goalDiv.appendChild(p);
            goalDiv.appendChild(checkbox);

            const container = document.getElementById("goals_Container") || document.querySelector(".goals_container");
            const addGoalWrapper = container.querySelector(".add-goal-wrapper");
            if (addGoalWrapper) {
                container.insertBefore(goalDiv, addGoalWrapper);
            } else {
                container.appendChild(goalDiv);
            }
        })
        .catch(err => {
            console.error("Failed to add goal", err);
            alert("Could not save goal. Are you logged in?");
        });

    input.value = "";
}
