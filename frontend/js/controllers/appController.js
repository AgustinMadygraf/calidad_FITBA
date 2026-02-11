import {
  CLIENTE_COLUMNS,
  ITEM_COLUMNS,
  REMITO_COLUMNS,
  UI_MESSAGES
} from "../config.js";
import { fetchClienteById } from "../services/clienteService.js";
import { fetchRemitos, getFallbackRemitos } from "../services/remitoService.js";
import {
  clearBanner,
  clearSelection,
  getSelectedRemito,
  getState,
  getVisibleRemitos,
  selectTransaccion,
  setBanner,
  setClienteError,
  setClienteLoading,
  setClienteNotFound,
  setClienteReady,
  setRemitos
} from "../state/store.js";
import { getDomRefs } from "../ui/dom.js";
import {
  hideDetailSection,
  renderBanner,
  renderClienteSection,
  renderItemSection,
  renderRemitoTable,
  renderShowAllButton
} from "../ui/renderers.js";

let domRefs = null;
let clienteRequestToken = 0;

function renderView() {
  const state = getState();
  const visibleRemitos = getVisibleRemitos();
  const selectedRemito = getSelectedRemito();

  renderBanner(domRefs.banner, state.banner);
  renderShowAllButton(domRefs.showAllButton, state.selectedTransaccionId !== null);
  renderRemitoTable(
    domRefs.remitoTableBody,
    visibleRemitos,
    REMITO_COLUMNS,
    UI_MESSAGES.noRemitos
  );

  if (selectedRemito) {
    renderItemSection(
      domRefs.itemSection,
      domRefs.itemTitle,
      domRefs.itemTableBody,
      selectedRemito,
      ITEM_COLUMNS,
      UI_MESSAGES.noItems
    );
  } else {
    hideDetailSection(domRefs.itemSection, domRefs.itemTableBody);
  }

  if (selectedRemito && state.clienteDetail.status !== "idle") {
    renderClienteSection(
      domRefs.clienteSection,
      domRefs.clienteTitle,
      domRefs.clienteTableBody,
      state.clienteDetail,
      CLIENTE_COLUMNS,
      UI_MESSAGES
    );
  } else {
    hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
  }
}

function handleTransaccionClick(transaccionId) {
  clienteRequestToken += 1;
  selectTransaccion(transaccionId);
  renderView();
}

async function handleClienteClick(transaccionId, clienteId) {
  const hasTransaccion = transaccionId !== null && transaccionId !== undefined;
  if (hasTransaccion) {
    selectTransaccion(transaccionId);
  } else {
    clearSelection();
  }

  if (clienteId === null || clienteId === undefined || String(clienteId).trim() === "") {
    setClienteError(null, UI_MESSAGES.clienteNotFound);
    renderView();
    return;
  }

  const requestToken = ++clienteRequestToken;
  setClienteLoading(clienteId);
  renderView();

  try {
    const cliente = await fetchClienteById(clienteId);
    if (requestToken !== clienteRequestToken) {
      return;
    }

    if (cliente === null) {
      setClienteNotFound(clienteId);
    } else {
      setClienteReady(clienteId, cliente);
    }
  } catch (error) {
    if (requestToken !== clienteRequestToken) {
      return;
    }
    setClienteError(clienteId, UI_MESSAGES.clienteLoadError);
  }

  renderView();
}

function bindEvents() {
  domRefs.remitoTableBody.addEventListener("click", (event) => {
    const transaccionLink = event.target.closest(".js-transaccion-link");
    if (transaccionLink) {
      event.preventDefault();
      handleTransaccionClick(transaccionLink.dataset.transaccionId);
      return;
    }

    const clienteLink = event.target.closest(".js-cliente-link");
    if (clienteLink) {
      event.preventDefault();
      void handleClienteClick(
        clienteLink.dataset.transaccionId,
        clienteLink.dataset.clienteId
      );
    }
  });

  domRefs.showAllButton.addEventListener("click", () => {
    clienteRequestToken += 1;
    clearSelection();
    renderView();
  });
}

async function loadRemitos() {
  try {
    const remitos = await fetchRemitos();
    setRemitos(remitos);
    clearBanner();
  } catch (error) {
    console.error("No se pudo cargar la lista de remitos:", error);
    setRemitos(getFallbackRemitos());
    setBanner(UI_MESSAGES.remitosLoadError, "warning");
  }
  renderView();
}

export async function initApp() {
  domRefs = getDomRefs();
  bindEvents();
  await loadRemitos();
}
