const TIMEZONES = {
  "PST": "Pacific Time",
  "AMT": "Arizona Time",
  "MST": "Mountain Time",
  "CST": "Central Time",
  "EST": "Eastern Time",
  "AST": "Atlantic Time"
};
const data = {};

function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function getValue(obj, key) {
  let defaultValue = null;
  if (arguments.length == 3) {
    defaultValue = arguments[2];
  }
  if (obj && Object.prototype.hasOwnProperty.call(obj, key)) {
    return obj[key];
  }
  else {
    return defaultValue;
  }
}

function showAlert() {
  let alertElem = $("#config-saved");
  if (alertElem.classList.contains("hide")) {
    alertElem.remove("hide");
    alertElem.add("show");
  }
}

function hideAlert() {
  let alertElem = $("#config-saved");
  if (alertElem.classList.contains("show")) {
    alertElem.remove("show");
    alertElem.add("hide");
  }
}

function updateUI() {
  // Door
  if (getValue(data, "door")) {
    $("span.door-status").innerHTML = data["door"]["status"];
    if (data["door"]["status"] === "Closed") {
      $("span.invert-action").innerHTML = "Open";
    }
    else {
      $("span.invert-action").innerHTML = "Close";
    }
  }
  // Network
  if (getValue(data, "network")) {
    let ip_address = getValue(data["network"], "ip_address", "(unknown)");
    let essid = getValue(data["network"], "essid", "");
    let password = getValue(data["network"], "password", "");
    let can_start_ap = getValue(data["network"], "can_start_ap", true);
    $("span.ip-address").innerHTML = data["network"]["ip_address"];
    $("#essid").value = essid;
    $("#password").value = password;
    $("#can-start-ap").checked = can_start_ap;
  }
  // Location
  if (getValue(data, "location")) {
    let latitude = getValue(data["location"], "latitude", "");
    let longitude = getValue(data["location"], "longitude", "");
    let timezone = getValue(data["location"], "timezone");
    if (timezone) {
      timezoneName = getValue(TIMEZONES, data["location"]["timezone"], "(not found)");
    }
    else {
      timezoneName = "(not set)";
    }
    $("#latitude").value = latitude;
    $("#longitude").value = longitude;
    $("#timezone").value = timezone;
    $("span.timezone").innerHTML = timezoneName;
  }
}

function loadData() {
  fetch("/location")
    .then(function (response) {
      return response.json();
    })
    .then(function (responseData) {
      data["location"] = responseData;
      console.log(responseData);
      updateUI();
    });
  fetch("/network")
    .then(function (response) {
      return response.json();
    })
    .then(function (responseData) {
      data["network"] = responseData;
      console.log(responseData);
      updateUI();
    });
  fetch("/door")
    .then(function (response) {
      return response.json();
    })
    .then(function (responseData) {
      data["door"] = responseData;
      console.log(responseData);
      updateUI();
    });
}

function saveLocation() {
    var params = {
        timezone: $("#timezone").value,
        latitude: $("#latitude").value,
        longitude: $("#longitude").value
    }
    fetch("/location", {method: "POST", body: JSON.stringify(params)})
      .then(function (response) { return response.json(); })
      .then(function (responseData) {
        data['location'] = responseData;
        updateUI();
        showAlert();
        setTimeout(hideAlert, 5000);
      });
}

function saveNetwork() {
    var params = {
        essid: $("#essid").value,
        password: $("#password").value,
        can_start_ap: $("#can-start-ap").checked
    }
    fetch("/network", {method: "POST", body: JSON.stringify(params)})
      .then(function (response) { return response.json(); })
      .then(function (responseData) {
        data["network"] = responseData;
        updateUI();
        showAlert();
        setTimeout(hideAlert, 5000);
      });
}

function performDoorAction() {
}

function setUpForms() {
    // The location form
    $("#save-location").addEventListener("click", saveLocation);
    $("#save-network").addEventListener("click", saveNetwork);
}

function setUpUI() {
  // Set up the navigation clicks on menu items and buttons
  $$("a[href^='#']").forEach(function (elem) {
    elem.addEventListener("click", function (event) {
      let elemId = event.target.hash;
      //["#getting-started", "#dashboard", "#network", "#door", "#location"].forEach(function (item) {
      ["#dashboard", "#network", "#door", "#location"].forEach(function (item) {
        console.log(item);
        console.log(elemId);
        if (elemId == item) {
          $("nav > a.link[href='" + item + "']").classList.add("active");
          $(item).style.display = "block";
        }
        else {
          $("nav > a.link[href='" + item + "']").classList.remove("active");
          $(item).style.display = "none";
        }
        event.preventDefault();
      });
    });
  });
  // Set up password view toggling
  $("#toggle-password").addEventListener("click", function (event) {
    let passwordInput = $("input#password");
    let button = event.target;
    if (passwordInput.type == "password") {
      passwordInput.type = "text";
      button.innerHTML = "Hide password";
    }
    else {
      passwordInput.type = "password";
      button.innerHTML = "Show password";
    }
  });
  $("#get-location").addEventListener("click", function (event) {
    if ("geolocation" in navigator) {
      let latInput = $("#latitude");
      let longInput = $("#longitude");
      navigator.geolocation.getCurrentPosition((position) => {
        latInput.value = position.coords.latitude;
        longInput.value = position.coords.longitude;
      });
    }
    else {
      console.log("No Geolocation API available");
      console.log(navigator);
    }
    let now = new Date().toTimeString();
    const timeZoneName = now.replace(/.*[(](.*)[)].*/,'$1');
    // const officialName = Intl.
    console.log(timeZone);
    event.preventDefault();
  });
}

document.addEventListener('readystatechange', event => {
  if (event.target.readyState === 'complete') {
    setUpUI();
    setUpForms();
    loadData();
  }
});
