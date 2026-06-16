const API_BASE = "http://127.0.0.1:8000/api";

const uploadButton = document.getElementById("uploadButton");
const fileInput = document.getElementById("fileInput");
const filesTableBody = document.getElementById("filesTableBody");
const statusElement = document.getElementById("status");
const searchInput = document.getElementById("searchInput");

let allFiles = [];

uploadButton.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files?.[0];
  if (!file) return;

  await uploadFile(file);
  fileInput.value = "";
});

searchInput.addEventListener("input", () => {
  const searchTerm = searchInput.value.toLowerCase();
  if (!searchTerm) {
    renderFiles(allFiles);
    return;
  }
  const filteredFiles = allFiles.filter((file) =>
    file.name.toLowerCase().includes(searchTerm)
  );
  renderFiles(filteredFiles);
});

async function uploadFile(file) {
  setStatus(`Subiendo ${file.name}...`, "");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error al subir archivo");
    }

    const data = await response.json();
    setStatus(`Archivo subido: ${data.filename}` , "success");
    await loadFiles();
  } catch (error) {
    setStatus(error.message || "Error al subir archivo", "error");
  }
}

function setStatus(message, type) {
  statusElement.textContent = message;
  statusElement.className = "status";
  if (type) {
    statusElement.classList.add(type);
  }
}

async function loadFiles() {
  filesTableBody.innerHTML = `
    <tr>
      <td colspan="3">Cargando archivos...</td>
    </tr>
  `;

  try {
    const response = await fetch(`${API_BASE}/files`);
    if (!response.ok) {
      throw new Error("No se pudieron cargar los archivos");
    }

    const data = await response.json();
    const archivos = Array.isArray(data.archivos) ? data.archivos : [];
    renderFiles(archivos);
  } catch (error) {
    filesTableBody.innerHTML = `
      <tr>
        <td colspan="3">Error cargando archivos.</td>
      </tr>
    `;
    setStatus(error.message || "Error al cargar archivos", "error");
  }
}

function renderFiles(archivos) {
  if (!archivos.length) {
    filesTableBody.innerHTML = `
      <tr>
        <td colspan="3">No hay archivos disponibles.</td>
      </tr>
    `;
    return;
  }

  allFiles = archivos;

  filesTableBody.innerHTML = archivos.map((archivo) => {
    const sizeLabel = formatBytes(archivo.size || 0);
    return `
      <tr>
        <td>${archivo.name}</td>
        <td>${sizeLabel}</td>
        <td class="actions-cell">
          <button type="button" data-url="${archivo.url_aws}" class="download-btn">Descargar</button>
          <button type="button" data-name="${archivo.name}" class="delete-btn">Eliminar</button>
        </td>
      </tr>
    `;
  }).join("");

  filesTableBody.querySelectorAll(".download-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const url = button.dataset.url;
      if (url) {
        window.open(url, "_blank");
      }
    });
  });

  filesTableBody.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const name = button.dataset.name;
      if (!name) return;
      const confirmDelete = window.confirm(`Eliminar archivo ${name}?`);
      if (!confirmDelete) return;
      await deleteFile(name);
    });
  });
}

async function deleteFile(name) {
  setStatus(`Eliminando ${name}...`, "");

  try {
    const response = await fetch(`${API_BASE}/files/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error al eliminar archivo");
    }

    const data = await response.json();
    setStatus(data.mensaje || `Archivo ${name} eliminado`, "success");
    await loadFiles();
  } catch (error) {
    setStatus(error.message || "Error al eliminar archivo", "error");
  }
}

function formatBytes(bytes) {
  if (typeof bytes !== "number") return "0 B";
  if (bytes === 0) return "0 B";
  const unidades = ["B", "KB", "MB", "GB", "TB"];
  const indice = Math.floor(Math.log(bytes) / Math.log(1024));
  const valor = bytes / Math.pow(1024, indice);
  return `${valor.toFixed(1)} ${unidades[indice]}`;
}

loadFiles();
