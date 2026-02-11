import {
  CATEGORIA_FISCAL_COLUMNS,
  CLIENTE_COLUMNS,
  IDENTIFICACION_TRIBUTARIA_COLUMNS,
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
  setRemitos,
  showClienteAsMainTable,
  showRemitoAsMainTable
} from "../state/store.js";
import { getDomRefs } from "../ui/dom.js";
import {
  hideDetailSection,
  renderBanner,
  renderCategoriaFiscalSection,
  renderClienteSection,
  renderIdentificacionTributariaSection,
  renderItemSection,
  renderRemitoTable,
  renderShowAllButton
} from "../ui/renderers.js";

let domRefs = null;
let clienteRequestToken = 0;

function renderView() {
  const state = getState();
  const isClienteMainTable = state.mainTable === "cliente";
  const visibleRemitos = getVisibleRemitos();
  const selectedRemito = getSelectedRemito();

  renderBanner(domRefs.banner, state.banner);
  renderShowAllButton(
    domRefs.showAllButton,
    state.selectedTransaccionId !== null || isClienteMainTable
  );

  if (isClienteMainTable) {
    domRefs.remitoTableWrapper.classList.add("d-none");
    renderClienteSection(
      domRefs.clienteMainTableWrapper,
      domRefs.mainTitle,
      domRefs.clienteMainTableBody,
      state.clienteDetail,
      CLIENTE_COLUMNS,
      UI_MESSAGES
    );
    hideDetailSection(domRefs.itemSection, domRefs.itemTableBody);
    hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
    if (state.clienteDetail.status !== "idle") {
      renderIdentificacionTributariaSection(
        domRefs.identificacionTributariaSection,
        domRefs.identificacionTributariaTitle,
        domRefs.identificacionTributariaTableBody,
        state.clienteDetail,
        IDENTIFICACION_TRIBUTARIA_COLUMNS,
        UI_MESSAGES
      );
      renderCategoriaFiscalSection(
        domRefs.categoriaFiscalSection,
        domRefs.categoriaFiscalTitle,
        domRefs.categoriaFiscalTableBody,
        state.clienteDetail,
        CATEGORIA_FISCAL_COLUMNS,
        UI_MESSAGES
      );
    } else {
      hideDetailSection(
        domRefs.identificacionTributariaSection,
        domRefs.identificacionTributariaTableBody
      );
      hideDetailSection(domRefs.categoriaFiscalSection, domRefs.categoriaFiscalTableBody);
    }
    return;
  }

  domRefs.mainTitle.textContent = "Remito de Venta";
  domRefs.remitoTableWrapper.classList.remove("d-none");
  hideDetailSection(domRefs.clienteMainTableWrapper, domRefs.clienteMainTableBody);
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
    renderIdentificacionTributariaSection(
      domRefs.identificacionTributariaSection,
      domRefs.identificacionTributariaTitle,
      domRefs.identificacionTributariaTableBody,
      state.clienteDetail,
      IDENTIFICACION_TRIBUTARIA_COLUMNS,
      UI_MESSAGES
    );
    renderCategoriaFiscalSection(
      domRefs.categoriaFiscalSection,
      domRefs.categoriaFiscalTitle,
      domRefs.categoriaFiscalTableBody,
      state.clienteDetail,
      CATEGORIA_FISCAL_COLUMNS,
      UI_MESSAGES
    );
  } else {
    hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
    hideDetailSection(
      domRefs.identificacionTributariaSection,
      domRefs.identificacionTributariaTableBody
    );
    hideDetailSection(domRefs.categoriaFiscalSection, domRefs.categoriaFiscalTableBody);
  }
}

async function handleClienteClick(
  transaccionId,
  clienteId,
  { clienteAsMainTable = false } = {}
) {
  const hasTransaccion = transaccionId !== null && transaccionId !== undefined;
  if (hasTransaccion) {
    selectTransaccion(transaccionId);
  } else {
    clearSelection();
  }
  if (clienteAsMainTable) {
    showClienteAsMainTable();
  } else {
    showRemitoAsMainTable();
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
      void handleClienteClick(
        transaccionLink.dataset.transaccionId,
        transaccionLink.dataset.clienteId,
        { clienteAsMainTable: false }
      );
      return;
    }

    const clienteLink = event.target.closest(".js-cliente-link");
    if (clienteLink) {
      event.preventDefault();
      void handleClienteClick(
        clienteLink.dataset.transaccionId,
        clienteLink.dataset.clienteId,
        { clienteAsMainTable: true }
      );
    }
  });

  domRefs.showAllButton.addEventListener("click", () => {
    clienteRequestToken += 1;
    showRemitoAsMainTable();
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
