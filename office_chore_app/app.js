const TEAM_KEY = "office-chore-team";
const CHORE_KEY = "office-chore-items";

const teamForm = document.getElementById("team-form");
const memberInput = document.getElementById("member-name");
const teamList = document.getElementById("team-list");

const choreForm = document.getElementById("chore-form");
const choreTitle = document.getElementById("chore-title");
const choreAssignee = document.getElementById("chore-assignee");
const choreDate = document.getElementById("chore-date");
const choreStart = document.getElementById("chore-start");
const choreEnd = document.getElementById("chore-end");
const choreRepeat = document.getElementById("chore-repeat");
const choreList = document.getElementById("chore-list");

const defaultTeam = ["Alex", "Sam", "Jordan"];

const state = {
  team: load(TEAM_KEY, defaultTeam),
  chores: load(CHORE_KEY, []),
};

const calendar = new FullCalendar.Calendar(document.getElementById("calendar"), {
  initialView: "timeGridWeek",
  height: "100%",
  nowIndicator: true,
  editable: false,
  selectable: false,
  headerToolbar: {
    left: "prev,next today",
    center: "title",
    right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
  },
  events: choresToEvents(state.chores),
});
calendar.render();

hydrate();

teamForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const name = memberInput.value.trim();
  if (!name) return;
  if (state.team.includes(name)) {
    memberInput.setCustomValidity("This member already exists.");
    memberInput.reportValidity();
    return;
  }

  memberInput.setCustomValidity("");
  state.team.push(name);
  persist();
  renderTeam();
  memberInput.value = "";
});

choreForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!choreAssignee.value) {
    alert("Add a team member before creating chores.");
    return;
  }

  const id = crypto.randomUUID();
  const item = {
    id,
    title: choreTitle.value.trim(),
    assignee: choreAssignee.value,
    date: choreDate.value,
    start: choreStart.value,
    end: choreEnd.value,
    repeat: choreRepeat.value,
  };

  if (!item.title || !item.date || !item.start || !item.end) return;

  if (`${item.date}T${item.end}` <= `${item.date}T${item.start}`) {
    alert("End time must be after start time.");
    return;
  }

  state.chores.push(item);
  persist();
  refreshChores();
  choreForm.reset();
  choreDate.value = today();
  choreStart.value = "09:00";
  choreEnd.value = "09:30";
});

function hydrate() {
  if (!state.team.length) state.team = [...defaultTeam];
  choreDate.value = today();
  choreStart.value = "09:00";
  choreEnd.value = "09:30";
  renderTeam();
  refreshChores();
}

function renderTeam() {
  choreAssignee.innerHTML = "";
  teamList.innerHTML = "";

  if (!state.team.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No members available";
    choreAssignee.append(option);
    choreAssignee.disabled = true;
  } else {
    choreAssignee.disabled = false;
    state.team.forEach((member) => {
      const option = document.createElement("option");
      option.value = member;
      option.textContent = member;
      choreAssignee.append(option);

      const li = document.createElement("li");
      const span = document.createElement("span");
      span.textContent = member;
      const removeButton = button("Remove", "remove", () => removeMember(member));
      li.append(span, removeButton);
      teamList.append(li);
    });
  }
}

function removeMember(member) {
  state.team = state.team.filter((entry) => entry !== member);
  state.chores = state.chores.filter((chore) => chore.assignee !== member);
  persist();
  renderTeam();
  refreshChores();
}

function refreshChores() {
  choreList.innerHTML = "";

  state.chores
    .sort((a, b) => `${a.date}${a.start}`.localeCompare(`${b.date}${b.start}`))
    .forEach((item) => {
      const li = document.createElement("li");
      const content = document.createElement("div");
      content.innerHTML = `<strong>${item.title}</strong><div class="meta">${item.assignee} • ${item.date} ${item.start}-${item.end} • ${readableRepeat(item.repeat)}</div>`;
      li.append(content, button("Remove", "remove", () => removeChore(item.id)));
      choreList.append(li);
    });

  calendar.removeAllEvents();
  choresToEvents(state.chores).forEach((event) => calendar.addEvent(event));
}

function removeChore(id) {
  state.chores = state.chores.filter((item) => item.id !== id);
  persist();
  refreshChores();
}

function choresToEvents(chores) {
  return chores.map((item) => {
    const title = `${item.title} (${item.assignee})`;
    const dtStart = `${item.date}T${item.start}:00`;
    const dtEnd = `${item.date}T${item.end}:00`;

    if (item.repeat === "none") {
      return {
        id: item.id,
        title,
        start: dtStart,
        end: dtEnd,
      };
    }

    const rrule = {
      dtstart: dtStart,
      freq: repeatToFrequency(item.repeat),
    };

    if (item.repeat === "weekdays") {
      rrule.byweekday = ["mo", "tu", "we", "th", "fr"];
      rrule.freq = "weekly";
    }

    return {
      id: item.id,
      title,
      rrule,
      duration: durationFrom(item.start, item.end),
    };
  });
}

function repeatToFrequency(repeat) {
  if (repeat === "daily") return "daily";
  if (repeat === "weekly") return "weekly";
  return "monthly";
}

function durationFrom(start, end) {
  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);
  const totalMinutes = eh * 60 + em - (sh * 60 + sm);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
}

function readableRepeat(repeat) {
  if (repeat === "none") return "One-time";
  if (repeat === "weekdays") return "Weekdays";
  return repeat[0].toUpperCase() + repeat.slice(1);
}

function button(text, className, onClick) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = className;
  element.textContent = text;
  element.addEventListener("click", onClick);
  return element;
}

function load(key, fallback) {
  const raw = localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function persist() {
  localStorage.setItem(TEAM_KEY, JSON.stringify(state.team));
  localStorage.setItem(CHORE_KEY, JSON.stringify(state.chores));
}

function today() {
  return new Date().toISOString().slice(0, 10);
}
