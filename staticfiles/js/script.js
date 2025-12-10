// Simple login validation
function loginUser(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (username === "student" && password === "1234") {
    window.location.href = "index.html";
  } else {
    alert("Invalid credentials! Try student/1234");
  }
}