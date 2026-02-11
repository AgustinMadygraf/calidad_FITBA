import {
  CATEGORIA_FISCAL_COLUMNS,
  CLIENTE_COLUMNS,
  IDENTIFICACION_TRIBUTARIA_COLUMNS,
  ITEM_COLUMNS,
  PRODUCTO_NESTED_ITEM_COLUMNS,
  PRODUCTO_COLUMNS,
  REMITO_COLUMNS,
  UI_MESSAGES
} from "../config.js";
import { fetchClienteById } from "../services/clienteService.js";
import { fetchProductoById } from "../services/productoService.js";
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
  setProductoError,
  setProductoLoading,
  setProductoNotFound,
  setProductoReady,
  setRemitos,
  showClienteAsMainTable,
  showProductoAsMainTable,
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
  renderProductoNestedSection,
  renderProductoSection,
  renderRemitoTable,
  renderShowAllButton
} from "../ui/renderers.js";

let domRefs = null;

function createRequestTracker() {
  let currentRequest = 0;
  return {
    next() {
      currentRequest += 1;
      return currentRequest;
    },
    invalidate() {
      currentRequest += 1;
    },
    isCurrent(requestId) {
      return requestId === currentRequest;
    }
  };
}

const requestTrackers = {
  cliente: createRequestTracker(),
  producto: createRequestTracker()
};

function hideProductoNestedSections() {
  hideDetailSection(
    domRefs.productoUnidadMedidaSection,
    domRefs.productoUnidadMedidaTableBody
  );
  hideDetailSection(domRefs.productoTasaIvaSection, domRefs.productoTasaIvaTableBody);
  hideDetailSection(
    domRefs.productoCuentaContableSection,
    domRefs.productoCuentaContableTableBody
  );
}

function hideClienteNestedSections() {
  hideDetailSection(
    domRefs.identificacionTributariaSection,
    domRefs.identificacionTributariaTableBody
  );
  hideDetailSection(domRefs.categoriaFiscalSection, domRefs.categoriaFiscalTableBody);
}

function renderClienteMainMode(state) {
  domRefs.remitoTableWrapper.classList.add("d-none");
  hideDetailSection(domRefs.productoMainTableWrapper, domRefs.productoMainTableBody);
  hideProductoNestedSections();
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
    return;
  }

  hideClienteNestedSections();
}

function renderProductoMainMode(state) {
  domRefs.remitoTableWrapper.classList.add("d-none");
  hideDetailSection(domRefs.clienteMainTableWrapper, domRefs.clienteMainTableBody);
  renderProductoSection(
    domRefs.productoMainTableWrapper,
    domRefs.mainTitle,
    domRefs.productoMainTableBody,
    state.productoDetail,
    PRODUCTO_COLUMNS,
    UI_MESSAGES
  );
  hideDetailSection(domRefs.itemSection, domRefs.itemTableBody);
  hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
  hideClienteNestedSections();

  if (state.productoDetail.status !== "idle") {
    renderProductoNestedSection(
      domRefs.productoUnidadMedidaSection,
      domRefs.productoUnidadMedidaTitle,
      domRefs.productoUnidadMedidaTableBody,
      state.productoDetail,
      PRODUCTO_NESTED_ITEM_COLUMNS,
      UI_MESSAGES,
      {
        fieldKey: "unidadMedida",
        label: "unidadMedida",
        notFoundMessageKey: "productoUnidadMedidaNotFound"
      }
    );
    renderProductoNestedSection(
      domRefs.productoTasaIvaSection,
      domRefs.productoTasaIvaTitle,
      domRefs.productoTasaIvaTableBody,
      state.productoDetail,
      PRODUCTO_NESTED_ITEM_COLUMNS,
      UI_MESSAGES,
      {
        fieldKey: "tasaIva",
        label: "tasaIva",
        notFoundMessageKey: "productoTasaIvaNotFound"
      }
    );
    renderProductoNestedSection(
      domRefs.productoCuentaContableSection,
      domRefs.productoCuentaContableTitle,
      domRefs.productoCuentaContableTableBody,
      state.productoDetail,
      PRODUCTO_NESTED_ITEM_COLUMNS,
      UI_MESSAGES,
      {
        fieldKey: "cuentaContable",
        label: "cuentaContable",
        notFoundMessageKey: "productoCuentaContableNotFound"
      }
    );
    return;
  }

  hideProductoNestedSections();
}

