function groupName(path) {
  if (path.startsWith("/API/1.1/")) return "API 1.1";
  const first = path.split("/").filter(Boolean)[0];
  return first ? first.toUpperCase() : "Otros";
}

function endpointItem(method, path) {
  const upperMethod = method.toUpperCase();
  return (
    '<li class="list-group-item d-flex justify-content-between align-items-center">' +
    '<a href="' + path + '">' + upperMethod + " " + path + "</a>" +
    '<span class="badge text-bg-light border">' + upperMethod + "</span>" +
    "</li>"
  );
}

async function loadOpenApiIndex() {
  const statusEl = document.getElementById("openapi-status");
  const sectionsEl = document.getElementById("openapi-sections");
  try {
    const response = await fetch("/openapi.json", { cache: "no-store" });
    if (!response.ok) throw new Error("No se pudo cargar /openapi.json");
    const schema = await response.json();
    const groups = {};
    const paths = schema.paths || {};

    Object.keys(paths).sort().forEach((path) => {
      const methods = paths[path] || {};
      Object.keys(methods).forEach((method) => {
        const name = groupName(path);
        if (!groups[name]) groups[name] = [];
        groups[name].push({ method: method, path: path });
      });
    });

    const groupNames = Object.keys(groups).sort();
    if (groupNames.length === 0) {
      statusEl.textContent = "No hay endpoints en OpenAPI.";
      return;
    }

    statusEl.textContent = "Endpoints cargados desde OpenAPI.";
    sectionsEl.innerHTML = groupNames.map((name) => {
      const items = groups[name]
        .sort((a, b) => (a.path + a.method).localeCompare(b.path + b.method))
        .map((ep) => endpointItem(ep.method, ep.path))
        .join("");
      return (
        '<section class="col-12 col-lg-6">' +
        '<div class="card h-100 shadow-sm"><div class="card-body">' +
        '<h2 class="h5 card-title">' + name + "</h2>" +
        '<ul class="list-group list-group-flush">' + items + "</ul>" +
        "</div></div></section>"
      );
    }).join("");
  } catch (error) {
    statusEl.textContent = "Error cargando OpenAPI: " + error.message;
    statusEl.classList.remove("text-secondary");
    statusEl.classList.add("text-danger");
  }
}

loadOpenApiIndex();
