import {
  CATEGORIA_FISCAL_COLUMNS,
  CLIENTE_COLUMNS,
  IDENTIFICACION_TRIBUTARIA_COLUMNS,
  ITEM_COLUMNS,
  LISTA_PRECIO_COLUMNS,
  PRODUCTO_NESTED_ITEM_COLUMNS,
  PRODUCTO_COLUMNS,
  REMITO_COLUMNS,
  UI_MESSAGES
} from "../config.js";
import { loadListaPrecios as loadListaPreciosUseCase } from "../application/listaPrecioUseCases.js";
import { loadRemitosWithFallback } from "../application/remitoUseCases.js";
import {
  readRouteFromUrl,
  writeRouteToUrl
} from "../router/queryState.js";
import { createRepositories } from "../repositories/index.js";
import {
  clearBanner,
  clearSelection,
  getSelectedRemito,
  getState,
  getVisibleRemitos,
  selectTransaccion,
  subscribe,
  setBanner,
  setClienteError,
  setClienteLoading,
  setClienteNotFound,
  setClienteReady,
  setListaPreciosError,
  setListaPreciosLoading,
  setListaPreciosReady,
  setProductoError,
  setProductoLoading,
  setProductoNotFound,
  setProductoReady,
  setRemitos,
  showClienteAsMainTable,
  showEmptyMainTable,
  showListaPrecioAsMainTable,
  showProductoAsMainTable,
  showRemitoAsMainTable
} from "../state/store.js";
import { getActiveModule, isRemitoFlow, MODES } from "../state/modeMachine.js";
import { getDomRefs } from "../ui/dom.js";
import {
  hideDetailSection,
  renderBanner,
  renderCategoriaFiscalSection,
  renderClienteSection,
  renderIdentificacionTributariaSection,
  renderItemSection,
  renderListaPrecioTable,
  renderProductoNestedSection,
  renderProductoSection,
  renderRemitoTable,
  renderShowAllButton
} from "../ui/renderers.js";

let domRefs = null;
let repositories = null;

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

async function applyRouteSelectionFromUrl() {
  const route = readRouteFromUrl();
  const currentState = getState();

  if (route.productoId !== null) {
    clearSelection();
    showProductoAsMainTable();
    await loadDetailEntity({
      entityId: route.productoId,
      requestTracker: requestTrackers.producto,
      setLoading: setProductoLoading,
      fetchById: repositories.producto.getById,
      setNotFound: setProductoNotFound,
      setReady: setProductoReady,
      setError: setProductoError,
      notFoundMessage: UI_MESSAGES.productoNotFound,
      loadErrorMessage: UI_MESSAGES.productoLoadError
    });
    return;
  }

  if (route.clienteId !== null) {
    clearSelection();
    showClienteAsMainTable();
    await loadDetailEntity({
      entityId: route.clienteId,
      requestTracker: requestTrackers.cliente,
      setLoading: setClienteLoading,
      fetchById: repositories.cliente.getById,
      setNotFound: setClienteNotFound,
      setReady: setClienteReady,
      setError: setClienteError,
      notFoundMessage: UI_MESSAGES.clienteNotFound,
      loadErrorMessage: UI_MESSAGES.clienteLoadError
    });
    return;
  }

  if (route.remitoVentaId !== null) {
    showRemitoAsMainTable();
    selectTransaccion(route.remitoVentaId);
    return;
  }

  if (currentState.mainTable === MODES.NONE) {
    clearSelection();
    return;
  }

  if (currentState.mainTable === MODES.LISTA_PRECIO) {
    renderView();
    return;
  }

  showRemitoAsMainTable();
  clearSelection();
}

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

function hideListaPrecioSection() {
  hideDetailSection(
    domRefs.listaPrecioTableWrapper,
    domRefs.listaPrecioTableBody
  );
}

function hideRemitoDetailSections() {
  hideDetailSection(domRefs.itemSection, domRefs.itemTableBody);
  hideDetailSection(domRefs.clienteSection, domRefs.clienteTableBody);
  hideClienteNestedSections();
  hideProductoNestedSections();
}

function renderEmptyState() {
  domRefs.mainTitle.textContent = "Selecciona un modulo";
  domRefs.emptyState.classList.remove("d-none");
  hideDetailSection(domRefs.remitoTableWrapper, domRefs.remitoTableBody);
  hideListaPrecioSection();
  hideDetailSection(domRefs.clienteMainTableWrapper, domRefs.clienteMainTableBody);
  hideDetailSection(domRefs.productoMainTableWrapper, domRefs.productoMainTableBody);
  hideRemitoDetailSections();
}

function renderListaPrecioMainMode(state) {
  domRefs.mainTitle.textContent = "Listado de precios";
  domRefs.emptyState.classList.add("d-none");
  hideDetailSection(domRefs.remitoTableWrapper, domRefs.remitoTableBody);
  hideDetailSection(domRefs.clienteMainTableWrapper, domRefs.clienteMainTableBody);
  hideDetailSection(domRefs.productoMainTableWrapper, domRefs.productoMainTableBody);
  hideRemitoDetailSections();

  domRefs.listaPrecioTableWrapper.classList.remove("d-none");
  renderListaPrecioTable(
    domRefs.listaPrecioTableBody,
    state.listaPrecios,
    LISTA_PRECIO_COLUMNS,
    UI_MESSAGES
  );
}

