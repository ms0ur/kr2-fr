document.querySelectorAll("[data-toggle]").forEach(function (button) {
  const details = document.getElementById(button.dataset.toggle);
  details.hidden = true;
  button.hidden = false;
  button.addEventListener("click", function () {
    details.hidden = !details.hidden;
    button.setAttribute("aria-expanded", String(!details.hidden));
    button.textContent = details.hidden ? "Подробнее о катке" : "Скрыть сведения";
  });
});