function renderRemitoMainMode(state, visibleRemitos, selectedRemito) {
  domRefs.mainTitle.textContent = "Remito de Venta";
  domRefs.remitoTableWrapper.classList.remove("d-none");
  hideDetailSection(domRefs.clienteMainTableWrapper, domRefs.clienteMainTableBody);
  hideDetailSection(domRefs.productoMainTableWrapper, domRefs.productoMainTableBody);
  hideProductoNestedSections();

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
    return;
  }

  hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
  hideClienteNestedSections();
}

const MAIN_TABLE_RENDERERS = {
  cliente: (state) => renderClienteMainMode(state),
  producto: (state) => renderProductoMainMode(state),
  remito: (state, context) =>
    renderRemitoMainMode(state, context.visibleRemitos, context.selectedRemito)
};

function renderView() {
  const state = getState();
  const visibleRemitos = getVisibleRemitos();
  const selectedRemito = getSelectedRemito();

  renderBanner(domRefs.banner, state.banner);
  renderShowAllButton(
    domRefs.showAllButton,
    state.selectedTransaccionId !== null ||
      state.mainTable === "cliente" ||
      state.mainTable === "producto"
  );

  const renderer = MAIN_TABLE_RENDERERS[state.mainTable] || MAIN_TABLE_RENDERERS.remito;
  renderer(state, { visibleRemitos, selectedRemito });
}

async function loadDetailEntity({
  entityId,
  requestTracker,
  setLoading,
  fetchById,
  setNotFound,
  setReady,
  setError,
  notFoundMessage,
  loadErrorMessage
}) {
  if (entityId === null || entityId === undefined || String(entityId).trim() === "") {
    setError(null, notFoundMessage);
    renderView();
    return;
  }

  const requestId = requestTracker.next();
  setLoading(entityId);
  renderView();

  try {
    const entity = await fetchById(entityId);
    if (!requestTracker.isCurrent(requestId)) {
      return;
    }

    if (entity === null) {
      setNotFound(entityId);
    } else {
      setReady(entityId, entity);
    }
  } catch (error) {
    if (!requestTracker.isCurrent(requestId)) {
      return;
    }
    setError(entityId, loadErrorMessage);
  }

  renderView();
}

function handleTransaccionClick(transaccionId) {
  requestTrackers.cliente.invalidate();
  requestTrackers.producto.invalidate();
  showRemitoAsMainTable();
  selectTransaccion(transaccionId);
  renderView();
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

  await loadDetailEntity({
    entityId: clienteId,
    requestTracker: requestTrackers.cliente,
    setLoading: setClienteLoading,
    fetchById: fetchClienteById,
    setNotFound: setClienteNotFound,
    setReady: setClienteReady,
    setError: setClienteError,
    notFoundMessage: UI_MESSAGES.clienteNotFound,
    loadErrorMessage: UI_MESSAGES.clienteLoadError
  });
}

async function handleProductoClick(productoId) {
  showProductoAsMainTable();
  await loadDetailEntity({
    entityId: productoId,
    requestTracker: requestTrackers.producto,
    setLoading: setProductoLoading,
    fetchById: fetchProductoById,
    setNotFound: setProductoNotFound,
    setReady: setProductoReady,
    setError: setProductoError,
    notFoundMessage: UI_MESSAGES.productoNotFound,
    loadErrorMessage: UI_MESSAGES.productoLoadError
  });
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
    if (!clienteLink) {
      return;
    }

    event.preventDefault();
    void handleClienteClick(
      clienteLink.dataset.transaccionId,
      clienteLink.dataset.clienteId,
      { clienteAsMainTable: true }
    );
  });

  domRefs.itemTableBody.addEventListener("click", (event) => {
    const productoLink = event.target.closest(".js-producto-link");
    if (!productoLink) {
      return;
    }
    event.preventDefault();
    void handleProductoClick(productoLink.dataset.productoId);
  });

  domRefs.showAllButton.addEventListener("click", () => {
    requestTrackers.cliente.invalidate();
    requestTrackers.producto.invalidate();
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
