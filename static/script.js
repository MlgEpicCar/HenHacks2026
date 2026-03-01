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
    const priorityInput = document.getElementById("priorityInput");
    const value = input.value.trim();
    const priority = parseInt(priorityInput.value) || 3;

    if (value === "") return;

    // send to server for persistence
    fetch("/add_goal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value, priority: priority })
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
            goalDiv.dataset.priority = data.priority;

            const p = document.createElement("p");
            p.classList.add("goaltxt");
            p.textContent = data.text;

            const badge = document.createElement("span");
            badge.classList.add("priority-badge");
            badge.title = "Priority";
            badge.textContent = "XP: " + data.priority; // example: 1 XP per priority level

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.classList.add("goal-checkbox");
            if (data.completed) checkbox.checked = true;

            goalDiv.appendChild(p);
            goalDiv.appendChild(badge);
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
    priorityInput.value = "3";
}

// context-menu handler for deleting
document.addEventListener("DOMContentLoaded", function() {
    const goalsContainer = document.getElementById("goals_Container") || document.querySelector(".goals_container");
    if (!goalsContainer) return; // fallback if container doesn't exist
    
    goalsContainer.addEventListener("contextmenu", function(e) {
        // only react if right-click on a goal div, not the add button
        const goalDiv = e.target.closest(".goals");
        if (!goalDiv || goalDiv.classList.contains("add-goal-wrapper")) return;

        e.preventDefault();
        const text = goalDiv.querySelector(".goaltxt")?.textContent || "this goal";
        if (!confirm(`Delete goal: '${text}'? You won't be able to recover it or gain xp from it.`)) return;

        const id = goalDiv.dataset.goalId;
        if (!id) {
            goalDiv.remove(); // just remove if no id
            return;
        }

        fetch("/delete_goal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: id })
        })
        .then(res => {
            if (!res.ok) throw res;
            return res.json();
        })
        .then(data => {
            if (data.success) goalDiv.remove();
            else alert(data.error || "Could not delete");
        })
        .catch(err => {
            console.error("Delete request failed", err);
            alert("Error deleting goal");
        });
    });

    // checkbox toggle handler (delegated)
    goalsContainer.addEventListener("change", function(e) {
        const cb = e.target;
        if (!cb.classList.contains("goal-checkbox")) return;
        const goalDiv = cb.closest(".goals");
        if (!goalDiv) return;
        const id = goalDiv.dataset.goalId;
        const completed = cb.checked;
        fetch("/toggle_goal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: id, completed: completed })
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
            if (data.xp) {
                const xpSpan = document.querySelector(".xp");
                if (xpSpan) {
                    // parse current xp and add
                    const curr = parseInt(xpSpan.textContent) || 0;
                    const newXp = curr + data.xp;
                    xpSpan.textContent = newXp + " xp";
                    const levelSpan = document.querySelector(".level");
                    if (levelSpan) {
                        levelSpan.textContent = "Level " + Math.floor(newXp / 10);
                    }
                }
            }
        })
        .catch(err => {
            console.error("Toggle request failed", err);
            alert("Error updating goal status");
        });
    });

    // ensure existing badges show XP text regardless of previous rendering
    goalsContainer.querySelectorAll(".priority-badge").forEach(b => {
        const text = b.textContent.trim();
        const num = parseInt(text.replace(/[^0-9]/g, "")) || 0;
        // if it doesn't already start with XP, rewrite
        if (!text.startsWith("XP")) {
            b.textContent = "XP: " + (num);
        }
    });
});