function renderClienteMainMode(state) {
  domRefs.emptyState.classList.add("d-none");
  hideListaPrecioSection();
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
  domRefs.emptyState.classList.add("d-none");
  hideListaPrecioSection();
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
  domRefs.emptyState.classList.add("d-none");
  hideListaPrecioSection();
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
  const activeModule = getActiveModule(state.mainTable);
  const hasActiveSelection =
    activeModule === MODES.REMITO &&
    (state.selectedTransaccionId !== null || isRemitoFlow(state.mainTable));

  renderBanner(domRefs.banner, state.banner);
  renderShowAllButton(domRefs.showAllButton, hasActiveSelection);
  domRefs.backButton.classList.toggle("d-none", !hasActiveSelection);
  domRefs.mainViewSelect.value =
    activeModule === MODES.NONE
      ? ""
      : activeModule === MODES.LISTA_PRECIO
        ? "listaPrecio"
        : "remito";

  if (activeModule === MODES.NONE) {
    renderEmptyState();
    return;
  }

  if (activeModule === MODES.LISTA_PRECIO) {
    renderListaPrecioMainMode(state);
    return;
  }

  const visibleRemitos = getVisibleRemitos();
  const selectedRemito = getSelectedRemito();
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
    return;
  }

  const requestId = requestTracker.next();
  setLoading(entityId);

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
}

function handleTransaccionClick(transaccionId) {
  requestTrackers.cliente.invalidate();
  requestTrackers.producto.invalidate();
  writeRouteToUrl({ remitoVentaId: transaccionId });
  showRemitoAsMainTable();
  selectTransaccion(transaccionId);
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
    writeRouteToUrl({ clienteId });
    showClienteAsMainTable();
  } else {
    writeRouteToUrl({ remitoVentaId: hasTransaccion ? transaccionId : null });
    showRemitoAsMainTable();
  }

  await loadDetailEntity({
    entityId: clienteId,
    requestTracker: requestTrackers.cliente,
    setLoading: setClienteLoading,
    fetchById: repositories.cliente.getById,
    setNotFound: setClienteNotFound,
    setReady: setClienteReady,
    setError: setClienteError,
    notFoundMessage: UI_MESSAGES.clienteNotFound,
    loadErrorMessage: UI_MESSAGES.clienteLoadError
  });
}

async function handleProductoClick(productoId) {
  writeRouteToUrl({ productoId });
  showProductoAsMainTable();
  await loadDetailEntity({
    entityId: productoId,
    requestTracker: requestTrackers.producto,
    setLoading: setProductoLoading,
    fetchById: repositories.producto.getById,
    setNotFound: setProductoNotFound,
    setReady: setProductoReady,
    setError: setProductoError,
    notFoundMessage: UI_MESSAGES.productoNotFound,
    loadErrorMessage: UI_MESSAGES.productoLoadError
  });
}

function bindEvents() {
  domRefs.mainViewSelect.addEventListener("change", (event) => {
    const selection = event.target.value;
    requestTrackers.cliente.invalidate();
    requestTrackers.producto.invalidate();
    writeRouteToUrl({});
    clearSelection();

    if (selection === "remito") {
      showRemitoAsMainTable();
      return;
    }

    if (selection === "listaPrecio") {
      showListaPrecioAsMainTable();
      void loadListaPreciosView();
      return;
    }

    showEmptyMainTable();
  });

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
    writeRouteToUrl({});
    showRemitoAsMainTable();
    clearSelection();
  });

  domRefs.backButton.addEventListener("click", () => {
    requestTrackers.cliente.invalidate();
    requestTrackers.producto.invalidate();

    if (window.history.length > 1) {
      window.history.back();
      return;
    }

    writeRouteToUrl({}, { mode: "replace" });
    showRemitoAsMainTable();
    clearSelection();
  });
}

function bindLocationEvents() {
  window.addEventListener("popstate", () => {
    requestTrackers.cliente.invalidate();
    requestTrackers.producto.invalidate();
    void applyRouteSelectionFromUrl();
  });
}

async function loadRemitos() {
  const { items, usedFallback, error } = await loadRemitosWithFallback(
    repositories.remito
  );
  setRemitos(items);
  if (usedFallback) {
    console.error("No se pudo cargar la lista de remitos:", error);
    setBanner(UI_MESSAGES.remitosLoadError, "warning");
  } else {
    clearBanner();
  }

  await applyRouteSelectionFromUrl();
}

async function loadListaPreciosView({ force = false } = {}) {
  const state = getState();
  if (!force && state.listaPrecios?.status === "ready") {
    renderView();
    return;
  }

  setListaPreciosLoading();

  try {
    const { items } = await loadListaPreciosUseCase(repositories.listaPrecio);
    setListaPreciosReady(items);
    clearBanner();
  } catch (error) {
    console.error("No se pudo cargar el listado de precios:", error);
    setListaPreciosError(UI_MESSAGES.listaPreciosLoadError);
    setBanner(UI_MESSAGES.listaPreciosLoadError, "warning");
  }
}

export async function initApp() {
  domRefs = getDomRefs();
  repositories = createRepositories();
  subscribe(renderView);
  renderView();
  bindEvents();
  bindLocationEvents();
  await loadRemitos();
}
