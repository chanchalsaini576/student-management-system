document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form.confirm-delete").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!confirm("Are you sure you want to delete this record?")) {
        e.preventDefault();
      }
    });
  });
});
